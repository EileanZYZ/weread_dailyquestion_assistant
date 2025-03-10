import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from PIL import Image, ImageTk

class Messager:
    # 消息列表
    info_list : dict = {
        "Messages" : {
            "Wechat" : "在微信程序目录下，定位到一个名称为版本号的文件夹中",
		    "WechatOcr" : "示例：\n C:\\Users\\Administrator\\AppData\\Roaming\\Tencent\\WeChat\\XPlugin\\Plugins\\WeChatOCR\\7079\\extracted\\WeChatOCR.exe",
		    "Saved" : "保存成功",
            "SelectWindow" : "点击按钮后，再左键点击需要截图的窗口，右键取消选取 \n 选取成功后，请不要对目标窗口进行移动和遮挡",
            "SelectRegion" : "点击按钮后，左键画出区域，松开左键完成选取，右键取消选取 \n 选取成功后，请不要对目标窗口进行移动和遮挡"
        },
        "Error" : {
            "PathNotFound" : "找不到微信/微信OCR程序目录 \n 可能是由于微信更新，请重新设置路径",
            "ClientNotFound" : "缺少可用的云端大模型服务 \n 可能是由于微信更新，请重新设置路径"
        }
    }

    def __init__(self, root):
        self.root = root
        self.message_list = {
            
        }

    def raise_info(self,type:str="",keyword:str="") -> None:
        if type in self.info_list:
            if keyword in self.info_list[type]:
                messagebox.showinfo(type, self.info_list[type][keyword])
            else:
                messagebox.showinfo(type, self.info_list[type])
        else:
            messagebox.showinfo("错误", "未知错误")


if __name__ == "__main__":
    root = tk.Tk()
    messager = Messager(root)
    print("Messages" in messager.info_list)