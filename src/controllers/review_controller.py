"""
复习功能控制器 - 处理试卷复习功能的业务逻辑
"""

from src.utils.data_loader import DataLoader

class ReviewController:
    """复习功能控制器类，处理试卷复习功能的业务逻辑"""
    
    def __init__(self, knowledge_base, api_client=None):
        """初始化复习控制器
        
        Args:
            knowledge_base: 知识库实例
            api_client: API客户端实例
        """
        self.api_client = api_client
        self.knowledge_base = knowledge_base
    
    def load_exam(self, file_path):
        """加载试卷文件
        
        Args:
            file_path: 试卷文件路径
            
        Returns:
            tuple: (成功标志, 内容/错误消息)
        """
        return DataLoader.load_text_file(file_path)
    
    def review_exam(self, exam_content):
        """复习试卷内容，生成复习资料
        
        Args:
            exam_content: 试卷内容
            
        Returns:
            str: 复习材料
            
        Raises:
            Exception: 当生成复习材料失败时抛出异常
        """
        if not self.api_client:
            raise Exception("未初始化API客户端，无法生成复习材料")
            
        prompt = f"""作为数据库教学AI助手，请针对以下试卷内容生成复习资料。
试卷内容：
{exam_content}

请提供以下内容：
1. 试卷中涉及的主要知识点解析
2. 每道题目的详细答案解释及思路分析
3. 相关概念的补充说明和拓展知识
4. 常见易错点和避坑指南
5. 复习建议和学习方法指导

请给出全面、专业、易于理解的复习材料，帮助学生掌握相关知识点。"""
        
        return self.api_client.get_completion(prompt) 