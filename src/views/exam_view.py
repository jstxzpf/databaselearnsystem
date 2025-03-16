"""
考试功能视图类 - 考试标签页的UI实现
"""

import tkinter as tk
from tkinter import ttk, filedialog
from src.config.config import Config
from src.views.base_view import BaseView

class ExamView(BaseView):
    """考试功能视图类，实现考试标签页的UI"""
    
    def __init__(self, parent, controller):
        """初始化考试视图
        
        Args:
            parent: 父窗口
            controller: 考试控制器实例
        """
        self.parent = parent
        self.controller = controller
        
        # 创建考试标签页
        self.frame = ttk.Frame(parent)
        self.parent.add(self.frame, text=Config.EXAM_TAB_TITLE)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建左侧章节选择框
        self.chapter_frame = ttk.LabelFrame(self.frame, text=Config.EXAM_CHAPTER_LABEL)
        self.chapter_frame.grid(row=0, column=0, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING, sticky="nsew")
        
        # 创建章节选择列表框（多选）
        self.chapter_listbox = tk.Listbox(self.chapter_frame, width=40, height=20, 
                                         font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE), 
                                         selectmode=tk.MULTIPLE, bg="white", selectbackground="#4a6984")
        self.chapter_listbox.pack(fill=tk.BOTH, expand=True, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 为章节列表添加滚动条
        chapter_scrollbar = ttk.Scrollbar(self.chapter_frame, orient="vertical", command=self.chapter_listbox.yview)
        self.chapter_listbox.configure(yscrollcommand=chapter_scrollbar.set)
        chapter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加章节到列表框
        if self.controller.get_chapters():
            for chapter in self.controller.get_chapters():
                self.chapter_listbox.insert(tk.END, chapter)
        else:
            self.chapter_listbox.insert(tk.END, "没有章节数据")
            
        # 添加选择提示
        chapter_hint = ttk.Label(self.chapter_frame, text="(按住Ctrl键可选择多个章节)", 
                                font=(Config.FONT_FAMILY, Config.SMALL_FONT_SIZE))
        chapter_hint.pack(anchor="w", pady=(5, 0))
        
        # 创建右侧考试控制面板
        self.control_frame = ttk.Frame(self.frame)
        self.control_frame.grid(row=0, column=1, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING, sticky="nsew")
        
        # 显示考试信息
        exam_name, duration = self.controller.get_exam_info()
        
        exam_name_label = ttk.Label(self.control_frame, 
                                    text=f"考试名称: {exam_name}", 
                                    font=(Config.FONT_FAMILY, Config.LABEL_FONT_SIZE))
        exam_name_label.pack(anchor="w", pady=5)
        
        exam_time_label = ttk.Label(self.control_frame, 
                                   text=f"考试时长: {duration}", 
                                   font=(Config.FONT_FAMILY, Config.LABEL_FONT_SIZE))
        exam_time_label.pack(anchor="w", pady=5)
        
        # 题型信息
        ttk.Label(self.control_frame, text="题型信息:", 
                 font=(Config.FONT_FAMILY, Config.LABEL_FONT_SIZE, "bold")).pack(anchor="w", pady=10)
        
        question_types = self.controller.get_question_types()
        if question_types:
            for question_type in question_types:
                type_name = question_type.get("题型名称", "")
                question_count = question_type.get("题量", 0)
                total_score = question_type.get("总分", 0)
                
                type_label = ttk.Label(self.control_frame, 
                                      text=f"{type_name}: {question_count}题, {total_score}分",
                                      font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE + 1))
                type_label.pack(anchor="w", pady=2)
        else:
            ttk.Label(self.control_frame, text="(未找到题型信息)", 
                     font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE)).pack(anchor="w", pady=2)
        
        # 操作提示
        hint_frame = ttk.Frame(self.control_frame)
        hint_frame.pack(fill=tk.X, pady=10)
        
        hint_label = ttk.Label(hint_frame, text=Config.EMPTY_EXAM_HINT,
                              font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                              wraplength=300, justify=tk.LEFT)
        hint_label.pack(fill=tk.X, pady=5)
        
        # 添加生成考试按钮 - 使用样式使其更加突出
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        generate_button = tk.Button(button_frame, text="生成考试", 
                                    bg=Config.BUTTON_GENERATE_BG, fg=Config.BUTTON_GENERATE_FG,
                                    font=(Config.FONT_FAMILY, Config.LABEL_FONT_SIZE, "bold"),
                                    height=2, command=self.on_generate_exam)
        generate_button.pack(fill=tk.X, padx=20)
        
        # 设置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
    
    def on_generate_exam(self):
        """生成考试按钮事件处理"""
        # 获取选中的章节
        selected_indices = self.chapter_listbox.curselection()
        if not selected_indices:
            self.show_info("提示", "请至少选择一个章节")
            return
            
        # 检查是否选择了"没有章节数据"
        selected_chapters = [self.chapter_listbox.get(i) for i in selected_indices]
        if "没有章节数据" in selected_chapters:
            self.show_info("提示", "无法使用'没有章节数据'生成试卷")
            return
        
        # 准备保存对话框
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            title="保存考试试卷"
        )
        
        if not file_path:
            return  # 用户取消了保存
        
        # 显示进度对话框
        progress_window, _ = self.create_progress_window(
            self.parent, "生成试卷中", "正在生成试卷，请稍候..."
        )
        
        try:
            # 生成试卷
            self.controller.generate_exam(selected_chapters, file_path)
            
            # 关闭进度对话框
            progress_window.destroy()
            
            # 显示成功消息
            self.show_info("成功", f"试卷已成功保存到: {file_path}")
        except Exception as e:
            progress_window.destroy()
            self.show_error("错误", f"生成试卷失败: {str(e)}") 