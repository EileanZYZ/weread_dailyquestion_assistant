import os
import json
import time
import re
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from PIL import Image

from module import QueryLLM
from module import CatchScreen
from module.RaiseInfo import Messager


class Config():
    wechat_path : str = ""  # 微信路径
    wechat_ocr_path : str = ""  # wechat ocr路径
    clients : OrderedDict = OrderedDict()  # 客户端列表，存有密钥；使用OrderedDict来保持顺序
    system_call : dict = {} # 系统角色prompt
    matcher : str = ""  # 正则表达式

    def __init__(self,root,config_name="Wrda"):
        # 读取配置文件        
        self.config_path = os.path.join(os.path.dirname(__file__),"config",config_name+".json")
        # 配置信使
        self.messager = Messager(root)

        if self.config_path :
            # 加载配置
            self.load_config(self.config_path)
            # 自检
        else:
            self.messager.raise_info("Error","ConfigNotFound")

    def load_config(self,config_path=""):
        with open(config_path,"r",encoding="utf-8") as f:
            config = json.load(f)
            self.wechat_path = config['App']['wechat_dir']
            self.wechat_ocr_path = config['App']['wechat_ocr_dir']
            self.clients = OrderedDict(config['Clients'])  # 使用OrderedDict来保持顺序
            self.system_call = config['SystemCall']
            self.matcher = config['Filter']
    
    def save_config(self, key: str, value: list) -> bool:
        """
        根据传入的key和value更新配置文件。

        参数:
        - key (str): 配置项的键。
        - value: 配置项的新值。
            -key-       -value-
            WeChat      [*wechat_dir*]
            WeChatOCR   [*wechat_ocr_dir*]
            Clients     [*command*,*old name*, *new name*,  *secret id*, *secret key*]
            Models      [*command*, *client name*, *old name*, *new name*]

        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 更新配置项
        if key == "WeChat":
            new_path = value[0]
            if not os.path.exists(new_path) or not os.path.isdir(new_path):
                self.messager.raise_info("Error", "InvalidPath")    # 提示路径错误
                return False
            config['App']['wechat_dir'] = new_path

        elif key == "WeChatOCR":
            new_path = value[0]
            if not os.path.exists(new_path) or not os.path.isfile(new_path):
                self.messager.raise_info("Error", "InvalidPath")
                return False
            config['App']['wechat_ocr_dir'] = new_path

        elif key == "Clients":
            """
            客户端更新
            value = [*command*,*old name*, *new name*,  *secret id*, *secret key*]

            command list = ["add", "edit", "delete"]
            """
            if value[0] == "edit":  
                # 编辑已有的client
                if value[1] in config['Clients']:
                    # 修改客户端名称
                    config['Clients'][value[2]] = config['Clients'].pop(value[1])
                    # 更新secret_id和secret_key
                    config['Clients'][value[2]]['secret_id'] = value[3]   
                    config['Clients'][value[2]]['secret_key'] = value[4]  
            elif value[0] == "add":
                # 添加新的client
                config['Clients'][value[2]] = {
                    'secret_id': value[3],
                    'secret_key': value[4],
                    'Models' : []
                }
            elif value[0] == "delete":
                # 删除已有的client
                del config['Clients'][value[1]]

        elif key == "Models":
            """
            模型更新
            value = [*command*, *cient name*, *old name*, *new name*]

            command list = ["add", "delete", "rename"]
            """
            if value[0] == "add":    # 新增操作
                # 将value[3]的值追加进config
                if value[2] not in config['Clients'][value[1]]['Models']:
                    config['Clients'][value[1]]['Models'].append(value[3])
                else:
                    self.messager.raise_info("Error", "ModelAlreadyExists")
                    return False
            elif value[0] == "edit": # 修改操作
                # 获取value[2]在config中的索引，将其改为value[3]
                if value[2] in config['Clients'][value[1]]['Models']:
                    index = config['Clients'][value[1]]['Models'].index(value[2])
                    config['Clients'][value[1]]['Models'][index] = value[3]
                else:
                    self.messager.raise_info("Error", "ModelNotFound")
                    return False
            elif value[0] == "delete":
                # 删除config['Clients'][value[1]]['Models']中的value[2]
                if value[2] in config['Clients'][value[1]]['Models']:
                    config['Clients'][value[1]]['Models'].remove(value[2])
                else:
                    self.messager.raise_info("Error", "ModelNotFound")
                    return False
            else:
                self.messager.raise_info("Error", "InvalidCommand")
                return False
        else:
            self.messager.raise_info("Error", "InvalidKey")
            return False

        # 写回配置文件
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        # 更新内部属性
        self.load_config(self.config_path)

        return True


class WeReadDailyquestionAssistant(Config):
    ocr_result : str = ""   # ocr结果
    window_sreenshot = Image    # 窗口截图
    selected_model :str = ""    # 绑定的模型
    selected_client : dict = "" # 绑定的客户端
    regular : bool = False  # 是否使用正则过滤
    ocr_activated : bool = False    # 是否开启ocr
    llm_initialized : bool = False  # 是否初始化llm
    screen_catcher_initialized : bool = False   # 是否初始化截图器

    def __init__(self,root):
        super().__init__(root) # 加载配置

    def init_screen_catcher(self):
        """
        初始化窗口截图器
        """
        print("初始化screen_catche...")
        self.screen_catcher = CatchScreen.ScreenCatcher()
        self.screen_catcher_initialized = True


    def init_ocr_manager(self):
        """
        初始化ocr服务
        """
        state : bool = True
        # 检查微信路径
        if not os.path.exists(self.wechat_path):
            self.messager.raise_info("Error","PathNotFound")
            state = False
        # 检查WeChatOcr路径
        if not os.path.exists(self.wechat_ocr_path):
            self.messager.raise_info("Error","PathNotFound")
            state = False
        if state:
            # print("初始化ocr服务...",end="")
            self.ocr_manager = OcrManager(self.wechat_path)
            # 设置WeChatOcr目录
            self.ocr_manager.SetExePath(self.wechat_ocr_path)
            # 设置微信所在路径
            self.ocr_manager.SetUsrLibDir(self.wechat_path)
            # 设置ocr识别结果的回调函数
            self.ocr_manager.SetOcrResultCallback(self.ocr_callback)
            # print("完成。")

            # 启动ocr服务
            self.ocr_manager.StartWeChatOCR()

            self.ocr_activated = True
            # print("ocr服务启动")

    def ocr_callback(self,img_path:str,results:dict):
        """
        OCR回调方法
        img_path用不上，原本是给保存结果用的，删掉的话接口对不上
        """
        final_result = ""

        # 提取文本
        for result in results['ocrResult']:
            final_result += result["text"] + "\n"
        
        # 提取有效文本并保存
        # wechat_ocr提供的方法并不支持文本返回，因此需要自己搞个缓存
        if self.regular:# 是否正则化
            self.ocr_result = self.extract_valid_text(final_result)
        else:
            self.ocr_result = final_result
        
        # if self.ocr_result:
        #     print("成功。识别结果:\n" + self.ocr_result)
        # else:
        #     print("失败，未提取到有效信息。\n源数据：" + final_result)

    def extract_valid_text(self,final_results: str) -> str:
        """
        正则过滤有效文本
        实际效果并不好（也许是我菜），所以关掉了，采用使用大模型提取
        """
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

    def init_llm(self):
        """
        初始化大模型
        """
        # print("正在初始化大模型...",end="")
        # print("确认密钥 \n SecretId:" + os.getenv(self.client["tencent_cloud"]["secret_id"])
            #   + "\n SecretKey:" + os.getenv(self.client["tencent_cloud"]["secret_key"]))
        try:
            if self.selected_client:
                self.llm = QueryLLM.tencentLLM(
                    os.getenv(self.clients[self.selected_client]["secret_id"]), 
                    os.getenv(self.clients[self.selected_client]["secret_key"])
                )
                self.llm_initialized = True
                self.messager.raise_info("Messages","BindSuccess")
            else:
                self.messager.raise_info("Error","ClientNotFound")
        except Exception as e:
            # 弹出错误窗口
            self.messager.raise_info("Error", "MissModel")
            # 或者使用自定义的消息提示器
            # self.messager.raise_info("Error", f"大模型初始化失败: {str(e)}")
        # print("完成")
    
    def gen_params(self,prompt:str=None,misson:str="a") -> dict:
        """
        生成Params（根据腾讯混元大模型接口）
        目前只能保证腾讯云混元服务的格式是对的
        等我大模型学扎实了再来改改
        """
        if not self.selected_model:
            params = {
            "Model": self.selected_model,
            "Messages": []
            }
            # 添加system Role
            if self.system_call[misson]:
                params["Messages"].append({"Role": "system","Content": self.system_call[misson]})
            # 添加user Role
            params["Messages"].append({"Role": "user","Content": prompt})
            # print(params)
        else:
            self.messager.raise_info("Error","MissModel")
        return params
    
    def answer_question(self, question:str=None, mission:str="a") -> list:
        """
        大模型回答问题
        @params:
            - question : 问题文本，可为空
            - mission : 执行任务类型 
                - "a" : 回答question
                - "r" : 识别并提取question中的问题
        @return:
            - result : [question,answer]
        """
        # 记录开始时间
        start_time = time.time()
        mission_list : list = ["a","r"]

        # 检查：大模型是否已经初始化完成？截图区域已绑定？
        if (not self.llm_initialized) and (not self.selected_model) and (not self.screen_catcher_initialized):
            self.messager.raise_info("Error","DidNotInitService")

        # 判断：是否为直接识别图片并询问大模型？
        if question is None:
            # 定义图片路径
            image_path = os.path.join("temp", "target.png")
            # 检查temp文件夹
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            # 检查并删除同名文件
            """
            由于wechat_ocr源码是本地批处理文件，ocr_manager不支持直接传入图片对象进行识别
            因此需要将图片暂存在本地，识别完成之后再删除。
            """
            # print("检查临时文件...",end="")
            if os.path.exists(image_path):
                os.remove(image_path)
                # print("临时文件已删除")
            # else:
            #     print("临时文件不存在")

            # 窗口截图并保存到temp目录下
            screenshot = self.screen_catcher.screen_shot(window=self.screen_catcher.target_window)
            screenshot.save(image_path)

            # print("识别图片...")
            self.ocr_manager.DoOCRTask(image_path)
            while self.ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
                pass

            # 删除图片文件
            # print("检查临时文件...",end="")
            if os.path.exists(image_path):
                os.remove(image_path)
                # print("临时文件已删除")
            # else:
                # print("临时文件不存在")
            question = self.ocr_result  # 保存问题
            self.ocr_result = ""  # 清空ocr结果缓存

        if question == "":
            self.messager.raise_info("Error","QuestionEmpty")

        # 询问大模型
        # print("正在询问大模型...")
        if mission in mission_list:
            answer = self.llm.query(self.gen_params(prompt=question, misson=mission))
            # print("答案：\n" + answer)
        else:
            self.messager.raise_info("Error","InvalidCommand")

        # 计算并打印总耗时
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"总耗时: {elapsed_time:.2f} 秒")

        return [question, answer]
    
if __name__ == "__main__":
    print("Ciallo～(∠・ω< )⌒★")
    root = tk.Tk()
    wrda = WeReadDailyquestionAssistant(root)