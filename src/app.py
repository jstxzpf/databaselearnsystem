"""
主应用模块 - 集成所有组件并启动应用程序
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.config.config import Config
from src.controllers.learning_controller import LearningController
from src.controllers.exam_controller import ExamController
from src.controllers.review_controller import ReviewController
from src.controllers.settings_controller import SettingsController
from src.views.learning_view import LearningView
from src.views.exam_view import ExamView
from src.views.review_view import ReviewView
from src.utils.data_loader import DataLoader
from src.utils.api_client import ApiClient


class App:
    """主应用类，集成所有组件并启动应用程序"""
    
    def __init__(self):
        """初始化应用程序"""
        # 创建根窗口
        self.root = tk.Tk()
        self.root.title(Config.APP_TITLE)
        self.root.geometry(f"{Config.APP_WIDTH}x{Config.APP_HEIGHT}")
        
        # 初始化组件
        self.init_components()
        
        # 初始化UI
        self.init_ui()
    
    def init_components(self):
        """初始化组件"""
        # 创建API客户端
        self.api_client = ApiClient()
        
        # 创建设置控制器
        self.settings_controller = SettingsController()
        self.settings_controller.set_api_client(self.api_client)
        
        # 加载数据
        self.load_data()
        
        # 初始化控制器
        self.learning_controller = LearningController(
            knowledge_base=self.knowledge_base,
            test_model=self.test_model,
            api_client=self.api_client
        )
        
        self.exam_controller = ExamController(
            knowledge_base=self.knowledge_base,
            test_model=self.test_model,
            api_client=self.api_client
        )
        
        self.review_controller = ReviewController(
            knowledge_base=self.knowledge_base,
            api_client=self.api_client
        )
        
        # 检查API可用性
        self.check_api_availability()
    
    def load_data(self):
        """加载数据"""
        # 加载知识库数据
        success_kb, data_kb = DataLoader.load_knowledge_base()
        if success_kb:
            self.knowledge_base = data_kb
            print(f"成功加载知识库数据")
        else:
            messagebox.showerror("错误", f"无法加载知识库数据: {data_kb}")
            self.knowledge_base = {}
        
        # 加载考试模型数据
        success_tm, data_tm = DataLoader.load_test_model()
        if success_tm:
            self.test_model = data_tm
            print(f"成功加载考试模型数据")
        else:
            messagebox.showerror("错误", f"无法加载考试模型数据: {data_tm}")
            self.test_model = {}
        
        # 显示加载成功消息
        if success_kb and success_tm:
            messagebox.showinfo("成功", Config.DATA_LOAD_SUCCESS_MSG)
    
    def check_api_availability(self):
        """检查API可用性"""
        success, message = self.api_client.check_availability()
        if not success:
            messagebox.showwarning("警告", f"{Config.API_ERROR_MSG}: {message}")
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建菜单栏
        menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="导出学习笔记")
        file_menu.add_command(label="导出考试记录")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 设置菜单
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="API设置")
        settings_menu.add_command(label="用户偏好")
        menu_bar.add_cascade(label="设置", menu=settings_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="使用帮助")
        help_menu.add_command(label="关于")
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING)
        
        # 创建学习视图
        self.learning_view = LearningView(self.notebook, self.learning_controller)
        
        # 创建考试视图
        self.exam_view = ExamView(self.notebook, self.exam_controller)
        
        # 创建复习视图
        self.review_view = ReviewView(self.notebook, self.review_controller)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop() 