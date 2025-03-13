import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
from threading import Thread
from PIL import Image, ImageTk
import webbrowser
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
        self.root.title("Wrda")
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

    """
        -------------------------------------------------------------------------
            顶部工具栏
        -------------------------------------------------------------------------
    """

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

    """
        -------------------------------------------------------------------------
            答题页面
        -------------------------------------------------------------------------
    """

    def create_answer_frame(self):
        """
        答题页面主框架
        """
        # 创建主框架
        frame = tk.Frame(self.root)

        # 第 0 行
        # 链接OCR按钮
        self.ocr_manager_botton = tk.Button(frame,
                                            text="连接OCR", 
                                            command=self.wrda.init_ocr_manager,
                                            width=10, height=1)
        self.ocr_manager_botton.grid(row=0, column=0, padx=5, pady=5,sticky="nw")
        # 识别按钮
        answer_recognaize_button = tk.Button(frame,
                                             text="识别", 
                                             command=lambda: self.start_answer_question(mission="r"),
                                             width=15, height=1)
        answer_recognaize_button.grid(row=0, column=1, padx=5, pady=5, sticky="nw")
        # 答题按钮
        answer_button = tk.Button(frame, 
                                  text="识别并答题",
                                  command=self.start_answer_question, # 回调方法：OCR识别并答题
                                  width=15, height=1)
        answer_button.grid(row=0, column=2, padx=5, pady=5, sticky="nw")
        # 提示按钮
        answer_info_button = tk.Button(frame, 
                                       text="?", 
                                       fg="blue",
                                       relief=tk.FLAT,
                                       command=lambda: self.messager.raise_info("Messages", "AnswerQuestion"))
        answer_info_button.grid(row=0, column=3, padx=5, pady=5, sticky="ne")


        # 第 1 行
        # OCR结果label
        ocr_result_label = tk.Label(frame,
                                    text="识别结果：", 
                                    font=(self.default_font, 12))
        ocr_result_label.grid(row=1, column=0, sticky="sw", padx=(5, 0), pady=(5, 0))
        # OCR结果文本框
        self.ocr_result_text = scrolledtext.ScrolledText(frame,
                                                         height=7, width=27, 
                                                         wrap=tk.WORD, 
                                                         font=(self.default_font, 10))
        self.ocr_result_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        # 绑定键盘事件，当文本区域中的按键释放（修改了文本）时，调用enable_send_button方法
        self.ocr_result_text.bind("<KeyRelease>",self.enable_send_button)
        # 发送按钮
        self.answer_send_button = tk.Button(frame,
                                            text="发送", 
                                            command=lambda: self.start_answer_question(self.ocr_result_text.get(1.0, tk.END).strip(),mission="a"), 
                                            state=tk.DISABLED,
                                            width=10, height=1)
        self.answer_send_button.grid(row=3, column=1, padx=5, pady=5, sticky="nw")

        # AI答案label
        answer_label = tk.Label(frame,
                                text="AI回答：", 
                                font=(self.default_font, 12))
        answer_label.grid(row=1, column=2, sticky="sw", padx=(5, 0), pady=(5, 0))
        # AI答案文本框
        self.answer_text = scrolledtext.ScrolledText(frame,
                                                     height=7, width=27, 
                                                     wrap=tk.WORD, 
                                                     font=(self.default_font, 10))
        self.answer_text.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="nsew")
        # 复制按钮
        copy_button = tk.Button(frame,# answer_frame, 
                                text="复制结果", 
                                command=lambda: self.copy_text(entry=self.answer_text), 
                                width=10, height=1)
        copy_button.grid(row=3, column=3, padx=5, pady=5, sticky="nw")

        return frame
    
    def select_region(self):
        messagebox.showinfo("咕", "这个功能还没做")

    def start_answer_question(self,question:str="",mission:str="a"):
        """
        回答问题并更新OCR结果显示。
        mission: a-回答问题，r-识别问题
        """
        if mission == "a":      
            """
            mission为“a”：回答问题
            """    
            if not question:    
                """
                question为空：OCR文本框中无文本
                --> 用户选择直接识别并答题
                """
                print("用户选择直接识别并答题")
                # 清空OCR文本框
                self.ocr_result_text.delete(1.0, tk.END)
                # 获取OCR结果和答案
                result : list = self.wrda.answer_question(mission=mission)
                # 向OCR结果文本框中输入新的内容
                self.ocr_result_text.insert(tk.END, result[0])
            else:
                """
                question不为空：“发送”被点击
                """
                print("用户发送问题")
                # 发送问题
                result : list = self.wrda.answer_question(question=question,mission=mission)
            # 清空AI回答文本框的现有内容
            self.answer_text.delete(1.0, tk.END)
            # 输出AI回答
            self.answer_text.insert(tk.END, result[1])
        elif mission == "r":
            """
            --> 用户选择识别问题
            """
            print("用户选择识别问题")
            # 清空OCR文本框
            self.ocr_result_text.delete(1.0, tk.END)
            # 获取OCR结果和答案
            result : list = self.wrda.answer_question(mission=mission)
            print("result:\n" + result[1])
            # 清空AI回答文本框的现有内容
            self.answer_text.delete(1.0, tk.END)
            # 向OCR结果文本框中输入新的内容(识别结果)
            self.ocr_result_text.insert(tk.END, result[1])
            self.copy_text(entry=self.ocr_result_text)  # 自动复制识别结果到剪切板

    def enable_send_button(self, event):
        """
        启用发送按钮
        """
        if self.ocr_result_text.get(1.0, tk.END).strip():
            self.answer_send_button.config(state=tk.NORMAL)
        else:
            self.answer_send_button.config(state=tk.DISABLED)

    def copy_text(self,entry):
        """
        复制文本框中的内容
        """
        self.root.clipboard_clear()
        self.root.clipboard_append(entry.get(1.0, tk.END).strip())
       
    """
        -------------------------------------------------------------------------
            绑定页面
        -------------------------------------------------------------------------
    """
    
    def create_bind_frame(self):
        """
        绑定页面主框架
        """
        # 创建主框架
        frame = tk.Frame(self.root)

        # 客户端选择下拉框
        client_binding_label = tk.Label(frame, text="选择客户端：", font=(self.default_font, 12))
        client_binding_label.grid(row=0, column=0, pady=10, padx=15, sticky="nw")
        # 下拉菜单
        client_names = list(self.wrda.clients.keys())
        self.client_binding_drop_var = tk.StringVar()
        self.client_binding_drop_var.set(client_names[0] if client_names else "")
        self.client_binding_dropdown = ttk.Combobox(frame, 
                                                    textvariable=self.client_binding_drop_var, 
                                                    values=client_names,
                                                    font=(self.default_font, 12), 
                                                    width=35, 
                                                    state='readonly')
        self.client_binding_dropdown.grid(row=0, column=1, pady=10, padx=15)
        # 选中事件
        self.client_binding_dropdown.bind("<<ComboboxSelected>>", self.update_binding_client)

        # 模型选择下拉框
        model_binding_label = tk.Label(frame, text="模型选择：", font=(self.default_font, 12))
        model_binding_label.grid(row=1, column=0, pady=10, padx=15, sticky="nw")
        # 下拉菜单
        self.model_binding_drop_var = tk.StringVar()
        self.model_binding_dropdown = ttk.Combobox(frame, 
                                                   textvariable=self.model_binding_drop_var, 
                                                   values=[], 
                                                   font=(self.default_font, 12), 
                                                   width=35,
                                                   state="readonly")
        self.model_binding_dropdown.grid(row=1, column=1, pady=10, padx=15)
        # 选中事件
        self.model_binding_dropdown.bind("<<ComboboxSelected>>", self.update_binding_model)

        # 客户端-模型绑定
        client_model_bind_button = tk.Button(frame, text="绑定&连接", 
                                             command=self.llm_bind_link,
                                             font=(self.default_font, 12), 
                                             width=20)
        client_model_bind_button.grid(row=2, column=1, pady=10, padx=15)

        # 绑定方式下拉框
        method_binding_label = tk.Label(frame, text="绑定方式：", font=(self.default_font, 12))
        method_binding_label.grid(row=3, column=0, pady=10, padx=15, sticky="nw")
        # 下拉菜单
        self.method_binding_var = tk.StringVar(value="选择窗口")
        self.method_binding_dropdown = ttk.Combobox(frame, 
                                                    textvariable=self.method_binding_var, 
                                                    values=[ "选择窗口", "选择区域"], 
                                                    font=(self.default_font, 12), 
                                                    width=35,
                                                    state='readonly')
        self.method_binding_dropdown.grid(row=3, column=1, pady=10, padx=15)
        # 选中事件
        self.method_binding_dropdown.bind("<<ComboboxSelected>>", self.update_binding_method)

        # 选择区域部分
        self.region_binding_frame = tk.Frame(frame)
        region_binding_label = tk.Label(self.region_binding_frame, 
                                        text="点击按钮进行题目截取区域选取：", 
                                        font=(self.default_font, 12))
        region_binding_label.grid(row=0, column=0, pady=10, padx=15, sticky="nw")
        region_binding_button = tk.Button(self.region_binding_frame, text="选取区域", command=self.select_region)
        region_binding_button.grid(row=0, column=1, pady=10, padx=15)
        region_binding_info_button = tk.Button(self.region_binding_frame, 
                                                text="?", 
                                                fg="blue",
                                                relief=tk.FLAT,
                                                command=lambda: self.messager.raise_info("Messages","SelectRegion"))
        region_binding_info_button.grid(row=0, column=2, pady=10, padx=15)
        self.region_binding_frame.grid(row=4, column=0, columnspan=2, pady=5, padx=15, sticky="nsew")  # 使用grid布局

        # 选择窗口部分
        self.window_binding_frame = tk.Frame(frame)
        window_binding_label = tk.Label(self.window_binding_frame, 
                                        text="点击按钮选择识别窗口：", 
                                        font=(self.default_font, 12))
        window_binding_label.grid(row=0, column=0, pady=10, padx=15, sticky="nw")
        window_binding_button = tk.Button(self.window_binding_frame, 
                                        text="选择窗口", 
                                        command=self.bind_window, 
                                        font=(self.default_font, 12))
        window_binding_button.grid(row=0, column=1, pady=10, padx=15)
        window_binding_info_button = tk.Button(self.window_binding_frame, 
                                            text="?", 
                                            fg="blue", 
                                            relief=tk.FLAT, 
                                            command=lambda: self.messager.raise_info("Messages","SelectWindow"))
        window_binding_info_button.grid(row=0, column=2, pady=10, padx=15)
        self.window_binding_frame.grid(row=4, column=0, columnspan=2, pady=5, padx=15, sticky="nsew")  # 使用grid布局

        # 初始化绑定客户端&模型
        self.update_binding_client(None)
        # 初始化绑定方式
        self.update_binding_method(None)

        return frame
    
    def llm_bind_link(self):
        print("开始绑定")
        self.wrda.selected_client = self.client_binding_drop_var.get()
        self.wrda.selected_model = self.model_binding_drop_var.get()
        print("selected client:" + self.wrda.selected_client)
        print("selected model:" + self.wrda.selected_model)
        if self.wrda.init_llm():
            self.messager.raise_info("Messages","BindSuccess")


    def update_binding_client(self,event):
        """
        更新选中的客户端和模型
        """
        # 获取选中的客户端名称
        self.wrda.selected_client = self.client_binding_drop_var.get()
        
        # 获取模型名
        models = self.wrda.clients[self.wrda.selected_client].get("Models", []) if self.wrda.selected_client else []
        self.model_binding_drop_var.set(models[0] if models else "")
        self.model_binding_dropdown["values"] = models

    def update_binding_model(self,event):
        """
        更新选中的模型名
        """
        self.wrda.selected_model = self.model_binding_drop_var.get()

    def update_binding_method(self,event):
        """
        更新绑定框架的显示状态。
    
        根据bind_var变量的值，决定显示区域选择框架还是窗口选择框架。
        这个函数通常会在用户交互事件（如点击下拉框选择不同选项）后被调用。
    
        参数:
        - event: 触发的事件对象，通常由Tkinter的事件绑定机制传递。
        """
        # 当bind_var的值为"选择区域"时，显示region_frame框架，隐藏window_frame框架
        if self.method_binding_var.get() == "选择区域":
            self.region_binding_frame.grid()
            self.window_binding_frame.grid_remove()
        # 当bind_var的值为"选择窗口"时，隐藏region_frame框架，显示window_frame框架
        elif self.method_binding_var.get() == "选择窗口":
            self.region_binding_frame.grid_remove()
            self.window_binding_frame.grid()

    def bind_window(self):
        """
            选择绑定窗口
        """
        # 初始化屏幕截图管理器
        self.wrda.init_screen_catcher()
        # 存储窗口截图
        self.wrda.window_sreenshot = self.wrda.screen_catcher.select_window()

        if self.wrda.window_sreenshot:
            # 显示截屏区域截图
            self.messager.raise_picture(self.wrda.window_sreenshot)

    def clear_binding(self):
        self.wrda.selected_client = ""
        self.wrda.selected_model = ""
        self.messager.raise_info("Message","BindingCleared")

    """
        -------------------------------------------------------------------------
            设置页面
        -------------------------------------------------------------------------
    """

    def create_settings_frame(self):
        """
        设置页面框架
        """
        # 创建主框架
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 微信设置
        wechat_setting_label = tk.Label(frame, text="微信", font=(self.default_font, 12))
        wechat_setting_label.grid(row=1, column=0, sticky=tk.W, pady=10, padx=15)
        # 文本框
        self.wechat_setting_entry = tk.Entry(frame, width=40)
        self.wechat_setting_entry.grid(row=1, column=1, pady=10, padx=15)
        self.wechat_setting_entry.insert(0, self.wrda.wechat_path)
        # 预览按钮
        wechat_pre_button = tk.Button(frame, 
                                      text="预览", 
                                      command=lambda: self.path_preview(isfile=True))
        wechat_pre_button.grid(row=1, column=2, pady=10, padx=(0, 5))
        # 保存按钮
        wechat_save_button = tk.Button(frame, 
                                       text="保存", 
                                       command=self.save_wechat_path)
        wechat_save_button.grid(row=1, column=3, pady=10, padx=(0, 5))
        # 信息按钮
        wechat_info_button = tk.Button(frame, 
                                       text="?", 
                                       fg="blue", 
                                       relief=tk.FLAT,
                                       command=lambda: self.messager.raise_info("Messages","Wechat"))
        wechat_info_button.grid(row=1, column=4, pady=5, padx=(0, 10))

        # Wechat_OCR设置
        wechat_ocr_setting_label = tk.Label(frame, text="微信OCR", font=(self.default_font, 12))
        wechat_ocr_setting_label.grid(row=2, column=0, sticky=tk.W, pady=10, padx=15)
        # 文本框
        self.wechat_ocr_setting_entry = tk.Entry(frame, width=40)
        self.wechat_ocr_setting_entry.grid(row=2, column=1, pady=10, padx=15)
        self.wechat_ocr_setting_entry.insert(0, self.wrda.wechat_ocr_path)
        # 预览
        wechat_ocr_pre_button = tk.Button(frame, 
                                          text="预览", 
                                          command=lambda: self.path_preview(isfile=False))
        wechat_ocr_pre_button.grid(row=2, column=2, pady=10, padx=(0, 5))
        # 保存
        wechat_ocr_save_button = tk.Button(frame, 
                                           text="保存", 
                                           command=self.save_wechat_ocr_path)
        wechat_ocr_save_button.grid(row=2, column=3, pady=10, padx=(0, 5))
        # 信息
        wechat_ocr_info_button = tk.Button(frame, 
                                           text="?", 
                                           fg="blue", 
                                           relief=tk.FLAT,
                                           command=lambda: self.messager.raise_info("Messages","WechatOcr"))
        wechat_ocr_info_button.grid(row=2, column=4, pady=10, padx=(0, 10))

        # Client下拉菜单及其相关按钮
        client_setting_label = tk.Label(frame, text="客户端", font=(self.default_font, 12))
        client_setting_label.grid(row=3, column=0, sticky=tk.W, pady=10, padx=15)
        # 下拉菜单
        client_names = list(self.wrda.clients.keys())
        self.client_setting_drop_var = tk.StringVar()
        self.client_setting_drop_var.set(client_names[0] if client_names else "")
        self.client_setting_dropdown = ttk.Combobox(frame, 
                                                    textvariable=self.client_setting_drop_var, 
                                                    values=client_names, 
                                                    width=35, 
                                                    state='readonly')
        self.client_setting_dropdown.grid(row=3, column=1, pady=10, padx=15)
        # 事件绑定
        self.client_setting_dropdown.bind("<<ComboboxSelected>>",self.update_setting_models)
        # 编辑
        client_edit_button = tk.Button(frame, text="编辑", 
                                       command=lambda: self.raise_client_setting(command="edit"))
        client_edit_button.grid(row=3, column=2, pady=10, padx=(0, 10))
        # 添加
        client_add_button = tk.Button(frame, text="添加", command=self.raise_client_setting)
        client_add_button.grid(row=3, column=3, pady=10, padx=(0, 10))
        client_info_button = tk.Button(frame, 
                                       text="?", 
                                       fg="blue", 
                                       relief=tk.FLAT,
                                       command=lambda: self.messager.raise_info("Messages","Clients"))
        client_info_button.grid(row=3, column=4, pady=10, padx=(0, 10))

        # Model下拉菜单及其相关按钮
        model_setting_label = tk.Label(frame, text="模型：", font=(self.default_font, 12))
        model_setting_label.grid(row=4, column=0, sticky=tk.W, pady=5, padx=15)
        self.model_setting_drop_var = tk.StringVar()
        self.model_setting_dropdown = ttk.Combobox(frame, 
                                                   textvariable=self.model_setting_drop_var, 
                                                   values=[], 
                                                   width=35)
        self.model_setting_dropdown.grid(row=4, column=1, pady=5, padx=15)
        # 事件绑定
        self.model_setting_dropdown.bind()
        # 删除
        model_delete_button = tk.Button(frame, text="编辑", 
                                        command=lambda: self.raise_model_setting(command="edit"))
        model_delete_button.grid(row=4, column=2, pady=5, padx=(0, 10))
        # 添加
        model_add_button = tk.Button(frame, text="添加", command=self.raise_model_setting)
        model_add_button.grid(row=4, column=3, pady=5, padx=(0, 10))
        # 提示
        model_info_button = tk.Button(frame, 
                                           text="?", 
                                           fg="blue", 
                                           relief=tk.FLAT,
                                           command=lambda: self.messager.raise_info("Messages","Models"))
        model_info_button.grid(row=4, column=4, pady=5, padx=(0, 10))

        # 更新client和model列表
        self.update_setting_models(None)

        return frame

    def path_preview(self,isfile:bool=True) -> None:
        """
        预览文件/文件夹路径，并将路径填写到相应的对话框中

        isfile: True 为预览文件路径，False 为预览文件夹路径
        """
        if isfile:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.wechat_setting_entry.delete(0, tk.END)
                self.wechat_setting_entry.insert(0, folder_path)
        else:
            file_path = filedialog.askopenfilename()
            if file_path:
                self.wechat_ocr_setting_entry.delete(0, tk.END)
                self.wechat_ocr_setting_entry.insert(0, file_path)

    def update_setting_models(self,event):
        client = self.client_setting_drop_var.get()

        # 获取模型名
        models = self.wrda.clients[client].get("Models", []) if client else []
        self.model_setting_drop_var.set(models[0] if models else "")
        self.model_setting_dropdown["values"] = models
    
    def save_wechat_path(self):
        """
        保存wechat_entry中的路径到self.wrda.wechat_path。
        """
        file_path = self.wechat_setting_entry.get().strip()   # 获取wechat_entry中的路径
        if file_path:
            if self.wrda.save_config(key="WeChat", value=[file_path]):
                self.messager.raise_info(type="Messages", keyword="PathSaved")
        else:
            self.messager.raise_info(type="Error", keyword="InvalidPath")

    def save_wechat_ocr_path(self):
        """
        保存wechat_ocr_entry中的路径到self.wrda.wechat_ocr_path。
        """
        folder_path = self.wechat_ocr_setting_entry.get().strip()
        if folder_path:
            if self.wrda.save_config(key="WeChatOCR", value=[folder_path]):
                self.messager.raise_info(type="Messages", keyword="PathSaved")
        else:
            self.messager.raise_info(type="Error", keyword="InvalidPath")    

    def raise_client_setting(self, command: str = "add"):
        """
        添加/编辑client
        @param command: add/edit
        """
        title = {"add": "添加客户端", "edit": "编辑客户端"}

        # 创建一个新的顶级窗口
        set_client_window = tk.Toplevel(self.root)
        set_client_window.title(title[command])  # 设置窗口标题
        set_client_window.geometry("700x250")
        self.messager.locate_window(set_client_window, self.root, c_width=700, c_height=250)

        client_name = ""
        secret_id = ""
        secret_key = ""

        if command == "edit":
            client_name = self.client_setting_drop_var.get()  # 获取当前选中的客户端名称
            secret_id = self.wrda.clients[client_name]["secret_id"]
            secret_key = self.wrda.clients[client_name]["secret_key"]

        # 客户端名称标签和文本框
        client_name_label = tk.Label(set_client_window, text="客户端名称：")
        client_name_label.grid(row=0, column=0, padx=5, pady=5)
        client_name_entry = tk.Entry(set_client_window, width=30)
        client_name_entry.grid(row=0, column=1, padx=5, pady=5)
        client_name_entry.insert(0, client_name)
        set_client_info_button = tk.Button(set_client_window, 
                                        text="?", 
                                        fg="blue", 
                                        relief=tk.FLAT,
                                        command=lambda: self.messager.raise_info(type="Messages", keyword="SetClient", parent=set_client_window))
        set_client_info_button.grid(row=0, column=2, padx=5, pady=5)

        # SecretId标签、文本框和info按钮
        secret_id_label = tk.Label(set_client_window, text="SecretId：")
        secret_id_label.grid(row=1, column=0, padx=5, pady=5)
        secret_id_entry = tk.Entry(set_client_window, width=30)
        secret_id_entry.grid(row=1, column=1, padx=5, pady=5)
        secret_id_entry.insert(0, secret_id)

        # SecretKey标签、文本框和info按钮
        secret_key_label = tk.Label(set_client_window, text="SecretKey：")
        secret_key_label.grid(row=2, column=0, padx=5, pady=5)
        secret_key_entry = tk.Entry(set_client_window, width=30)
        secret_key_entry.grid(row=2, column=1, padx=5, pady=5)
        secret_key_entry.insert(0, secret_key)

        if command == "edit":
            # 删除按钮
            delete_button = tk.Button(set_client_window, text="删除", 
                                    command=lambda: self.save_client(window=set_client_window, 
                                                                     old_name=self.client_setting_drop_var.get(),
                                                                     new_name="", 
                                                                     secret_id=secret_id_entry.get(), 
                                                                     secret_key=secret_key_entry.get(),
                                                                     command="delete"))
            delete_button.grid(row=3, column=0, padx=10, pady=10)

        # 保存按钮
        save_button = tk.Button(set_client_window, text="保存", 
                                command=lambda: self.save_client(window=set_client_window, 
                                                                 old_name=self.client_setting_drop_var.get(),
                                                                 new_name=client_name_entry.get(), 
                                                                 secret_id=secret_id_entry.get(), 
                                                                 secret_key=secret_key_entry.get(),
                                                                 command=command))
        save_button.grid(row=3, column=1, padx=10, pady=10)

        # 取消按钮
        cancel_button = tk.Button(set_client_window, text="取消", command=set_client_window.destroy)
        cancel_button.grid(row=3, column=2, padx=10, pady=10)

    def save_client(self, window:tk.Toplevel,old_name:str, new_name:str, secret_id:str, secret_key:str, command:str):
        """
        保存客户端信息
        """
        # command list = ["add", "edit", "delete"]

        state : bool = False
        if command == "add" or command == "edit":
            if new_name and secret_id and secret_key: # 需三个都不为空
                # 保存
                state = self.wrda.save_config(key="Clients",
                                              value=[command,old_name,new_name,secret_id,secret_key])
                if state:
                    # 提示保存成功
                    self.messager.raise_info("Messages", "Saved", parent=window)
                    # 更新下拉菜单
                    self.client_setting_drop_var.set(new_name)
                    self.client_setting_dropdown["values"] = list(self.wrda.clients.keys())
                    # 更新模型下拉框
                    self.update_setting_models(None)
                    window.destroy()
            else:
                self.messager.raise_info(type="Error", keyword="EmptyValue",parent=window)
        elif command == "delete":
            confirm = self.messager.raise_confirm(parent=window)
            if confirm: # 确认删除
                state = self.wrda.save_config(key="Clients",
                                              value=[command,old_name,new_name,secret_id,secret_key])
                if state:
                    # 提示保存成功
                    self.messager.raise_info("Messages", "Saved", parent=window)
                    # 更新下拉菜单
                    self.client_setting_drop_var.set(new_name)
                    self.client_setting_dropdown["values"] = list(self.wrda.clients.keys())
                    # 更新模型下拉框
                    self.model_setting_drop_var.set("")
                    self.model_setting_dropdown["values"] = []
                    if old_name == self.wrda.selected_client: # 删除的客户端正好是目前绑定的
                        self.clear_binding()
                    window.destroy()
                    


    def raise_model_setting(self,command:str="add"):
        """
        添加/编辑模型
        :param command:add/edit
        """
        # command = [add,edit,delete]
        title = {
            "add":"添加模型",
            "edit":"编辑模型"
        }

        set_model_window = tk.Toplevel(self.root)
        set_model_window.title(title[command])
        set_model_window.geometry("520x120")
        self.messager.locate_window(set_model_window,self.root,520,120)

        model_name = ""
        if command == "edit":
            model_name = self.model_setting_drop_var.get()
        
        # 模型名称标签和文本框
        model_name_label = tk.Label(set_model_window, text="模型名称：")
        model_name_label.grid(row=0, column=0, padx=5, pady=5)
        model_name_entry = tk.Entry(set_model_window, width=20)
        model_name_entry.grid(row=0, column=1, padx=5, pady=5)
        model_name_entry.insert(0, model_name)

        if command == "edit":
            # 删除按钮
            delete_button = tk.Button(set_model_window, text="删除", 
                                    command=lambda: self.save_model(window=set_model_window, 
                                                                    client=self.client_setting_drop_var.get(),
                                                                    old_name=self.model_setting_drop_var.get(),
                                                                    new_name="", 
                                                                    command="delete"))
            delete_button.grid(row=3, column=0, padx=10, pady=10)

        # 保存按钮
        save_button = tk.Button(set_model_window, text="保存", 
                                command=lambda: self.save_model(window=set_model_window, 
                                                                client=self.client_setting_drop_var.get(),
                                                                old_name=model_name,
                                                                new_name=model_name_entry.get(), 
                                                                command=command))
        save_button.grid(row=3, column=1, padx=10, pady=10)

        # 取消按钮
        cancel_button = tk.Button(set_model_window, text="取消", command=set_model_window.destroy)
        cancel_button.grid(row=3, column=2, padx=10, pady=10)



    def save_model(self,window:tk.Toplevel,client:str,old_name:str,new_name:str,command:str):
        """
        保存模型
        command : [add,edit,delet]
        """
        state : bool = False
        if command == "add" or command == "edit":
            if new_name : 
                # 保存
                state = self.wrda.save_config(key="Models",
                                              value=[command,client,old_name,new_name])
                if state:
                    # 提示保存成功
                    self.messager.raise_info("Messages", "Saved", parent=window)
                    # 更新下拉菜单
                    self.model_setting_drop_var.set(new_name)
                    self.model_setting_dropdown["values"] = self.wrda.clients[client].get("Models", [])
                    window.destroy()
            else:
                self.messager.raise_info(type="Error", keyword="EmptyValue",parent=window)
        elif command == "delete":
            confirm = self.messager.raise_confirm(parent=window)
            if confirm:
                state = self.wrda.save_config(key="Models",
                                              value=[command,client,old_name,new_name])
                if state:
                    if old_name == self.wrda.selected_model:
                        self.clear_binding()
                    # 提示保存成功
                    self.messager.raise_info("Messages", "Saved", parent=window)
                    # 更新下拉菜单
                    self.model_setting_drop_var.set(new_name)
                    self.model_setting_dropdown["values"] = self.wrda.clients[client].get("Models", [])
                    window.destroy()

    """
        -------------------------------------------------------------------------
            关于页面
        -------------------------------------------------------------------------
    """

    def create_about_frame(self):
        frame = tk.Frame(self.root)

        # 第一行：WeRead Dailyquestion Assistant（居中，加粗）
        title_label = tk.Label(frame, 
                               text="WeRead Dailyquestion Assistant", 
                               font=(self.default_font, 16, "bold"), 
                               justify="center")
        title_label.pack(padx=10,pady=10)

        # 第二行：版本
        version_label = tk.Label(frame, text="版本：1.0.0", 
                                 font=(self.default_font, 12), 
                                 justify="center")
        version_label.pack(padx=10,pady=5)

        # 第三行：作者
        author_label = tk.Label(frame, text="作者：ÆlieanZ", 
                                font=(self.default_font, 12), 
                                justify="center")
        author_label.pack(padx=10,pady=5)
        
        # 第四行： 仓库源码
        repo_link = "https://github.com/EileanZYZ/weread_dailyquestion_assistant"
        repo_frame = tk.Frame(frame)
        repo_label_1 = tk.Label(repo_frame, 
                            text="仓库源码：", 
                            font=(self.default_font, 12), 
                            justify="left")
        repo_label_1.pack(side=tk.LEFT, padx=0, pady=5)
        repo_label_2 = tk.Label(repo_frame, 
                            text="GitHub", 
                            font=(self.default_font, 12), 
                            justify="left", 
                            fg="blue", 
                            cursor="hand2")
        repo_label_2.pack(side=tk.LEFT, padx=0, pady=5)
        repo_label_2.bind("<Button-1>", 
                        lambda e: self.open_url(repo_link))
        repo_frame.pack(pady=5)

        # 第五行：【声明】（居中，加粗）
        disclaimer_title_label = tk.Label(frame, 
                                          text="【声明】", 
                                          font=(self.default_font, 14, "bold"), 
                                          justify="center")
        disclaimer_title_label.pack(padx=10,pady=10)

        # 第六行：本软件仅供个人使用，不可用于商业用途（左对齐）
        disclaimer_label = tk.Label(frame, 
                                    text="本软件仅供个人使用，不可用于商业用途", 
                                    font=(self.default_font, 12), 
                                    justify="center")
        disclaimer_label.pack(padx=10,pady=5)

        return frame

    def open_url(self, url):
        webbrowser.open(url)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = WrdaGui(root)
    print("Ciallo～(∠・ω< )⌒★")
    root.mainloop()
    # print("结束OCR服务")
    if app.wrda.ocr_activated:
        app.wrda.ocr_manager.KillWeChatOCR()