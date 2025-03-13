import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
from PIL import Image, ImageTk

class Messager:
    # 消息列表
    info_list : dict = {
        "Messages" : {
            # 系统消息
		    "ConfigSaved" : "保存成功",   # 配置保存：客户端、模型的新增与编辑
            "ConfigDeleted" : "删除成功",   # 配置删除：客户端、模型的删除
            "PathSaved" : "路径保存成功，请重启程序后再连接OCR",    # 路径保存：微信路径、微信OCR路径
            "BindingCleared" : "由于被绑定的客户端/模型被修改/删除，请重新绑定",
            "BindSuccess" : "绑定成功",
            "OcrStarted" : "OCR成功启动",

            # 提示消息
            "WechatInfo" : "在微信程序目录下，定位到一个名称为版本号的文件夹中",    # 微信路径提示
		    "WechatOcrInfo" : "示例\nC:\\Users\\Administrator\\AppData\\Roaming\\Tencent\\WeChat\\XPlugin\\Plugins\\WeChatOCR\\7079\\extracted\\WeChatOCR.exe", # 微信OCR路径提示
            "SelectWindowInfo" : "点击按钮后，再左键点击需要截图的窗口，右键取消选取\n选取成功后，请不要对目标窗口进行移动和遮挡",  # 选取窗口提示
            "SelectRegionInfo" : "点击按钮后，左键画出区域，松开左键完成选取，右键取消选取\n选取成功后，请不要对目标窗口进行移动和遮挡",    # 选取区域提示
            "AnswerQuestionInfo" : "如何开始：\n1、确认云服务、模型名及路径配置正确。\n2、来到“绑定”页面，点击“连接大模型”，然后进行识别区域的绑定。\n3、来到“答题”页面，点击“连接OCR”。\n4、以上步骤全部成功后，开始答题。\n按钮功能：\n[识别]：利用大模型提取OCR结果中的题目和选项，并自动复制到剪贴板\n[识别并答题]：直接向大模型发送识别结果并回答，如果识别效果较差则有可能失败\n[发送]在编辑OCR文本框中的内容后可点击，并将编辑后的文本再次发送给大模型进行回答\n[复制结果]：将大模型回答复制到剪贴板",   # 答题页面帮助信息
            "ClientsSettingInfo" : "目前只支持腾讯云的混元大模型。\n同时，为了保证密钥安全，推荐将SecretId和SecretKey保存在环境变量中，再在配置文件中填写对应的变量名。",  # 客户端配置帮助信息
            "ModelsSettingInfo" : "填写你申请到的模型名称，具体请参考云服务的相关文档。\n【注意】请务必确保填写的模型名与文档中的接口一直，否则无法连接。\n腾讯云服务有免费的hunyuan-lite，在您于云端开通了混元大模型服务后就可以直接使用。"   # 模型配置帮助信息
        },
        "Error" : {
            # 配置报错
            "WechatPathNotFound" : "找不到微信目录\n可能是由于微信更新，请重新设置路径",
            "WechatOcrPathNotFound" : "找不到WeChat.exe\n请设置正确的路径",
            "ModelNotFound" : "模型不存在",
            "ConfigNotFound" : "找不到配置文件\n请检查配置文件Wrda.json是在\\config\\目录下",
            # 运行报错
            "DidNotFindModel" : "缺少可用的模型\n请先在绑定中选择一个可用的模型",
            "DidNotFindClient" : "缺少可用的云端大模型服务\n请注册一个腾讯云账号并填写密钥",
            "CloudAuthorizeFailed" : "云服务认证失败\n请检查ID和密钥是否正确",
            "DidNotInitModel" : "大模型服务未初始化\n请前往“绑定界面”，完成客户端、模型和识别区域的绑定后再开始答题",
            "DidNotInitOCR" : "未初始化OCR\n请先点击“连接OCR”，启动识别服务",
            "DidNotInitScreenCatcher" : "没有选定识别区域\n请先前往“绑定”页面，选择识别区域",
            "BindFailed" : "绑定失败\n请确认客户端和模型各字段有效",
            # 调试报错
            "InvalidPath" : "非法路径",
            "InvalidKey" : "非法关键字",
            "ModelAlreadyExists" : "模型名已存在",
            "InvalidCommand" : "非法指令",
            "EmptyValue" : "属性有空\n请确认填写完成所有字段",
            "QuestionEmpty" : "问题为空"
        }
    }

    def __init__(self, root):
        self.root = root

    def raise_info(self,type:str="",keyword:str=None,parent:tk.Toplevel=None) -> None:
        # print("show info:",end="")
        if type == "Messages":
            if keyword in self.info_list[type]:
                messagebox.showinfo(keyword, self.info_list[type][keyword])
            else:
                messagebox.showerror("Error", "消息类型不存在")
        elif type == "Error":
            if keyword in self.info_list[type]:
                messagebox.showerror(keyword, self.info_list[type][keyword])
            else:
                messagebox.showerror("Error", "错误类型不存在")
        else:
            messagebox.showerror("Error", "未知错误")

        if parent:
            parent.focus_force() # 获取焦点
        

    def raise_picture(self,screen_shot):
        # print("show_screenshot:",end="")
        # 创建一个新的 Toplevel 窗口
        screen_shot_window = tk.Toplevel(self.root)
        screen_shot_window.title("窗口截图成功")
        # print("窗口截图成功")

        self.locate_window(screen_shot_window,self.root)

        # 将图片转换为 PhotoImage 对象
        photo = ImageTk.PhotoImage(screen_shot)

        # 创建一个标签来显示图片
        label = tk.Label(screen_shot_window, image=photo)
        label.image = photo  # 保持对 PhotoImage 的引用，防止被垃圾回收
        label.pack()

    def locate_window(self,window,parent,c_width:int=0,c_height:int=0):
        # 计算子窗口的位置，使其居中显示在父窗口上方
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # 计算位置
        x = parent_x + (parent_width - c_width) // 2
        y = parent_y + (parent_height - c_height) // 2

        window.geometry(f"+{x}+{y}")


    def raise_confirm(self, parent=None) -> bool:
        # 创建一个新的 Toplevel 窗口
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("确认操作")
        confirm_window.geometry("400x200")
        confirm_window.transient(self.root)  # 使对话框成为父窗口的子窗口

        # 确定窗口位置
        self.locate_window(confirm_window,self.root,c_width=400,c_height=200)

        # 创建标签
        label = tk.Label(confirm_window, text="确认执行此操作？", font=("Microsoft YaHei", 12))
        label.pack(pady=10)

        # 创建确认按钮
        confirm_button = tk.Button(confirm_window, text="确认", command=lambda: self._confirm(confirm_window, True))
        confirm_button.pack(side=tk.LEFT, padx=20)

        # 创建取消按钮
        cancel_button = tk.Button(confirm_window, text="取消", command=lambda: self._confirm(confirm_window, False))
        cancel_button.pack(side=tk.RIGHT, padx=20)

        # 用于存储用户的选择
        self.confirm_result = False

        # 进入消息循环，等待用户选择
        confirm_window.wait_window()

        parent.focus_force()

        return self.confirm_result

    def _confirm(self, window, result):
        self.confirm_result = result
        window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    messager = Messager(root)
    type = "Error"
    keyword = ""
    # print("Messages" in messager.info_list)
    # print(messager.info_list[type][keyword])
    # print(keyword in messager.info_list[type])