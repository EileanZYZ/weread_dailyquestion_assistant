import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
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
            "Models" : "填写你申请到的模型名称，具体请参考云服务的相关文档\n如果您申请了腾讯云，那么预设的hunyuan-lite在您于云端开通了混元大模型服务后应该可以直接用",
            "SetClient": "请优先选择腾讯云（tencent could）避免出现不可知的错误\n为了您的安全，请将SecretId和SecretKey保存在环境变量中，并在此填写相应的环境变量名"
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
            "InvalidCommand" : "非法指令",
            "EmptyValue" : "属性有空\n请确认填写完成所有字段"
        }
    }

    def __init__(self, root):
        self.root = root

    def raise_info(self,type:str="",keyword:str=None,parent=None) -> None:
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
        print("show_screenshot:",end="")
        # 创建一个新的 Toplevel 窗口
        screen_shot_window = tk.Toplevel(self.root)
        screen_shot_window.title("窗口截图成功")
        print("窗口截图成功")

        self.locate_window(screen_shot_window,self.root)

        # 将图片转换为 PhotoImage 对象
        photo = ImageTk.PhotoImage(screen_shot)

        # 创建一个标签来显示图片
        label = tk.Label(screen_shot_window, image=photo)
        label.image = photo  # 保持对 PhotoImage 的引用，防止被垃圾回收
        label.pack()

    def locate_window(self,window,parent):
        # 计算子窗口的位置，使其居中显示在父窗口上方
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # 计算位置
        x = parent_x + (parent_width) // 2
        y = parent_y + (parent_height) // 2

        window.geometry(f"+{x}+{y}")


    def raise_confirm(self, parent=None) -> bool:
        # 创建一个新的 Toplevel 窗口
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("确认操作")
        confirm_window.geometry("400x200")
        confirm_window.transient(self.root)  # 使对话框成为父窗口的子窗口

        # 确定窗口位置
        self.locate_window(confirm_window,self.root)

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