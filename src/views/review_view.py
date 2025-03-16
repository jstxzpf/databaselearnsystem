"""
复习功能视图类 - 复习标签页的UI实现
"""

import tkinter as tk
from tkinter import ttk, filedialog
from src.config.config import Config
from src.views.base_view import BaseView

class ReviewView(BaseView):
    """复习功能视图类，实现复习标签页的UI"""
    
    def __init__(self, parent, controller):
        """初始化复习视图
        
        Args:
            parent: 父窗口
            controller: 复习控制器实例
        """
        self.parent = parent
        self.controller = controller
        self.imported_exam = None
        
        # 创建复习标签页
        self.frame = ttk.Frame(parent)
        self.parent.add(self.frame, text=Config.REVIEW_TAB_TITLE)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建控制框架
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING)
        
        # 导入试卷按钮
        import_button = ttk.Button(control_frame, text="导入试卷", command=self.on_import_exam)
        import_button.pack(side=tk.LEFT, padx=Config.WIDGET_PADDING)
        
        # 复习试卷按钮
        self.review_button = ttk.Button(control_frame, text="开始复习", command=self.on_review_exam, state=tk.DISABLED)
        self.review_button.pack(side=tk.LEFT, padx=Config.WIDGET_PADDING)
        
        # 创建内容区域
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING)
        
        # 水平分割内容区域
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # 创建考试内容显示区域
        exam_frame = ttk.LabelFrame(content_frame, text="考试内容")
        exam_frame.grid(row=0, column=0, sticky="nsew", padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 创建文本区域和滚动条
        self.exam_text = tk.Text(exam_frame, height=15, width=80, 
                               font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                               wrap=tk.WORD, bg="white", state=tk.DISABLED)
        self.exam_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        exam_scrollbar = ttk.Scrollbar(exam_frame, orient="vertical", command=self.exam_text.yview)
        self.exam_text.configure(yscrollcommand=exam_scrollbar.set)
        exam_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加初始提示
        self.exam_text.configure(state=tk.NORMAL)
        self.exam_text.insert(tk.END, Config.EMPTY_REVIEW_EXAM_HINT)
        self.exam_text.configure(state=tk.DISABLED)
        
        # 创建复习结果显示区域
        result_frame = ttk.LabelFrame(content_frame, text="复习结果")
        result_frame.grid(row=1, column=0, sticky="nsew", padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 创建文本区域和滚动条
        self.result_text = tk.Text(result_frame, height=15, width=80, 
                                 font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                                 wrap=tk.WORD, bg="white", state=tk.DISABLED)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加初始提示
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.insert(tk.END, Config.EMPTY_REVIEW_RESULT_HINT)
        self.result_text.configure(state=tk.DISABLED)
        
        # 设置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
    def on_import_exam(self):
        """导入试卷按钮事件处理"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt")],
            title="选择试卷文件"
        )
        
        if not file_path:
            return  # 用户取消了选择
        
        try:
            # 读取试卷内容
            with open(file_path, 'r', encoding='utf-8') as file:
                exam_content = file.read()
            
            # 保存导入的试卷内容
            self.imported_exam = exam_content
            
            # 显示试卷内容
            self.exam_text.configure(state=tk.NORMAL)
            self.exam_text.delete(1.0, tk.END)
            self.exam_text.insert(tk.END, exam_content)
            self.exam_text.configure(state=tk.DISABLED)
            
            # 启用复习按钮
            self.review_button.configure(state=tk.NORMAL)
            
        except Exception as e:
            self.show_error("错误", f"导入试卷失败: {str(e)}")
    
    def on_review_exam(self):
        """复习试卷按钮事件处理"""
        if not self.imported_exam:
            self.show_info("提示", "请先导入试卷")
            return
        
        # 显示进度对话框
        progress_window, _ = self.create_progress_window(
            self.parent, "生成复习内容中", "正在生成复习内容，请稍候..."
        )
        
        try:
            # 处理复习
            review_result = self.controller.review_exam(self.imported_exam)
            
            # 关闭进度对话框
            progress_window.destroy()
            
            # 显示复习结果
            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, review_result)
            self.result_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            progress_window.destroy()
            self.show_error("错误", f"生成复习内容失败: {str(e)}") 