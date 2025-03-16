"""
基础视图类 - 视图层的基类
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.config import Config

class BaseView:
    """基础视图类，提供共用的UI功能"""
    
    @staticmethod
    def show_info(title, message):
        """显示信息对话框
        
        Args:
            title: 对话框标题
            message: 对话框消息
        """
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error(title, message):
        """显示错误对话框
        
        Args:
            title: 对话框标题
            message: 对话框消息
        """
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_warning(title, message):
        """显示警告对话框
        
        Args:
            title: 对话框标题
            message: 对话框消息
        """
        messagebox.showwarning(title, message)
    
    @staticmethod
    def create_progress_window(parent, title, message):
        """创建进度窗口
        
        Args:
            parent: 父窗口
            title: 窗口标题
            message: 窗口消息
            
        Returns:
            tuple: (窗口实例, 进度条实例)
        """
        progress_window = tk.Toplevel(parent)
        progress_window.title(title)
        progress_window.geometry("300x100")
        progress_window.transient(parent)
        
        ttk.Label(progress_window, text=message).pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode="indeterminate")
        progress.pack(fill=tk.X, padx=20, pady=10)
        progress.start()
        
        return progress_window, progress 