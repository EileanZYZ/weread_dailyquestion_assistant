import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from threading import Thread
from PIL import Image, ImageTk

import Wrda
from module import RaiseInfo

class WrdaGui:
    default_font :str = "Microsoft YaHei"

    def __init__(self, root):
        """
        初始化WeRead Daily Question Assistant的图形用户界面。
    
        参数:
        - root: Tkinter的主窗口对象，用于承载整个应用的界面。
    
        此方法负责设置主窗口的基本属性，初始化WeRead Daily Question Assistant的核心功能，
        并创建顶部工具栏及初始化页面。
        """
        self.root = root
        self.root.title("WeRead Daily Question Assistant")
        self.root.geometry("960x540")
        self.root.resizable(False, False)   # 禁止调整窗口大小
    
        # 初始化WeRead Daily Question Assistant
        self.wrda = Wrda.WeReadDailyquestionAssistant(self.root)
        # 创建消息提示器
        self.messager = RaiseInfo.Messager(self.root)
    
        # 创建顶部工具栏
        self.create_toolbar()
    
        # 初始化页面
        self.current_frame = None
        self.current_page = None  # 添加属性来跟踪当前选中的按钮
        self.show_frame("答题")

    def create_toolbar(self):
        """
        创建工具栏。

        本函数通过在主窗口的顶部添加一个包含多个按钮的工具栏来实现。
        工具栏的背景颜色被设置为浅灰色，并且会根据定义的按钮文本列表来动态创建按钮。
        每个按钮都绑定了一个事件处理函数，该函数会根据按钮的文本显示相应的界面。
        """
        # 创建一个浅灰色背景的工具栏框架，并将其放置在主窗口的顶部
        toolbar = tk.Frame(self.root, bg="white")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # 定义工具栏按钮的文本列表
        buttons = ["答题", "绑定", "设置", "关于"]
        # 遍历按钮文本列表，创建并添加按钮到工具栏
        for button_text in buttons:
            # 创建按钮时，使用lambda表达式捕获当前的按钮文本，并将其作为事件处理函数的参数
            button = tk.Button(toolbar, 
                            text=button_text, 
                            command=lambda text=button_text: self.show_frame(text),
                            bg="white", 
                            fg="black", 
                            relief=tk.FLAT)  # 初始化relief为FLAT
            button.pack(side=tk.LEFT, padx=5, pady=0)
            if button_text == "答题":  # 初始化时“答题”按钮为SUNKEN
                button.config(relief=tk.SUNKEN)
                self.current_page = button  # 记录当前选中的按钮

    def show_frame(self, frame_name):
        """
        切换并显示指定的框架。
    
        销毁当前框架（如果存在），根据提供的框架名称创建新的框架，并将其打包到界面上。
        同时，更新工具栏中按钮的relief状态，以指示当前选中的按钮。
    
        参数:
        frame_name (str): 要显示的框架名称，可以是"答题"、"绑定"、"设置"或"关于"。
    
        返回:
        无
        """
        if self.current_frame:
            self.current_frame.destroy()
    
        if frame_name == "答题":
            self.current_frame = self.create_answer_frame()
        elif frame_name == "绑定":
            self.current_frame = self.create_bind_frame()
        elif frame_name == "设置":
            self.current_frame = self.create_settings_frame()
        elif frame_name == "关于":
            self.current_frame = self.create_about_frame()
    
        self.current_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
        # 更新工具栏按钮的relief状态
        if self.current_page:
            self.current_page.config(relief=tk.FLAT)  # 将之前选中的按钮设置为FLAT
        for button in self.root.winfo_children()[0].winfo_children():  # 获取工具栏中的所有按钮
            if button['text'] == frame_name:
                button.config(relief=tk.SUNKEN)  # 将当前选中的按钮设置为SUNKEN
                self.current_page = button  # 更新当前选中的按钮

    def create_answer_frame(self):
        """
        创建包含OCR结果、AI回答及其对应操作按钮的框架
        
        此函数负责构建一个框架，该框架包含两个主要部分：
        1. OCR结果文本框和发送按钮
        2. AI回答文本框和复制按钮
        每个文本框都配备了一个功能按钮，且按钮的启用状态取决于文本框内容是否为空
        """
        # 创建主框架
        frame = tk.Frame(self.root)

        # 创建一个子框架来放置“答题”按钮，并使其居中显示
        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.TOP, pady=0, fill=tk.X)

        # 自检按钮
        self.answer_check_button = tk.Button(button_frame, text="自检", 
                                            command=lambda: self.wrda.check_config(callback=True),
                                            width=5, height=1)
        self.answer_check_button.pack(side=tk.LEFT, pady=1, padx=5)

        # 答题按钮
        self.answer_button = tk.Button(button_frame, text="答题",
                                    command=self.answer_question, # 回调方法：OCR识别并答题
                                    width=25, height=1)
        self.answer_button.pack(side=tk.LEFT, pady=1, padx=5, expand=True)

        # 提示按钮
        self.answer_info_button = tk.Button(button_frame, 
                                            text="?", 
                                            fg="blue",
                                            relief=tk.FLAT,
                                            command=lambda: self.messager.raise_info("Messages", "AnswerQuestion"))
        self.answer_info_button.pack(side=tk.RIGHT, pady=1, padx=3)

        # 创建一个子框架来放置OCR结果文本框和标签
        ocr_frame = tk.Frame(frame)
        ocr_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        # OCR结果文本框和label
        ocr_result_label = tk.Label(ocr_frame, text="识别结果：", font=(self.default_font, 12))
        ocr_result_label.pack(pady=(5, 0), anchor=tk.W)
        self.ocr_result_text = scrolledtext.ScrolledText(ocr_frame, height=5, width=20, wrap=tk.WORD, font=(self.default_font, 10))
        self.ocr_result_text.pack(pady=(0, 5), padx=5, fill=tk.BOTH, expand=True)
        # 绑定键盘事件，当文本区域中的按键释放（修改了文本）时，调用enable_send_button方法
        self.ocr_result_text.bind("<KeyRelease>", self.enable_send_button)
        # 发送按钮
        self.send_button = tk.Button(ocr_frame, 
                                    text="发送", 
                                    command=lambda: self.answer_question(self.ocr_result_text.get(1.0, tk.END).strip()), 
                                    state=tk.DISABLED,
                                    width=10, height=1)
        self.send_button.pack(side=tk.BOTTOM, pady=5, padx=5)

        # 创建一个子框架来放置AI回答文本框和标签
        answer_frame = tk.Frame(frame)
        answer_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        # AI答案文本框和label
        answer_label = tk.Label(answer_frame, text="AI回答：", font=(self.default_font, 12))
        answer_label.pack(pady=(5, 0), anchor=tk.W)
        self.answer_text = scrolledtext.ScrolledText(answer_frame, height=5, width=20, wrap=tk.WORD, font=(self.default_font, 10))
        self.answer_text.pack(pady=(0, 5), padx=5, fill=tk.BOTH, expand=True)
        # 复制按钮
        self.copy_button = tk.Button(answer_frame, 
                                    text="复制", 
                                    command=self.copy_answer, 
                                    width=10, height=1)
        self.copy_button.pack(side=tk.BOTTOM, pady=5, padx=5)

        return frame
    
    def create_bind_frame(self):
        """
        创建绑定框架，用于设置绑定方式、选择区域或窗口、以及模型选择。
        
        :return: 返回配置好的框架对象。
        """
        # 创建主框架
        frame = tk.Frame(self.root)

        # 模型选择下拉框
        model_frame = tk.Frame(frame)
        self.model_label = tk.Label(model_frame, text="模型选择：", font=(self.default_font, 12))
        self.model_label.pack(side=tk.LEFT, pady=5)
        self.model_var = tk.StringVar(value=self.wrda.models[0])
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, values=self.wrda.models, font=(self.default_font, 12), state="readonly")
        self.model_dropdown.pack(side=tk.LEFT, pady=5, padx=5)
        model_frame.pack(pady=5)

        # 绑定方式下拉框
        bind_frame = tk.Frame(frame)
        bind_label = tk.Label(bind_frame, text="绑定方式：", font=(self.default_font, 12))
        bind_label.pack(side=tk.LEFT, pady=5)
        self.bind_var = tk.StringVar(value="选择窗口")
        self.bind_dropdown = ttk.Combobox(bind_frame, textvariable=self.bind_var, values=["选择区域", "选择窗口"], font=(self.default_font, 12), state='readonly')
        self.bind_dropdown.pack(side=tk.LEFT, pady=5, padx=5)
        self.bind_dropdown.bind("<<ComboboxSelected>>", self.update_bind_frame)
        bind_frame.pack(pady=5)

        # 选择区域部分
        self.region_frame = tk.Frame(frame)
        select_region_label = tk.Label(self.region_frame, text="点击按钮进行题目截取区域选取：", font=(self.default_font, 12))
        select_region_label.pack(side=tk.LEFT, pady=5)
        select_region_button = tk.Button(self.region_frame, text="选取区域", command=self.select_region)
        select_region_button.pack(side=tk.LEFT, pady=5)
        select_region_info_button = tk.Button(self.region_frame, 
                                              text="?", 
                                              fg="blue",
                                              relief=tk.FLAT,
                                              command=lambda: self.messager.raise_info("Messages","SelectRegion"))
        select_region_info_button.pack(side=tk.RIGHT, padx=10, pady=5)
        self.region_frame.pack_forget()  # 隐藏region_frame

        # 选择窗口部分
        self.window_frame = tk.Frame(frame)
        select_window_label = tk.Label(self.window_frame, text="点击按钮选择识别窗口：", font=(self.default_font, 12))
        select_window_label.pack(side=tk.LEFT, pady=5)
        select_window_button = tk.Button(self.window_frame, 
                                         text="选择窗口", 
                                         command=self.select_window, 
                                         font=(self.default_font, 12))
        select_window_button.pack(side=tk.LEFT, pady=5)

        select_window_info_button = tk.Button(self.window_frame, 
                                              text="?", 
                                              fg="blue", 
                                              relief=tk.FLAT, 
                                              command=lambda: self.messager.raise_info("Messages","SelectWindow"))
        select_window_info_button.pack(side=tk.RIGHT, padx=10, pady=5)
        self.window_frame.pack(pady=5)  # 显示window_frame

        return frame

    def update_bind_frame(self, event):
        """
        更新绑定框架的显示状态。
    
        根据bind_var变量的值，决定显示区域选择框架还是窗口选择框架。
        这个函数通常会在用户交互事件（如点击下拉框选择不同选项）后被调用。
    
        参数:
        - event: 触发的事件对象，通常由Tkinter的事件绑定机制传递。
    
        返回值:
        无返回值。
        """
        # 当bind_var的值为"选择区域"时，显示region_frame框架，隐藏window_frame框架
        if self.bind_var.get() == "选择区域":
            self.region_frame.pack(pady=5)
            self.window_frame.pack_forget()
        # 当bind_var的值为"选择窗口"时，隐藏region_frame框架，显示window_frame框架
        elif self.bind_var.get() == "选择窗口":
            self.region_frame.pack_forget()
            self.window_frame.pack(pady=5)

    def create_settings_frame(self):
        frame = tk.Frame(self.root)

        # App设置
        app_label = tk.Label(frame, text="App")
        app_label.pack(pady=5)

        wechat_label = tk.Label(frame, text="微信：")
        wechat_label.pack(side=tk.LEFT, pady=5)
        self.wechat_entry = tk.Entry(frame, width=50)
        self.wechat_entry.pack(side=tk.LEFT, pady=5)
        wechat_info_button = tk.Button(frame, 
                                       text="?", 
                                       fg="blue", 
                                       relief=tk.FLAT,
                                       command=lambda: self.messager.raise_info("Messages","Wechat"))
        wechat_info_button.pack(side=tk.LEFT, pady=5)

        # Wechat_OCR设置
        wechat_ocr_label = tk.Label(frame, text="Wechat_OCR：")
        wechat_ocr_label.pack(side=tk.LEFT, pady=5)
        self.wechat_ocr_entry = tk.Entry(frame, width=50)
        self.wechat_ocr_entry.pack(side=tk.LEFT, pady=5)
        wechat_ocr_info_button = tk.Button(frame, 
                                           text="?", 
                                           fg="blue", 
                                           relief=tk.FLAT,
                                           command=lambda: self.messager.raise_info("Messages","WechatOcr"))
        wechat_ocr_info_button.pack(side=tk.LEFT, pady=5)

        # Client设置
        client_label = tk.Label(frame, text="Client")
        client_label.pack(pady=5)

        client_dropdown_label = tk.Label(frame, text="Client：")
        client_dropdown_label.pack(side=tk.LEFT, pady=5)
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(frame, textvariable=self.client_var, values=self.wrda.client.keys())
        self.client_dropdown.pack(side=tk.LEFT, pady=5)
        add_client_button = tk.Button(frame, text="添加", command=self.add_client)
        add_client_button.pack(side=tk.LEFT, pady=5)

        secret_id_label = tk.Label(frame, text="SecretId：")
        secret_id_label.pack(side=tk.LEFT, pady=5)
        self.secret_id_entry = tk.Entry(frame, width=50)
        self.secret_id_entry.pack(side=tk.LEFT, pady=5)

        secret_key_label = tk.Label(frame, text="SecretKey：")
        secret_key_label.pack(side=tk.LEFT, pady=5)
        self.secret_key_entry = tk.Entry(frame, width=50)
        self.secret_key_entry.pack(side=tk.LEFT, pady=5)

        save_client_button = tk.Button(frame, text="保存", command=self.save_client)
        save_client_button.pack(side=tk.LEFT, pady=5)

        # Model设置
        model_label = tk.Label(frame, text="Model")
        model_label.pack(pady=5)

        model_dropdown_label = tk.Label(frame, text="Model：")
        model_dropdown_label.pack(side=tk.LEFT, pady=5)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(frame, textvariable=self.model_var, values=self.wrda.models)
        self.model_dropdown.pack(side=tk.LEFT, pady=5)
        add_model_button = tk.Button(frame, text="添加", command=self.add_model)
        add_model_button.pack(side=tk.LEFT, pady=5)

        model_name_label = tk.Label(frame, text="Model Name：")
        model_name_label.pack(side=tk.LEFT, pady=5)
        self.model_name_entry = tk.Entry(frame, width=50)
        self.model_name_entry.pack(side=tk.LEFT, pady=5)

        save_model_button = tk.Button(frame, text="保存", command=self.save_model)
        save_model_button.pack(side=tk.LEFT, pady=5)

        return frame

    def create_about_frame(self):
        frame = tk.Frame(self.root)

        about_label = tk.Label(frame, text="Ciallo～(∠・ω< )⌒★")
        about_label.pack(pady=5)

        return frame

    def select_region(self):
        region = simpledialog.askstring("选取区域", "请输入选取区域坐标（例如：x1,y1,x2,y2）")
        if region:
            self.region_entry.delete(0, tk.END)
            self.region_entry.insert(0, region)

    # 选择截图窗口
    def select_window(self):
        self.wrda.init_screen_catcher()
        if self.wrda.window_sreenshot:
            # 显示截屏区域截图
            self.messager.raise_picture(self.wrda.window_sreenshot)


    def answer_question(self,question:str=""):
        """
        回答问题并更新OCR结果显示。
        
        本方法从wrda对象获取OCR结果和答案，然后更新UI中的OCR结果文本显示。
        """
        if not question:    # question不为空：“发送”按钮被点击
            # 清空OCR文本框
            self.ocr_result_text.delete(1.0, tk.END)
            # 获取OCR结果和答案
            result : list = self.wrda.answer_question()
            # 向OCR结果文本框中输入新的内容
            self.ocr_result_text.insert(tk.END, result[0])
        else:
            # 发送问题
            result : list = self.wrda.answer_question(question)

        # 清空AI回答文本框的现有内容
        self.answer_text.delete(1.0, tk.END)
        # 输出AI回答
        self.answer_text.insert(tk.END, result[1])

    def enable_send_button(self, event):
        """
        启用发送按钮
        """
        if self.ocr_result_text.get(1.0, tk.END).strip():
            self.send_button.config(state=tk.NORMAL)
        else:
            self.send_button.config(state=tk.DISABLED)

    def copy_answer(self):
        """
        复制AI回答
        """
        self.root.clipboard_clear()
        self.root.clipboard_append(self.answer_text.get(1.0, tk.END).strip())
    
    def add_client(self):
        client_name = simpledialog.askstring("添加Client", "请输入Client名称")
        if client_name:
            self.client_var.set(client_name)
            self.client_dropdown["values"] = list(self.wrda.client.keys()) + [client_name]

    def save_client(self):
        client_name = self.client_var.get()
        secret_id = self.secret_id_entry.get()
        secret_key = self.secret_key_entry.get()

        if client_name and secret_id and secret_key:
            self.wrda.client[client_name] = {"secret_id": secret_id, "secret_key": secret_key}
            messagebox.showinfo("保存成功", f"Client {client_name} 已保存")
        else:
            messagebox.showerror("错误", "请填写所有字段")

    def add_model(self):
        model_name = simpledialog.askstring("添加Model", "请输入Model名称")
        if model_name:
            self.model_var.set(model_name)
            self.model_dropdown["values"] = self.wrda.models + [model_name]

    def save_model(self):
        model_name = self.model_name_entry.get()

        if model_name:
            self.wrda.models.append(model_name)
            messagebox.showinfo("保存成功", f"Model {model_name} 已保存")
        else:
            messagebox.showerror("错误", "请填写所有字段")

    def show_about(self):
        messagebox.showinfo("关于", "WeRead Daily Question Assistant\n版本: 1.0\n作者: 你的名字")

if __name__ == "__main__":
    root = tk.Tk()
    app = WrdaGui(root)
    root.mainloop()
    print("结束OCR服务")
    app.wrda.ocr_manager.KillWeChatOCR()