"""
设置视图类 - 处理设置相关的UI
"""

import tkinter as tk
from tkinter import ttk
from src.config.config import Config
from src.views.base_view import BaseView

class SettingsView(BaseView):
    """设置视图类，实现设置对话框的UI"""
    
    def __init__(self, parent, controller):
        """初始化设置视图
        
        Args:
            parent: 父窗口
            controller: 设置控制器实例
        """
        self.parent = parent
        self.controller = controller
    
    def show_api_settings_dialog(self):
        """显示API设置对话框"""
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Ollama API 设置")
        settings_window.geometry("400x230")
        settings_window.transient(self.parent)
        settings_window.resizable(False, False)
        
        # 说明标签
        ttk.Label(settings_window, text="请设置Ollama的chat API接口参数：", 
                 font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE, "bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # API地址设置
        ttk.Label(settings_window, text="API地址:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        api_url_var = tk.StringVar(value=self.controller.get_api_url())
        api_url_entry = ttk.Entry(settings_window, textvariable=api_url_var, width=40)
        api_url_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # 模型名称设置
        ttk.Label(settings_window, text="模型名称:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        model_name_var = tk.StringVar(value=self.controller.get_model_name())
        model_entry = ttk.Entry(settings_window, textvariable=model_name_var, width=40)
        model_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # 提示标签
        ttk.Label(settings_window, text='注意: 需要Ollama v0.1.14+版本支持chat API', 
                 font=(Config.FONT_FAMILY, Config.SMALL_FONT_SIZE), foreground="red").grid(
            row=3, column=0, columnspan=2, padx=10, pady=0, sticky="w")
        
        # 测试连接按钮
        def on_test_connection():
            api_url = api_url_var.get()
            model_name = model_name_var.get()
            
            success, _ = self.controller.update_settings(api_url, model_name)
            if not success:
                self.show_error("错误", "更新设置失败")
                return
            
            success, message = self.controller.test_connection()
            if success:
                self.show_info("成功", f"连接测试成功: {message}")
            else:
                self.show_warning("警告", f"连接测试失败: {message}")
        
        ttk.Button(settings_window, text="测试连接", command=on_test_connection).grid(
            row=4, column=0, padx=10, pady=20)
        
        # 保存按钮
        def on_save_settings():
            api_url = api_url_var.get()
            model_name = model_name_var.get()
            
            success, error = self.controller.update_settings(api_url, model_name)
            if success:
                self.show_info("成功", "已保存API设置")
                settings_window.destroy()
            else:
                self.show_error("错误", f"保存设置失败: {error}")
        
        ttk.Button(settings_window, text="保存", command=on_save_settings).grid(
            row=4, column=1, padx=10, pady=20)
    
    def show_about_dialog(self):
        """显示关于对话框"""
        about_text = """数据库学习系统 v1.0
        
基于Tkinter和Ollama AI的交互式学习工具
专为辅助学生学习数据库课程设计

系统集成了知识学习、考试生成和试卷审批三大功能
通过本地AI模型提供智能辅导
"""
        self.show_info("关于", about_text) 