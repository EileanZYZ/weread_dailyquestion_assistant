import os
import json
import time
import re
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
from PIL import Image

from module import QueryLLM
from module import CatchScreen
from module.RaiseInfo import Messager


class Config():
    wechat_path : str = ""
    wechat_ocr_path : str = ""
    client : dict = {}
    models : list = []
    prompts : dict = {}
    matcher : str = ""
    regular : bool = False
    window_sreenshot = Image

    def __init__(self,root,config_name="Wrda"):        
        self.config_path = os.path.join(os.path.dirname(__file__),"config",config_name+".json")
        # 配置信使
        self.messager = Messager(root)

        if self.config_path :
            # 加载配置
            self.load_config(self.config_path)
            # 自检
            self.check_config()
        else:
            self.messager.raise_info("Error","ConfigNotFound")

    def load_config(self,config_path=""):
        with open(config_path,"r",encoding="utf-8") as f:
            config = json.load(f)
            self.wechat_path = config['App']['wechat_dir']
            self.wechat_ocr_path = config['App']['wechat_ocr_dir']
            self.client = config['Client']
            self.models = config['Models']
            self.prompts = config['Prompts']
            self.matcher = config['Filter']

    def check_config(self,callback:bool=False):
        # 检查微信路径
        if not os.path.exists(self.wechat_path):
            self.messager.raise_info("Error","PathNotFound")
        # 检查WeChatOcr路径
        if not os.path.exists(self.wechat_ocr_path):
            self.messager.raise_info("Error","WechatOcr")
        # 检查客户端
        if not self.client:
            self.messager.raise_info("Error","ClientNotFound")
        # 检查模型
        if not self.models:
            self.messager.raise_info("Error","ModelNotFound")
        elif callback:
            self.messager.raise_info("Messages","Checked")
    
    def save_config(self, key: str, value: list):
        """
        根据传入的key和value更新配置文件。

        参数:
        - key (str): 配置项的键。
        - value: 配置项的新值。
        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 更新配置项
        if key == "WeChat":
            new_path = value[0]
            if not os.path.exists(new_path) or not os.path.isdir(new_path):
                self.messager.raise_info("Error", "InvalidPath")
                return
            config['App']['wechat_dir'] = new_path
        elif key == "WeChatOCR":
            new_path = value[0]
            if not os.path.exists(new_path) or not os.path.isfile(new_path):
                self.messager.raise_info("Error", "InvalidPath")
                return
            config['App']['wechat_ocr_dir'] = new_path
        elif key == "Client":
            """
            客户端更新
            value = [*client name*, *secret id*, *secret key*]
            """
            if value[0] in self.client:  
                # 若为真则是编辑已有的client
                config['Client'][value[0]]['secret_id'] = value[1]   
                config['Client'][value[0]]['secret_key'] = value[2]  
            else:
                # 若为假则是添加新的client
                config['Client'][value[0]] = {
                    'secret_id': value[1],
                    'secret_key': value[2]
                }
        elif key == "Models":
            """
            模型更新
            value = [*command*, *old name*, *new name*]
            """
            command = value[0]
            if command == "add":    # 新增操作
                # 将value[2]的值追加进config
                if value[2] not in config['Models']:
                    config['Models'].append(value[2])
                else:
                    self.messager.raise_info("Error", "ModelAlreadyExists")
            elif command == "edit": # 修改操作
                # 获取value[1]在config中的索引，将其改为value[2]
                if value[1] in config['Models']:
                    index = config['Models'].index(value[1])
                    config['Models'][index] = value[2]
                else:
                    self.messager.raise_info("Error", "ModelNotFound")
            elif command == "delete":
                # 删除config中的value[1]
                if value[1] in config['Models']:
                    config['Models'].remove(value[1])
                else:
                    self.messager.raise_info("Error", "ModelNotFound")
            else:
                self.messager.raise_info("Error", "InvalidCommand")
        else:
            self.messager.raise_info("Error", "InvalidKey")
            return

        # 写回配置文件
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        # 更新内部属性
        self.load_config(self.config_path)

        # 提示保存成功
        self.messager.raise_info("Messages", "Saved")

        # 自检
        self.check_config(callback=False)


class WeReadDailyquestionAssistant(Config):
    ocr_result : str = ""

    def __init__(self,root):
        super().__init__(root) # 加载配置

        # 启动OCR
        self.init_ocr_manager()

        # 启动大模型
        self.init_llm()

    # OCR设置
    def init_ocr_manager(self):
        print("初始化ocr服务...",end="")
        self.ocr_manager = OcrManager(self.wechat_path)
        # 设置WeChatOcr目录
        self.ocr_manager.SetExePath(self.wechat_ocr_path)
        # 设置微信所在路径
        self.ocr_manager.SetUsrLibDir(self.wechat_path)
        # 设置ocr识别结果的回调函数
        self.ocr_manager.SetOcrResultCallback(self.ocr_callback)
        print("完成。")

        # 启动ocr服务
        
        self.ocr_manager.StartWeChatOCR()
        print("ocr服务启动")

    # OCR回调
    def ocr_callback(self,img_path:str,results:dict):
        final_result = ""

        # 提取文本
        for result in results['ocrResult']:
            final_result += result["text"] + "\n"
        
        # 提取有效文本并保存
        # wechat_ocr提供的方法并不支持文本返回，因此需要自己搞个缓存
        if self.regular:
            self.ocr_result = self.extract_valid_text(final_result)
        else:
            self.ocr_result = final_result
        
        if self.ocr_result:
            print("成功。识别结果:\n" + self.ocr_result)
        else:
            print("失败，未提取到有效信息。\n源数据：" + final_result)

    # 文本过滤
    def extract_valid_text(self,final_results: str) -> str:
        # 使用re.search查找匹配的位置
        match = re.search(self.matcher, final_results)
        
        if match:
            # 获取匹配结束的位置
            start_index = match.end()
            # 提取匹配位置之后的所有文本
            valid_text = final_results[start_index:].strip()
            return valid_text
        else:
            # 如果没有找到匹配的内容，返回空字符串或其他适当的值
            return ""

    # 大模型设置

    def init_llm(self):
        print("正在初始化大模型...",end="")
        # print("确认密钥 \n SecretId:" + os.getenv(self.client["tencent_cloud"]["secret_id"])
            #   + "\n SecretKey:" + os.getenv(self.client["tencent_cloud"]["secret_key"]))
        self.llm = QueryLLM.tencentLLM(os.getenv(self.client["tencent_cloud"]["secret_id"]), 
                                       os.getenv(self.client["tencent_cloud"]["secret_key"]))
        print("完成")
    
    # prompt生成
    def gen_params(self,model:str=None,prompt:str=None) -> dict:
        if model not in self.models:
            raise ValueError("没有找到对应的模型！")
        
        params = {
        "Model": model,
        "Messages": []
        }
        # 添加system Role
        if self.prompts["system_call"]:
            params["Messages"].append({"Role": "system","Content": self.prompts["system_call"]})
        # 添加user Role
        params["Messages"].append({"Role": "user","Content": prompt})
        # print(params)

        return params
    
    # 初始化窗口截图器并选择目标窗口
    def init_screen_catcher(self):
        print("初始化screen_catche...")
        self.screen_catcher = CatchScreen.ScreenCatcher()


    def answer_question(self, question: str = None) -> list:
        # 记录开始时间
        start_time = time.time()

        # 判断：是否为直接识别图片并询问大模型？
        if question is None:
            # 定义图片路径
            image_path = os.path.join("temp", "target.png")

            # 检查并删除同名文件
            print("检查临时文件...",end="")
            if os.path.exists(image_path):
                os.remove(image_path)
                print("临时文件已删除")
            else:
                print("临时文件不存在")

            # 窗口截图并保存到temp目录下
            screenshot = self.screen_catcher.screen_shot(window=self.screen_catcher.target_window)
            screenshot.save(image_path)

            # # 启动ocr服务
            # print("ocr服务启动")
            # self.ocr_manager.StartWeChatOCR()

            print("识别图片...")
            self.ocr_manager.DoOCRTask(image_path)
            while self.ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
                pass

            # # 结束ocr服务
            # print("ocr服务结束")
            # self.ocr_manager.KillWeChatOCR()

            # 再次删除图片文件
            print("检查临时文件...",end="")
            if os.path.exists(image_path):
                os.remove(image_path)
                print("临时文件已删除")
            else:
                print("临时文件不存在")
            question = self.ocr_result  # 保存问题
            self.ocr_result = ""  # 清空ocr结果缓存

        if question == "":
            print("问题保存失败")

        # 询问大模型
        print("正在询问大模型...")
        answer = self.llm.query(self.gen_params("hunyuan-lite", question))
        print("答案：\n" + answer)

        # 计算并打印总耗时
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"总耗时: {elapsed_time:.2f} 秒")

        return [question, answer]
    
if __name__ == "__main__":
    # image_path = "temp/target.png"
    # if os.path.exists(image_path):
    #             os.remove(image_path)
    # else:
    #     print("临时文件不存在")
    # self = Config()
    # print(os.getenv(self.client["tencent_cloud"]["secret_id"]))
    print("hello")
    root = tk.Tk()
    wrda = WeReadDailyquestionAssistant(root)
    client =list(wrda.client.keys())
    print(client[0])