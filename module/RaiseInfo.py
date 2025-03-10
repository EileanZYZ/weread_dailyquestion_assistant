import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from PIL import Image, ImageTk

class Messager:
    # 消息列表
    info_list : dict = {
        "Messages" : {
            # 消息
		    "Saved" : "保存成功",
            "Checked" : "自检完成",
            # 窗口提示
            "Wechat" : "在微信程序目录下，定位到一个名称为版本号的文件夹中",
		    "WechatOcr" : "示例\nC:\\Users\\Administrator\\AppData\\Roaming\\Tencent\\WeChat\\XPlugin\\Plugins\\WeChatOCR\\7079\\extracted\\WeChatOCR.exe",
            "SelectWindow" : "点击按钮后，再左键点击需要截图的窗口，右键取消选取\n选取成功后，请不要对目标窗口进行移动和遮挡",
            "SelectRegion" : "点击按钮后，左键画出区域，松开左键完成选取，右键取消选取\n选取成功后，请不要对目标窗口进行移动和遮挡",
            "AnswerQuestion" : "现在“绑定”页面选择截图识别的窗口/区域，再点击“答题”开始提问大模型\n如果识别结果大模型无法回答，可在人工编辑后点“发送”再次提问\n提问前，请确认所有设置均正确",
            "Clients" : "目前只能保证支持腾讯云的混元大模型",
            "Models" : "填写你申请到的模型名称，具体请参考云服务的相关文档"
        },
        "Error" : {
            "PathNotFound" : "找不到微信/微信OCR程序目录\n可能是由于微信更新，请重新设置路径",
            "ClientNotFound" : "缺少可用的云端大模型服务\n请注册一个腾讯云账号并填写密钥",
            "ModelNotFound" : "缺少可用的模型\n请先在设置中选择一个可用的模型",
            "ConfigNotFound" : "找不到配置文件\n请检查配置文件Wrda.json是在\\config\\目录下",
            "InvalidPath" : "非法路径",
            "InvalidKey" : "非法关键字",
            "ModelAlreadyExists" : "模型名已存在",
            "ModelNotFound" : "模型不存在",
            "InvalidCommand" : "非法指令"
        }
    }

    def __init__(self, root):
        self.root = root

    def raise_info(self,type:str="",keyword:str=None) -> None:
        # print("show info:",end="")
        if type in self.info_list:
            if keyword in self.info_list[type]:
                messagebox.showinfo(keyword, self.info_list[type][keyword])
            else:
                messagebox.showinfo("Error", "消息类型不存在")
        else:
            messagebox.showinfo("Error", "未知错误")

    def raise_picture(self,window):
        print("show_screenshot:",end="")
        # 创建一个新的 Toplevel 窗口
        top = tk.Toplevel(self.root)
        top.title("窗口截图成功")
        print("窗口截图成功")

        # 将图片转换为 PhotoImage 对象
        photo = ImageTk.PhotoImage(window)

        # 创建一个标签来显示图片
        label = tk.Label(top, image=photo)
        label.image = photo  # 保持对 PhotoImage 的引用，防止被垃圾回收
        label.pack()


if __name__ == "__main__":
    root = tk.Tk()
    messager = Messager(root)
    type = "Error"
    keyword = ""
    # print("Messages" in messager.info_list)
    # print(messager.info_list[type][keyword])
    # print(keyword in messager.info_list[type])