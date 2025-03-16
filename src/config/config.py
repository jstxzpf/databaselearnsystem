"""
配置模块 - 存储应用程序的全局配置
"""

class Config:
    """配置类，存储应用程序的全局配置"""
    
    # 应用程序设置
    APP_TITLE = "数据库学习系统"
    APP_VERSION = "1.0.0"
    APP_WIDTH = 1200
    APP_HEIGHT = 800
    
    # API设置
    API_URL = "http://localhost:8000/api"
    API_TIMEOUT = 30  # 秒
    
    # 文件路径
    DATA_DIR = "data"
    LOG_DIR = "logs"
    TEMP_DIR = "temp"
    EXPLANATIONS_DIR = "data/explanations"  # 存储AI解析结果的目录
    
    # UI设置
    FONT_FAMILY = "Microsoft YaHei"  # 微软雅黑
    NORMAL_FONT_SIZE = 10
    LABEL_FONT_SIZE = 12
    TITLE_FONT_SIZE = 14
    SMALL_FONT_SIZE = 9
    
    # 边距设置
    FRAME_PADDING = 10
    WIDGET_PADDING = 5
    
    # 标签页标题
    LEARNING_TAB_TITLE = "学习"
    EXAM_TAB_TITLE = "考试"
    REVIEW_TAB_TITLE = "复习"
    SETTINGS_TAB_TITLE = "设置"
    
    # 学习视图标签
    LEARNING_CHAPTER_LABEL = "章节"
    LEARNING_CONTENT_LABEL = "内容"
    LEARNING_EXPLANATION_LABEL = "AI解析"
    
    # 考试视图标签
    EXAM_CHAPTER_LABEL = "章节选择"
    EXAM_CONTENT_LABEL = "考试内容"
    
    # 复习视图标签
    REVIEW_CONTENT_LABEL = "考试内容"
    REVIEW_RESULT_LABEL = "复习结果"
    
    # 消息文本
    API_ERROR_MSG = "API连接失败，请检查网络连接或API服务状态"
    DATA_LOAD_ERROR_MSG = "加载数据失败，请检查数据文件是否存在且格式正确"
    DATA_LOAD_SUCCESS_MSG = "数据加载成功"
    
    # 空白状态提示
    EMPTY_CHAPTER_HINT = "没有章节数据"
    EMPTY_CONTENT_HINT = "   (无概念数据)"
    EMPTY_KNOWLEDGE_HINT = "   (无知识点数据)"
    EMPTY_EXPLANATION_HINT = "请双击左侧列表中的内容项目以查看AI解析"
    EMPTY_EXAM_HINT = "请从左侧选择一个或多个章节，然后点击生成考试按钮获取试卷。\n\n生成的试卷将保存为文本文件，可用于打印或复习。"
    EMPTY_REVIEW_EXAM_HINT = "请点击\"导入试卷\"按钮以导入需要复习的试卷。\n您可以导入之前生成的考试试卷文件。"
    EMPTY_REVIEW_RESULT_HINT = "导入试卷后，点击\"开始复习\"按钮生成复习内容。\n复习内容将包含知识点解析和答案提示。"
    
    # 按钮颜色
    BUTTON_GENERATE_BG = "#4CAF50"  # 绿色
    BUTTON_GENERATE_FG = "white"
    BUTTON_IMPORT_BG = "#2196F3"    # 蓝色
    BUTTON_IMPORT_FG = "white"
    BUTTON_REVIEW_BG = "#FF9800"    # 橙色
    BUTTON_REVIEW_FG = "white"
    
    # Ollama API 设置
    MODEL_NAME = "qwen2.5:14b"
    
    # 文件路径
    KNOWLEDGE_BASE_FILE = "kownlgebase.json"
    TEST_MODEL_FILE = "testmodel.json"
    
    # UI设置
    SUBJECT_LABEL_X = 10         # 科目标签X坐标
    SUBJECT_LABEL_Y = 10         # 科目标签Y坐标
    
    # 标签文本
    CHAPTER_LABEL = "章节列表"
    CONTENT_LABEL = "主要概念和知识点"
    AI_EXPLANATION_LABEL = "AI讲解"
    EXAM_CHAPTER_LABEL = "选择考试章节"
    EXAM_CONTENT_LABEL = "试卷内容"
    REVIEW_RESULT_LABEL = "审批结果"
    
    # 提示信息
    MAIN_CONCEPTS_SEPARATOR = "--- 主要概念 ---"
    MAIN_CONTENTS_SEPARATOR = "--- 主要知识点 ---"
    EMPTY_REVIEW_HINT = "请点击\"导入试卷\"按钮导入要审批的试卷..."
    
    # 布局设置
    WINDOW_PADDING = 10          # 窗口内边距
    NOTEBOOK_TOP_PADDING = 40    # 标签页顶部内边距，解决标签页显示不全问题
    FRAME_PADDING = 10           # 框架内边距
    WIDGET_PADDING = 5           # 控件内边距
    SUBJECT_LABEL_X = 10         # 科目标签X坐标
    SUBJECT_LABEL_Y = 10         # 科目标签Y坐标
    
    # 标签文本
    LEARNING_TAB_TITLE = "学习"
    EXAM_TAB_TITLE = "考试"
    REVIEW_TAB_TITLE = "审批试卷"
    CHAPTER_LABEL = "章节列表"
    CONTENT_LABEL = "主要概念和知识点"
    AI_EXPLANATION_LABEL = "AI讲解"
    EXAM_CHAPTER_LABEL = "选择考试章节"
    EXAM_CONTENT_LABEL = "试卷内容"
    REVIEW_RESULT_LABEL = "审批结果"
    
    # 提示信息
    MAIN_CONCEPTS_SEPARATOR = "--- 主要概念 ---"
    MAIN_CONTENTS_SEPARATOR = "--- 主要知识点 ---"
    EMPTY_CHAPTER_HINT = "请选择左侧章节查看内容..."
    EMPTY_CONTENT_HINT = "请双击知识点或概念查看AI讲解..."
    EMPTY_EXAM_HINT = "请选择要考试的章节，然后点击'生成考试'按钮..."
    EMPTY_REVIEW_HINT = "请点击'导入试卷'按钮导入要审批的试卷..."
    
    # 按钮颜色
    BUTTON_GENERATE_BG = "#4CAF50"   # 生成考试按钮背景色 (绿色)
    BUTTON_GENERATE_FG = "white"     # 生成考试按钮文字颜色
    BUTTON_IMPORT_BG = "#2196F3"     # 导入试卷按钮背景色 (蓝色)
    BUTTON_IMPORT_FG = "white"       # 导入试卷按钮文字颜色
    BUTTON_REVIEW_BG = "#FF9800"     # 审批试卷按钮背景色 (橙色)
    BUTTON_REVIEW_FG = "white"       # 审批试卷按钮文字颜色 