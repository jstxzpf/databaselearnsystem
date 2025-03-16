"""
学习功能视图类 - 学习标签页的UI实现
"""

import os
import tkinter as tk
from tkinter import ttk
import markdown
import tempfile
import webview
import threading
from tkhtmlview import HTMLScrolledText
from src.config.config import Config
from src.views.base_view import BaseView

class LearningView(BaseView):
    """学习功能视图类，实现学习标签页的UI"""
    
    def __init__(self, parent, controller):
        """初始化学习视图
        
        Args:
            parent: 父窗口
            controller: 学习控制器实例
        """
        self.parent = parent
        self.controller = controller
        
        # 创建学习标签页
        self.frame = ttk.Frame(parent)
        self.parent.add(self.frame, text=Config.LEARNING_TAB_TITLE)
        
        # 存储当前选中的章节
        self.current_chapter = None
        
        # 存储当前选中的内容
        self.current_content = None
        
        # 存储HTML临时文件路径
        self.html_temp_file = None
        
        # webview窗口
        self.web_window = None
        
        # 初始化UI
        self.init_ui()
        
        # 创建临时目录用于存放HTML文件
        self.temp_dir = tempfile.mkdtemp()
        
        # 尝试绑定标签页选择事件
        try:
            self.parent.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        except:
            print("无法绑定标签页切换事件")
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置网格布局
        self.frame.columnconfigure(0, weight=1)  # 左侧章节列表
        self.frame.columnconfigure(1, weight=2)  # 中间内容列表
        self.frame.columnconfigure(2, weight=3)  # 右侧解释区域
        self.frame.rowconfigure(0, weight=1)     # 主内容区域
        self.frame.rowconfigure(1, weight=0)     # 底部按钮区域
        
        # 创建左侧章节选择框
        self.chapter_frame = ttk.LabelFrame(self.frame, text=Config.LEARNING_CHAPTER_LABEL)
        self.chapter_frame.grid(row=0, column=0, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING, sticky="nsew")
        
        # 创建章节列表框和滚动条
        chapter_scroll = ttk.Scrollbar(self.chapter_frame)
        chapter_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chapter_listbox = tk.Listbox(self.chapter_frame, 
                                         font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                                         bg="white", selectbackground="#4a6984")
        self.chapter_listbox.pack(fill=tk.BOTH, expand=True, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 配置滚动条
        self.chapter_listbox.config(yscrollcommand=chapter_scroll.set)
        chapter_scroll.config(command=self.chapter_listbox.yview)
        
        # 添加章节到列表框
        chapters = self.controller.get_chapters()
        if chapters:
            for chapter in chapters:
                self.chapter_listbox.insert(tk.END, chapter)
        else:
            self.chapter_listbox.insert(tk.END, Config.EMPTY_CHAPTER_HINT)
        
        # 绑定章节选择事件
        self.chapter_listbox.bind('<<ListboxSelect>>', self.on_chapter_select)
        
        # 创建中间内容选择框
        self.content_frame = ttk.LabelFrame(self.frame, text=Config.LEARNING_CONTENT_LABEL)
        self.content_frame.grid(row=0, column=1, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING, sticky="nsew")
        
        # 创建内容列表框和滚动条
        content_scroll = ttk.Scrollbar(self.content_frame)
        content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.content_listbox = tk.Listbox(self.content_frame, 
                                         font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                                         bg="white", selectbackground="#4a6984")
        self.content_listbox.pack(fill=tk.BOTH, expand=True, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 配置滚动条
        self.content_listbox.config(yscrollcommand=content_scroll.set)
        content_scroll.config(command=self.content_listbox.yview)
        
        # 添加初始空状态提示
        self.content_listbox.insert(tk.END, Config.EMPTY_CONTENT_HINT)
        
        # 绑定内容选择事件
        self.content_listbox.bind('<Double-1>', self.on_content_double_click)
        self.content_listbox.bind('<FocusIn>', self.on_content_focus)
        self.content_listbox.bind('<Button-3>', self.show_content_context_menu)
        
        # 创建右侧AI解析区域
        self.explanation_frame = ttk.LabelFrame(self.frame, text=Config.LEARNING_EXPLANATION_LABEL)
        self.explanation_frame.grid(row=0, column=2, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING, sticky="nsew")
        
        # 创建一个按钮用于打开WebView窗口
        self.webview_button = ttk.Button(
            self.explanation_frame, 
            text="打开Markdown预览", 
            command=self.open_webview_window
        )
        self.webview_button.pack(fill=tk.X, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 创建基本的预览文本区域（用于简单预览，详细内容会在webview中显示）
        self.preview_text = tk.Text(self.explanation_frame, wrap=tk.WORD, 
                                 font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=Config.WIDGET_PADDING, pady=Config.WIDGET_PADDING)
        
        # 添加滚动条
        preview_scroll = ttk.Scrollbar(self.explanation_frame, command=self.preview_text.yview)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=preview_scroll.set)
        
        # 显示初始空状态提示
        self.show_markdown_content(Config.EMPTY_EXPLANATION_HINT)
        
        # 添加底部按钮区域
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.grid(row=1, column=0, columnspan=3, padx=Config.FRAME_PADDING, pady=Config.FRAME_PADDING, sticky="ew")
        
        # 添加批量生成按钮
        self.batch_generate_button = ttk.Button(
            self.button_frame, 
            text="批量生成所有章节解析", 
            command=self.batch_generate_explanations
        )
        self.batch_generate_button.pack(side=tk.LEFT, padx=Config.WIDGET_PADDING)
        
        # 添加生成当前章节按钮
        self.generate_current_button = ttk.Button(
            self.button_frame,
            text="生成当前章节解析",
            command=self.generate_current_chapter
        )
        self.generate_current_button.pack(side=tk.LEFT, padx=Config.WIDGET_PADDING)
        
        # 添加缓存管理按钮
        self.cache_manage_button = ttk.Button(
            self.button_frame, 
            text="缓存管理", 
            command=self.show_cache_management
        )
        self.cache_manage_button.pack(side=tk.LEFT, padx=Config.WIDGET_PADDING)
        
        # 添加进度标签
        self.progress_label = ttk.Label(self.button_frame, text="")
        self.progress_label.pack(side=tk.LEFT, padx=Config.WIDGET_PADDING)
    
    def show_markdown_content(self, text, is_markdown=False):
        """显示Markdown内容
        
        Args:
            text: 要显示的文本内容
            is_markdown: 是否为Markdown格式
        """
        try:
            # 在文本框中显示原始内容
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, text)
            
            # 保存当前内容用于webview窗口
            self.current_markdown_content = text
            self.current_is_markdown = is_markdown
            
            # 如果当前已有webview窗口打开，更新内容
            if hasattr(self, 'web_window') and self.web_window is not None:
                self.update_webview_content()
                
        except Exception as e:
            print(f"显示Markdown内容失败: {str(e)}")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"显示内容失败: {str(e)}")
            self.show_error("显示内容失败", f"无法显示内容: {str(e)}")
    
    def update_webview_content(self):
        """更新WebView窗口中的内容"""
        if not hasattr(self, 'current_markdown_content'):
            return
            
        text = self.current_markdown_content
        is_markdown = getattr(self, 'current_is_markdown', False)
        
        try:
            # 如果是Markdown格式，转换为HTML
            if is_markdown:
                # 去除可能存在的HTML标签
                import re
                text = re.sub(r'^<[^>]*>', '', text)
                text = re.sub(r'</?(?:div|span|p)[^>]*>', '', text)
                
                # 预先处理Mermaid代码块，在Markdown转HTML前处理
                mermaid_blocks = []
                mermaid_pattern = r'```\s*mermaid\s*([\s\S]*?)```'
                
                # 提取所有Mermaid代码块
                for i, match in enumerate(re.finditer(mermaid_pattern, text)):
                    block_id = 'mermaid-' + str(i)
                    content = match.group(1).strip()
                    
                    # 清理Mermaid代码块内容
                    content = content.replace('（', '(').replace('）', ')')
                    content = content.replace('"', '"').replace('"', '"')
                    content = content.replace('，', ',').replace('：', ':')
                    content = content.replace('【', '[').replace('】', ']')
                    content = content.replace('；', ';')
                    
                    # 修复常见的语法问题
                    lines = content.split('\n')
                    if len(lines) >= 1:
                        first_line = lines[0].strip()
                        valid_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                                     'stateDiagram', 'erDiagram', 'gantt', 'pie']
                        
                        if not any(first_line.startswith(t) for t in valid_types):
                            content = 'graph TD\n' + content
                    
                    # 创建唯一占位符
                    placeholder = 'MERMAID_PLACEHOLDER_' + block_id
                    mermaid_blocks.append((placeholder, content))
                    
                    # 替换原始文本中的Mermaid代码块为占位符
                    text = text.replace(match.group(0), placeholder)
                
                # 转换Markdown为HTML
                html_content = markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])
                
                # 替换占位符为Mermaid div
                for placeholder, content in mermaid_blocks:
                    div_id = placeholder.replace("MERMAID_PLACEHOLDER_", "")
                    mermaid_div = '<div class="mermaid" id="' + div_id + '">' + content + '</div>'
                    html_content = html_content.replace(placeholder, mermaid_div)
                
                # 处理剩余可能以不同方式格式化的Mermaid代码块
                html_content = html_content.replace('<pre><code class="language-mermaid">', '<div class="mermaid">')
                html_content = re.sub(r'<pre><code>mermaid\s*', '<div class="mermaid">', html_content)
                html_content = re.sub(r'</code></pre>', '</div>', html_content)
            else:
                # 如果不是Markdown，将纯文本包装为HTML
                html_content = '<pre style="white-space: pre-wrap; word-wrap: break-word;">' + text + '</pre>'
            
            # 应用CSS样式和Mermaid支持
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Markdown内容</title>
                <style>
                    body {{
                        font-family: "Microsoft YaHei", Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        padding: 20px;
                        max-width: 900px;
                        margin: 0 auto;
                    }}
                    pre {{
                        background-color: #f5f5f5;
                        padding: 12px;
                        border-radius: 5px;
                        border: 1px solid #e3e3e3;
                        overflow-x: auto;
                    }}
                    code {{
                        background-color: #f0f0f0;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: Consolas, Monaco, monospace;
                        font-size: 0.9em;
                    }}
                    h1 {{
                        color: #286090;
                        font-size: 24px;
                        border-bottom: 2px solid #286090;
                        padding-bottom: 8px;
                    }}
                    h2 {{
                        color: #337ab7;
                        font-size: 20px;
                        border-bottom: 1px solid #ddd;
                        padding-bottom: 5px;
                    }}
                    h3, h4, h5, h6 {{
                        color: #333;
                        margin-top: 16px;
                        margin-bottom: 8px;
                    }}
                    blockquote {{
                        border-left: 4px solid #4CAF50;
                        padding: 10px 15px;
                        color: #555;
                        background-color: #f9f9f9;
                        margin: 15px 0;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 16px 0;
                    }}
                    table, th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        text-align: left;
                        font-weight: bold;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f8f8f8;
                    }}
                    ul, ol {{
                        padding-left: 25px;
                    }}
                    li {{
                        margin-bottom: 5px;
                    }}
                    a {{
                        color: #2196F3;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    .mermaid {{
                        text-align: center;
                        margin: 20px 0;
                        background-color: white;
                        padding: 15px;
                        border-radius: 5px;
                    }}
                    /* 代码高亮样式 */
                    .language-sql, .language-python, .language-java {{
                        display: block;
                        background-color: #282c34;
                        color: #abb2bf;
                        padding: 12px;
                        border-radius: 5px;
                        overflow-x: auto;
                        font-family: Consolas, Monaco, monospace;
                    }}
                    .hljs-keyword {{
                        color: #c678dd;
                    }}
                    .hljs-string {{
                        color: #98c379;
                    }}
                    .hljs-number {{
                        color: #d19a66;
                    }}
                    .hljs-comment {{
                        color: #5c6370;
                        font-style: italic;
                    }}
                    .error-box {{
                        color: #721c24;
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        padding: 10px;
                        margin: 10px 0;
                        border-radius: 5px;
                    }}
                    .mermaid-source {{
                        background-color: #f8f9fa;
                        border: 1px dashed #ccc;
                        padding: 10px;
                        margin-top: 10px;
                        font-family: monospace;
                        white-space: pre;
                        font-size: 0.9em;
                    }}
                    #render-button {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 15px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                        margin: 20px 0;
                        display: block;
                    }}
                    #render-button:hover {{
                        background-color: #45a049;
                    }}
                </style>
                <!-- 直接内联Mermaid库，避免网络加载问题 -->
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
                <script>
                    // 初始化完成标志
                    let mermaidInitialized = false;
                    let renderAttempted = false;
                    
                    // 日志函数
                    function log(message) {{
                        console.log('[Mermaid]', message);
                        const logElement = document.getElementById('mermaid-log');
                        if (logElement) {{
                            const timeStr = new Date().toLocaleTimeString();
                            logElement.innerHTML += '<div>[' + timeStr + '] ' + message + '</div>';
                        }}
                    }}
                    
                    // 初始化Mermaid
                    function initMermaid() {{
                        if (mermaidInitialized) {{
                            log('Mermaid已经初始化，跳过');
                            return true;
                        }}
                        
                        try {{
                            if (typeof mermaid === 'undefined') {{
                                log('Mermaid未加载，尝试从备用源加载');
                                loadBackupMermaid();
                                return false;
                            }}
                            
                            log('开始初始化Mermaid...');
                            mermaid.initialize({{
                                startOnLoad: false,  // 我们手动控制渲染
                                theme: 'default',
                                logLevel: 'error',
                                securityLevel: 'loose',
                                flowchart: {{ 
                                    useMaxWidth: false, 
                                    htmlLabels: true,
                                    curve: 'basis'
                                }},
                                fontFamily: 'Microsoft YaHei, sans-serif'
                            }});
                            
                            log('Mermaid初始化成功，版本: ' + mermaid.version());
                            mermaidInitialized = true;
                            return true;
                        }} catch (error) {{
                            log('Mermaid初始化失败: ' + error.message);
                            document.getElementById('mermaid-error').style.display = 'block';
                            document.getElementById('error-details').textContent = error.message;
                            return false;
                        }}
                    }}
                    
                    // 加载备用Mermaid库
                    function loadBackupMermaid() {{
                        log('尝试加载备用Mermaid库...');
                        const sources = [
                            'https://unpkg.com/mermaid@10.6.1/dist/mermaid.min.js',
                            'https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js'
                        ];
                        
                        let loaded = false;
                        for (const source of sources) {{
                            const script = document.createElement('script');
                            script.src = source;
                            script.async = false;
                            script.onload = () => {{
                                if (!loaded) {{
                                    loaded = true;
                                    log('成功从' + source + '加载Mermaid');
                                    initMermaid() && renderAllDiagrams();
                                }}
                            }};
                            document.head.appendChild(script);
                        }}
                    }}
                    
                    // 渲染所有图表
                    function renderAllDiagrams() {{
                        if (!initMermaid()) {{
                            return;
                        }}
                        
                        if (renderAttempted) {{
                            log('已尝试渲染，使用强制模式重新渲染');
                        }}
                        
                        renderAttempted = true;
                        log('开始渲染所有Mermaid图表...');
                        
                        const diagrams = document.querySelectorAll('.mermaid');
                        log('找到' + diagrams.length + '个Mermaid图表');
                        
                        if (diagrams.length === 0) {{
                            log('没有找到Mermaid图表元素');
                            return;
                        }}
                        
                        // 强制重新渲染
                        try {{
                            mermaid.run({{
                                nodes: [...diagrams],
                                suppressErrors: false
                            }});
                            log('成功运行mermaid.run()');
                        }} catch (error) {{
                            log('mermaid.run()失败: ' + error.message);
                            
                            // 回退到逐个渲染
                            diagrams.forEach((diagram, index) => {{
                                renderSingleDiagram(diagram, index);
                            }});
                        }}
                        
                        // 添加查看源码按钮
                        diagrams.forEach((diagram, index) => {{
                            // 如果已经有按钮了，不再添加
                            if (diagram.nextElementSibling && 
                                diagram.nextElementSibling.classList.contains('mermaid-toggle')) {{
                                return;
                            }}
                            
                            const sourceDiv = document.createElement('div');
                            sourceDiv.className = 'mermaid-source';
                            sourceDiv.style.display = 'none';
                            sourceDiv.textContent = diagram.getAttribute('data-original') || diagram.textContent;
                            
                            const toggleButton = document.createElement('button');
                            toggleButton.textContent = '查看Mermaid源码';
                            toggleButton.className = 'mermaid-toggle';
                            toggleButton.style.fontSize = '12px';
                            toggleButton.style.margin = '5px 0';
                            toggleButton.onclick = function() {{
                                if (sourceDiv.style.display === 'none') {{
                                    sourceDiv.style.display = 'block';
                                    this.textContent = '隐藏Mermaid源码';
                                }} else {{
                                    sourceDiv.style.display = 'none';
                                    this.textContent = '查看Mermaid源码';
                                }}
                            }};
                            
                            // 保存原始内容
                            diagram.setAttribute('data-original', diagram.textContent);
                            
                            // 插入按钮和源码div
                            diagram.insertAdjacentElement('afterend', sourceDiv);
                            diagram.insertAdjacentElement('afterend', toggleButton);
                        }});
                    }}
                    
                    // 渲染单个图表
                    function renderSingleDiagram(element, index) {{
                        try {{
                            const content = element.textContent.trim();
                            const id = element.id || 'mermaid-' + index;
                            element.id = id;
                            
                            log('尝试渲染图表 #' + index + ' (ID: ' + id + ')');
                            
                            mermaid.render(id, content).then(result => {{
                                element.innerHTML = result.svg;
                                log('图表 #' + index + ' 渲染成功');
                            }}).catch(error => {{
                                log('图表 #' + index + ' 渲染失败: ' + error.message);
                                showRenderError(element, content, error.message);
                            }});
                        }} catch (error) {{
                            log('处理图表 #' + index + ' 时出错: ' + error.message);
                            showRenderError(element, element.textContent, error.message);
                        }}
                    }}
                    
                    // 显示渲染错误
                    function showRenderError(element, content, errorMessage) {{
                        const errorBox = document.createElement('div');
                        errorBox.className = 'error-box';
                        errorBox.innerHTML = '<strong>Mermaid图表渲染错误:</strong><br>' + 
                            errorMessage + '<br><br>' +
                            '<button onclick="retryRender(this.parentNode, \'' + element.id + '\')">重试渲染</button>';
                        
                        element.innerHTML = '';
                        element.appendChild(errorBox);
                        
                        // 用于调试
                        console.error("Mermaid渲染错误:", errorMessage);
                        console.log("图表内容:", content);
                    }}
                    
                    // 重试渲染
                    function retryRender(errorElement, diagramId) {{
                        const diagram = document.getElementById(diagramId);
                        if (!diagram) return;
                        
                        const content = diagram.getAttribute('data-original') || diagram.textContent;
                        log('重试渲染图表 ' + diagramId);
                        
                        try {{
                            mermaid.render('retry-' + diagramId, content).then(result => {{
                                diagram.innerHTML = result.svg;
                                log('重试渲染成功');
                            }}).catch(error => {{
                                showRenderError(diagram, content, '重试失败: ' + error.message);
                            }});
                        }} catch (error) {{
                            showRenderError(diagram, content, '重试过程出错: ' + error.message);
                        }}
                    }}
                    
                    // 页面加载完成后执行
                    document.addEventListener('DOMContentLoaded', function() {{
                        log('页面DOM加载完成');
                        setTimeout(() => {{
                            log('DOM加载后延迟执行初始化');
                            initMermaid() && renderAllDiagrams();
                        }}, 100);
                    }});
                    
                    // 页面完全加载后执行
                    window.addEventListener('load', function() {{
                        log('页面完全加载完成');
                        setTimeout(() => {{
                            log('页面加载后延迟执行初始化');
                            initMermaid() && renderAllDiagrams();
                        }}, 500);
                    }});
                    
                    // 提供手动渲染按钮功能
                    function manualRender() {{
                        log('手动触发渲染');
                        renderAllDiagrams();
                    }}
                </script>
            </head>
            <body>
                <!-- 添加手动渲染按钮 -->
                <button id="render-button" onclick="manualRender()">
                    手动渲染Mermaid图表
                </button>
                
                {html_content}
                
                <!-- Mermaid错误信息 -->
                <div id="mermaid-error" style="display:none; background-color:#ffecec; color:#721c24; padding:15px; margin:20px 0; border:1px solid #f5c6cb; border-radius:5px;">
                    <h3>Mermaid图表加载或渲染失败</h3>
                    <p>无法加载或渲染Mermaid图表。可能原因:</p>
                    <ul>
                        <li>网络连接问题，无法加载Mermaid库</li>
                        <li>图表语法错误 <span id="error-details" style="font-style:italic;"></span></li>
                        <li>浏览器兼容性问题</li>
                    </ul>
                    <p>常见语法错误包括:</p>
                    <ul>
                        <li>缺少图表类型声明（如graph TD）</li>
                        <li>使用了中文标点符号而非英文标点</li>
                        <li>箭头格式不正确（应使用 -->, ===>, -.->, 等）</li>
                        <li>节点定义格式不正确</li>
                    </ul>
                    <button onclick="document.getElementById('debug-panel').style.display='block'; this.parentNode.style.display='none';">
                        显示调试信息
                    </button>
                </div>
                
                <!-- 调试面板 -->
                <div id="debug-panel" style="display:none; background-color:#f8f9fa; padding:15px; margin:20px 0; border:1px solid #dee2e6; border-radius:5px;">
                    <h3>Mermaid调试信息</h3>
                    <div id="mermaid-log" style="max-height:300px; overflow:auto; background:#f0f0f0; padding:10px; border-radius:3px; font-family:monospace; font-size:12px;"></div>
                    <div style="margin-top:10px;">
                        <button onclick="document.getElementById('debug-panel').style.display='none'">关闭调试信息</button>
                        <button onclick="manualRender()">重新渲染所有图表</button>
                    </div>
                </div>
                
                <script>
                    // 初始化调试信息
                    log('浏览器信息: ' + navigator.userAgent);
                    log('Mermaid库状态: ' + (typeof mermaid !== 'undefined' ? '已加载，版本 ' + mermaid.version() : '未加载'));
                </script>
            </body>
            </html>
            """
            
            # 保存HTML到临时文件
            if self.html_temp_file and os.path.exists(self.html_temp_file):
                os.remove(self.html_temp_file)
                
            fd, self.html_temp_file = tempfile.mkstemp(suffix='.html', dir=self.temp_dir)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(styled_html)
            
            # 如果webview窗口已经打开，加载新内容
            if hasattr(self, 'web_window') and self.web_window is not None:
                try:
                    # 使用文件协议加载本地HTML文件
                    file_url = 'file://' + os.path.abspath(self.html_temp_file)
                    webview.load_url(file_url, self.web_window)
                except Exception as e:
                    print(f"更新webview内容失败: {str(e)}")
            
        except Exception as e:
            print(f"准备webview内容失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def open_webview_window(self):
        """打开WebView窗口显示当前内容"""
        if not hasattr(self, 'current_markdown_content'):
            self.show_error("无内容", "没有可显示的内容")
            return
            
        # 更新webview内容
        self.update_webview_content()
        
        # 文件路径
        if not self.html_temp_file or not os.path.exists(self.html_temp_file):
            self.show_error("文件不存在", "预览文件不存在或尚未生成")
            return
            
        # 优先使用系统浏览器打开
        try:
            import webbrowser
            file_url = 'file://' + os.path.abspath(self.html_temp_file)
            webbrowser.open(file_url)
            return
        except Exception as e:
            print(f"使用系统浏览器打开HTML失败: {str(e)}")
        
        # 尝试使用子进程运行预览器
        try:
            import subprocess
            import sys

            # 获取当前显示的内容名称作为窗口标题
            title = "Markdown内容"
            if hasattr(self, 'current_content') and self.current_content:
                title = '解析内容 - ' + self.current_content
                
            # 创建子进程运行预览器
            previewer_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "md_previewer.py")
            python_exe = sys.executable
            
            # 使用Popen启动子进程
            process = subprocess.Popen(
                [python_exe, previewer_path, self.html_temp_file, "--title", title],
                # 不捕获输出，让子进程输出到控制台
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE  # 在Windows上创建新控制台窗口
            )
            
            # 非阻塞方式检查进程是否启动成功
            def check_process():
                if process.poll() is not None:
                    # 进程已经结束，检查是否有错误
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    if stderr:
                        print(f"预览器进程错误: {stderr}")
                        # 如果失败，显示错误并尝试直接打开文件
                        self.show_error("预览器启动失败", 
                                       f"无法启动预览窗口，请手动打开以下文件:\n{self.html_temp_file}")
                
            # 延迟检查进程状态
            self.after(1000, check_process)
            
        except Exception as e:
            print(f"启动预览器进程失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 显示错误信息，并建议手动打开文件
            self.show_error("无法启动预览", 
                          f"无法启动预览窗口，请手动打开以下文件:\n{self.html_temp_file}")
    
    def on_chapter_select(self, event):
        """章节选择事件处理
        
        Args:
            event: 事件对象
        """
        # 获取选中的章节索引
        selection = self.chapter_listbox.curselection()
        if not selection:
            return
        
        # 检查是否选择了空状态提示
        chapter_text = self.chapter_listbox.get(selection[0])
        if chapter_text == Config.EMPTY_CHAPTER_HINT:
            return
        
        # 存储当前选中的章节
        self.current_chapter = chapter_text
            
        # 清空内容列表
        self.content_listbox.delete(0, tk.END)
        
        # 获取并显示选中章节的内容
        contents = self.controller.get_contents(chapter_text)
        
        # 显示主要概念
        if "concepts" in contents and contents["concepts"]:
            self.content_listbox.insert(tk.END, Config.MAIN_CONCEPTS_SEPARATOR)
            for concept in contents["concepts"]:
                self.content_listbox.insert(tk.END, concept)
        else:
            self.content_listbox.insert(tk.END, Config.EMPTY_CONTENT_HINT)
        
        # 显示知识点
        if "knowledge_points" in contents and contents["knowledge_points"]:
            self.content_listbox.insert(tk.END, Config.MAIN_CONTENTS_SEPARATOR)
            for point in contents["knowledge_points"]:
                self.content_listbox.insert(tk.END, point)
        else:
            self.content_listbox.insert(tk.END, Config.EMPTY_KNOWLEDGE_HINT)
        
        # 重置AI解析区域标题
        self.explanation_frame.config(text=Config.LEARNING_EXPLANATION_LABEL)
        
        # 显示提示信息
        self.show_markdown_content(Config.EMPTY_EXPLANATION_HINT)
    
    def on_content_double_click(self, event):
        """内容双击事件处理
        
        Args:
            event: 事件对象
        """
        # 调用更新解析方法，不强制更新
        self.update_explanation(force=False)
    
    def on_content_focus(self, event=None):
        """内容列表获取焦点时的处理，确保章节保持选中状态
        
        Args:
            event: 事件对象
        """
        # 如果有当前章节，确保章节列表中保持选中状态
        if self.current_chapter:
            # 找到当前章节在列表中的索引
            for i in range(self.chapter_listbox.size()):
                if self.chapter_listbox.get(i) == self.current_chapter:
                    # 若当前没有选中项，则选中该章节
                    if not self.chapter_listbox.curselection():
                        self.chapter_listbox.selection_set(i)
                    break
                    
    def on_tab_changed(self, event=None):
        """标签页切换事件处理，确保显示正确内容
        
        Args:
            event: 事件对象
        """
        # 获取当前选中的标签页
        current_tab = self.parent.select()
        
        # 如果当前标签页是学习标签页，确保章节保持选中状态
        if current_tab == str(self.frame):
            # 确保章节保持选中状态
            self.ensure_chapter_selection()
    
    def ensure_chapter_selection(self):
        """确保章节选择状态，并显示相应内容"""
        # 如果有当前章节，确保章节列表中保持选中状态
        if self.current_chapter:
            # 找到当前章节在列表中的索引
            for i in range(self.chapter_listbox.size()):
                if self.chapter_listbox.get(i) == self.current_chapter:
                    # 若当前没有选中项，则选中该章节
                    if not self.chapter_listbox.curselection():
                        self.chapter_listbox.selection_set(i)
                    break
        elif self.chapter_listbox.size() > 0 and self.chapter_listbox.get(0) != Config.EMPTY_CHAPTER_HINT:
            # 如果没有当前章节但章节列表有内容，选择第一个章节
            self.chapter_listbox.selection_set(0)
            # 模拟章节选择事件
            self.on_chapter_select(None)
    
    def show_content_context_menu(self, event):
        """显示内容列表的右键菜单
        
        Args:
            event: 事件对象
        """
        # 获取鼠标点击位置的项目
        index = self.content_listbox.nearest(event.y)
        if index < 0:
            return
            
        # 选中该项目
        self.content_listbox.selection_clear(0, tk.END)
        self.content_listbox.selection_set(index)
        self.content_listbox.activate(index)
        
        # 获取内容文本
        content_text = self.content_listbox.get(index)
        
        # 检查是否选择了分隔符或空状态提示
        if content_text in [Config.MAIN_CONCEPTS_SEPARATOR, Config.MAIN_CONTENTS_SEPARATOR, 
                          Config.EMPTY_CONTENT_HINT, Config.EMPTY_KNOWLEDGE_HINT]:
            return
            
        # 创建右键菜单
        context_menu = tk.Menu(self.frame, tearoff=0)
        context_menu.add_command(label="查看解析", command=lambda: self.on_content_double_click(None))
        context_menu.add_command(label="强制更新解析", command=lambda: self.update_explanation(force=True))
        
        # 显示菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def update_explanation(self, force=False):
        """更新解析内容
        
        Args:
            force: 是否强制更新
        """
        # 获取选中的内容索引
        selection = self.content_listbox.curselection()
        if not selection:
            return
            
        # 获取内容文本
        content_text = self.content_listbox.get(selection[0])
        
        # 检查是否选择了分隔符或空状态提示
        if content_text in [Config.MAIN_CONCEPTS_SEPARATOR, Config.MAIN_CONTENTS_SEPARATOR, 
                          Config.EMPTY_CONTENT_HINT, Config.EMPTY_KNOWLEDGE_HINT]:
            return
            
        # 优先使用存储的当前章节，如果没有则尝试从列表中获取
        chapter_text = self.current_chapter
        
        # 如果没有当前章节，则尝试从列表中获取
        if not chapter_text:
            chapter_selection = self.chapter_listbox.curselection()
            if not chapter_selection:
                print("错误：未选择章节，无法解析内容")
                self.show_error("错误", "请先选择一个章节")
                return
            chapter_text = self.chapter_listbox.get(chapter_selection[0])
        
        # 存储当前内容
        self.current_content = content_text
        
        # 显示加载提示
        loading_msg = "正在" + ("重新生成" if force else "获取") + "「" + content_text + "」的AI解析，请稍候..."
        self.show_markdown_content(loading_msg)
        
        # 显示进度窗口
        progress_window, progress_label = self.create_progress_window(
            self.parent, 
            "生成解析中" if force else "获取解析中", 
            "正在" + ("重新生成" if force else "获取") + "「" + content_text + "」的AI解析，请稍候..."
        )
        
        # 更新UI
        self.frame.update()
        
        try:
            # 获取AI解析内容
            explanation = self.controller.get_explanation(chapter_text, content_text, force_update=force)
            
            # 关闭进度窗口
            progress_window.destroy()
            
            # 更新窗口标题，显示当前内容
            self.explanation_frame.config(text=Config.LEARNING_EXPLANATION_LABEL + " - " + content_text)
            
            # 显示解析内容，将其作为Markdown格式处理
            self.show_markdown_content(explanation, is_markdown=True)
            
        except Exception as e:
            # 关闭进度窗口
            progress_window.destroy()
            
            # 显示错误信息
            error_msg = "生成解析失败:\n" + str(e) + "\n\n请检查API连接或稍后重试。"
            self.show_markdown_content(error_msg)
            
            self.show_error("生成解析失败", "无法生成「" + content_text + "」的解析: " + str(e))
    
    def __del__(self):
        """析构函数，清理资源"""
        # 删除临时文件和目录
        try:
            if hasattr(self, 'html_temp_file') and self.html_temp_file and os.path.exists(self.html_temp_file):
                os.remove(self.html_temp_file)
                
            if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
            
    def batch_generate_explanations(self):
        """批量生成所有章节的知识点和概念解析"""
        # 确认是否生成所有章节
        confirm = self.show_confirm(
            "批量生成确认", 
            "确定要生成所有章节的内容解析吗？\n\n"
            "这个过程将为所有章节的所有知识点和概念生成解析，\n"
            "需要消耗大量API调用并可能需要较长时间。\n\n"
            "是否继续？"
        )
        
        if not confirm:
            return
            
        # 获取所有章节
        all_chapters = self.controller.get_chapters()
        
        if not all_chapters:
            self.show_error("错误", "无法获取章节列表")
            return
            
        # 计算总项目数
        total_items = 0
        chapter_items = {}
        
        for chapter in all_chapters:
            contents = self.controller.get_contents(chapter)
            all_items = []
            
            if "concepts" in contents and contents["concepts"]:
                all_items.extend(contents["concepts"])
            if "knowledge_points" in contents and contents["knowledge_points"]:
                all_items.extend(contents["knowledge_points"])
                
            if all_items:
                chapter_items[chapter] = all_items
                total_items += len(all_items)
        
        if total_items == 0:
            self.show_error("错误", "没有可生成的内容")
            return
            
        # 创建进度窗口
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("批量生成中")
        progress_window.geometry("400x160")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        
        # 设置进度窗口内容
        progress_frame = ttk.Frame(progress_window, padding=20)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(progress_frame, text="正在为所有章节生成解析内容", 
                 font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE)).pack(pady=10)
        
        progress_text = ttk.Label(progress_frame, text="正在准备...",
                              font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE))
        progress_text.pack(pady=5)
        
        progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                      length=350, mode="determinate", maximum=total_items)
        progress_bar.pack(pady=10)
        
        # 添加取消按钮
        self.cancel_batch = False
        cancel_button = ttk.Button(progress_frame, text="取消", 
                                 command=lambda: self.cancel_batch_generation(progress_window))
        cancel_button.pack(pady=5)
        
        # 更新UI
        progress_window.update()
        
        # 开始批量生成
        generated = 0
        errors = 0
        progress = 0
        
        for chapter, items in chapter_items.items():
            if self.cancel_batch:
                break
                
            for item in items:
                if self.cancel_batch:
                    break
                    
                # 更新进度
                progress += 1
                progress_bar["value"] = progress
                progress_text.config(text="正在处理 (" + str(progress) + "/" + str(total_items) + "): " + chapter + " - " + item)
                progress_window.update()
                
                try:
                    # 生成解析（强制更新）
                    self.controller.get_explanation(chapter, item, force_update=True)
                    generated += 1
                except Exception as e:
                    print("生成「" + chapter + " - " + item + "」的解析失败: " + str(e))
                    errors += 1
                    
                # 短暂延迟，给UI时间刷新
                import time
                time.sleep(0.1)
        
        # 关闭进度窗口
        progress_window.destroy()
        
        # 显示完成信息
        if self.cancel_batch:
            self.show_info("操作取消", "批量生成已取消。\n已成功生成: " + str(generated) + "\n失败: " + str(errors))
        else:
            self.show_info("批量生成完成", "成功生成 " + str(generated) + " 个解析内容。\n失败: " + str(errors))
            
        # 清空取消标志
        self.cancel_batch = False
    
    def cancel_batch_generation(self, progress_window):
        """取消批量生成操作"""
        self.cancel_batch = True
        
    def show_confirm(self, title, message):
        """显示确认对话框
        
        Args:
            title: 对话框标题
            message: 对话框消息
            
        Returns:
            bool: 用户是否确认
        """
        import tkinter.messagebox as messagebox
        return messagebox.askyesno(title, message)
        
    def show_info(self, title, message):
        """显示信息对话框
        
        Args:
            title: 对话框标题
            message: 对话框消息
        """
        import tkinter.messagebox as messagebox
        messagebox.showinfo(title, message)
    
    def show_cache_management(self):
        """显示缓存管理界面"""
        # 创建缓存管理窗口
        cache_window = tk.Toplevel(self.parent)
        cache_window.title("知识点解析缓存管理")
        cache_window.geometry("500x400")
        cache_window.transient(self.parent)
        cache_window.grab_set()
        
        # 设置缓存管理窗口内容
        cache_frame = ttk.Frame(cache_window, padding=20)
        cache_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(cache_frame, text="已缓存的知识点解析", 
                 font=(Config.FONT_FAMILY, Config.LABEL_FONT_SIZE, "bold")).pack(pady=10)
        
        # 统计当前缓存
        import os
        cache_dir = Config.EXPLANATIONS_DIR
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.txt')]
        
        ttk.Label(cache_frame, text="共有 " + str(len(cache_files)) + " 个缓存文件", 
                 font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE)).pack(pady=5)
        
        # 创建缓存列表框和滚动条
        list_frame = ttk.Frame(cache_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        cache_listbox = tk.Listbox(list_frame, 
                                  font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                                  bg="white", selectbackground="#4a6984")
        cache_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        cache_listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=cache_listbox.yview)
        
        # 添加缓存文件到列表框
        current_chapter_files = []
        
        for file in cache_files:
            cache_listbox.insert(tk.END, file)
            # 如果是当前章节的缓存，添加到单独列表
            if self.current_chapter and file.startswith(self.current_chapter.replace(' ', '_')):
                current_chapter_files.append(file)
        
        # 添加按钮区域
        btn_frame = ttk.Frame(cache_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 添加查看按钮
        view_btn = ttk.Button(btn_frame, text="查看选中缓存", 
                             command=lambda: self.view_cache_file(cache_listbox.get(cache_listbox.curselection()[0]) 
                                           if cache_listbox.curselection() else None))
        view_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加删除按钮
        delete_btn = ttk.Button(btn_frame, text="删除选中缓存", 
                               command=lambda: self.delete_cache_file(cache_listbox.get(cache_listbox.curselection()[0]) 
                                             if cache_listbox.curselection() else None))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加清空当前章节缓存按钮
        clear_chapter_btn = ttk.Button(btn_frame, text="清空当前章节缓存(" + str(len(current_chapter_files)) + "个)", 
                                      command=lambda: self.clear_chapter_cache(self.current_chapter, cache_window))
        clear_chapter_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加清空所有缓存按钮
        clear_all_btn = ttk.Button(btn_frame, text="清空所有缓存(" + str(len(cache_files)) + "个)", 
                                  command=lambda: self.clear_all_cache(cache_window))
        clear_all_btn.pack(side=tk.LEFT, padx=5)
    
    def view_cache_file(self, filename):
        """查看缓存文件内容
        
        Args:
            filename: 文件名
        """
        if not filename:
            self.show_error("错误", "请先选择一个缓存文件")
            return
            
        import os
        filepath = os.path.join(Config.EXPLANATIONS_DIR, filename)
        
        # 创建查看窗口
        view_window = tk.Toplevel(self.parent)
        view_window.title("查看缓存内容 - " + filename)
        view_window.geometry("600x500")
        view_window.transient(self.parent)
        
        # 设置窗口内容
        view_frame = ttk.Frame(view_window, padding=20)
        view_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本区域和滚动条
        scroll = ttk.Scrollbar(view_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(view_frame, wrap=tk.WORD, 
                           font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE),
                           bg="white")
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        text_area.config(yscrollcommand=scroll.set)
        scroll.config(command=text_area.yview)
        
        # 加载文件内容
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            text_area.insert(tk.END, content)
        except Exception as e:
            text_area.insert(tk.END, "无法读取文件内容: " + str(e))
    
    def delete_cache_file(self, filename):
        """删除缓存文件
        
        Args:
            filename: 文件名
        """
        if not filename:
            self.show_error("错误", "请先选择一个缓存文件")
            return
            
        # 询问确认
        confirm = self.show_confirm("确认删除", "确定要删除缓存文件 " + filename + " 吗？")
        if not confirm:
            return
            
        import os
        filepath = os.path.join(Config.EXPLANATIONS_DIR, filename)
        
        try:
            os.remove(filepath)
            self.show_info("删除成功", "已删除缓存文件: " + filename)
        except Exception as e:
            self.show_error("删除失败", "无法删除文件: " + str(e))
    
    def clear_chapter_cache(self, chapter, parent_window=None):
        """清空指定章节的所有缓存
        
        Args:
            chapter: 章节名称
            parent_window: 父窗口，用于关闭
        """
        if not chapter:
            self.show_error("错误", "未指定章节")
            return
            
        # 询问确认
        confirm = self.show_confirm("确认清空", "确定要清空章节「" + chapter + "」的所有缓存吗？")
        if not confirm:
            return
            
        import os
        import re
        
        # 转换章节名为安全的文件名前缀
        safe_chapter = re.sub(r'[\\/*?:"<>|]', '_', chapter)
        
        cache_dir = Config.EXPLANATIONS_DIR
        deleted = 0
        errors = 0
        
        # 删除所有匹配的文件
        for file in os.listdir(cache_dir):
            if file.startswith(safe_chapter + "_") and file.endswith('.txt'):
                try:
                    os.remove(os.path.join(cache_dir, file))
                    deleted += 1
                except:
                    errors += 1
        
        # 显示结果
        self.show_info("清空结果", "已清空章节「" + chapter + "」的缓存。\n成功: " + str(deleted) + " 个\n失败: " + str(errors) + " 个")
        
        # 如果指定了父窗口，关闭它以刷新列表
        if parent_window:
            parent_window.destroy()
            self.show_cache_management()
    
    def clear_all_cache(self, parent_window=None):
        """清空所有缓存
        
        Args:
            parent_window: 父窗口，用于关闭
        """
        # 询问确认
        confirm = self.show_confirm("确认清空所有", "确定要清空所有知识点解析缓存吗？\n这个操作无法撤销。")
        if not confirm:
            return
            
        import os
        import shutil
        
        cache_dir = Config.EXPLANATIONS_DIR
        
        try:
            # 如果目录存在，先删除整个目录再重新创建
            if os.path.exists(cache_dir):
                # 删除目录中的所有文件
                for file in os.listdir(cache_dir):
                    if file.endswith('.txt'):
                        os.remove(os.path.join(cache_dir, file))
                
            self.show_info("清空成功", "已清空所有知识点解析缓存")
        except Exception as e:
            self.show_error("清空失败", "清空缓存时出错: " + str(e))
        
        # 如果指定了父窗口，关闭它
        if parent_window:
            parent_window.destroy()
    
    def generate_current_chapter(self):
        """生成当前选中章节的所有内容解析"""
        # 检查是否有选中的章节
        if not self.current_chapter:
            self.show_error("错误", "请先选择一个章节")
            return
            
        # 确认是否生成当前章节
        confirm = self.show_confirm(
            "生成当前章节确认", 
            "确定要生成章节「" + self.current_chapter + "」的所有内容解析吗？\n\n"
            "这个过程将为该章节的所有知识点和概念生成解析，\n"
            "需要消耗API调用并可能需要一些时间。\n\n"
            "是否继续？"
        )
        
        if not confirm:
            return
            
        # 获取当前章节的内容
        contents = self.controller.get_contents(self.current_chapter)
        
        # 收集所有需要生成的内容
        all_items = []
        if "concepts" in contents and contents["concepts"]:
            all_items.extend(contents["concepts"])
        if "knowledge_points" in contents and contents["knowledge_points"]:
            all_items.extend(contents["knowledge_points"])
            
        if not all_items:
            self.show_error("错误", "当前章节没有可生成的内容")
            return
            
        # 创建进度窗口
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("生成当前章节解析中")
        progress_window.geometry("400x160")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        
        # 设置进度窗口内容
        progress_frame = ttk.Frame(progress_window, padding=20)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(progress_frame, text="正在为章节「" + self.current_chapter + "」生成解析内容", 
                 font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE)).pack(pady=10)
        
        progress_text = ttk.Label(progress_frame, text="正在准备...",
                              font=(Config.FONT_FAMILY, Config.NORMAL_FONT_SIZE))
        progress_text.pack(pady=5)
        
        progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                      length=350, mode="determinate", maximum=len(all_items))
        progress_bar.pack(pady=10)
        
        # 添加取消按钮
        self.cancel_batch = False
        cancel_button = ttk.Button(progress_frame, text="取消", 
                                 command=lambda: self.cancel_batch_generation(progress_window))
        cancel_button.pack(pady=5)
        
        # 更新UI
        progress_window.update()
        
        # 开始生成
        generated = 0
        errors = 0
        progress = 0
        
        for item in all_items:
            if self.cancel_batch:
                break
                
            # 更新进度
            progress += 1
            progress_bar["value"] = progress
            progress_text.config(text="正在处理 (" + str(progress) + "/" + str(len(all_items)) + "): " + item)
            progress_window.update()
            
            try:
                # 生成解析（强制更新）
                self.controller.get_explanation(self.current_chapter, item, force_update=True)
                generated += 1
            except Exception as e:
                print("生成「" + self.current_chapter + " - " + item + "」的解析失败: " + str(e))
                errors += 1
                
            # 短暂延迟，给UI时间刷新
            import time
            time.sleep(0.1)
        
        # 关闭进度窗口
        progress_window.destroy()
        
        # 显示完成信息
        if self.cancel_batch:
            self.show_info("操作取消", "生成已取消。\n已成功生成: " + str(generated) + "\n失败: " + str(errors))
        else:
            self.show_info("生成完成", "成功生成 " + str(generated) + " 个解析内容。\n失败: " + str(errors))
            
        # 清空取消标志
        self.cancel_batch = False 