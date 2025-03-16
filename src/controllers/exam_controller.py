"""
考试功能控制器 - 处理考试功能的业务逻辑
"""

from src.utils.data_loader import DataLoader

class ExamController:
    """考试功能控制器类，处理考试功能的业务逻辑"""
    
    def __init__(self, knowledge_base, test_model, api_client=None):
        """初始化考试控制器
        
        Args:
            knowledge_base: 知识库实例
            test_model: 考试模型实例
            api_client: API客户端实例
        """
        self.api_client = api_client
        self.knowledge_base = knowledge_base
        self.test_model = test_model
    
    def get_chapters(self):
        """获取所有章节
        
        Returns:
            list: 章节名称列表
        """
        if not self.knowledge_base:
            return []
            
        # 处理知识库中的章节结构
        if "章节" in self.knowledge_base:
            return list(self.knowledge_base["章节"].keys())
        return []
    
    def get_exam_info(self):
        """获取考试信息
        
        Returns:
            tuple: (考试名称, 考试时长)
        """
        if not self.test_model:
            return "未知考试", "未知时长"
            
        exam_info = self.test_model.get("考试信息", {})
        exam_name = exam_info.get("考试名称", "数据库系统考试")
        duration = exam_info.get("总时长", "120分钟")
        
        return exam_name, duration
    
    def get_question_types(self):
        """获取题型列表
        
        Returns:
            list: 题型信息列表
        """
        if not self.test_model:
            return []
            
        exam_info = self.test_model.get("考试信息", {})
        return exam_info.get("题型列表", [])
    
    def generate_exam(self, selected_chapters, output_file):
        """生成考试试卷
        
        Args:
            selected_chapters: 选中的章节列表
            output_file: 输出文件路径
            
        Returns:
            tuple: (成功标志, 错误消息)
            
        Raises:
            Exception: 当生成试卷失败时抛出异常
        """
        if not self.api_client:
            raise Exception("未初始化API客户端，无法生成试卷")
            
        # 准备试卷头部
        exam_name, duration = self.get_exam_info()
        
        exam_content = f"{exam_name}\n"
        exam_content += f"考试时长: {duration}\n"
        exam_content += f"考试范围: {', '.join(selected_chapters)}\n\n"
        
        # 生成各个题型
        question_types = self.get_question_types()
        if not question_types:
            raise Exception("未找到题型信息，无法生成试卷")
            
        total_questions = 0
        for question_type in question_types:
            type_name = question_type.get("题型名称", "")
            question_count = question_type.get("题量", 0)
            total_score = question_type.get("总分", 0)
            
            # 构建提示
            prompt = f"""作为数据库教学AI助手，请为数据库系统考试生成{question_count}道{type_name}。
考试范围限定在以下章节: {', '.join(selected_chapters)}
考查重点: {question_type.get('考查重点', '基础知识')}
题型要求:
1. 每题请提供标准答案
2. 题目难度适中，符合大学本科水平
3. 题目内容紧扣章节知识点
4. 格式要求: 先列出所有题目，然后单独列出参考答案

请生成完整且符合要求的{type_name}。"""
            
            try:
                # 获取AI生成的内容
                question_content = self.api_client.get_completion(prompt)
                
                # 添加到试卷
                exam_content += f"\n{total_questions + 1}. {type_name} ({total_score}分)\n"
                exam_content += f"{question_content}\n"
                
                total_questions += 1
            except Exception as e:
                raise Exception(f"生成{type_name}失败: {str(e)}")
        
        # 保存到文件
        success, error = DataLoader.save_to_file(output_file, exam_content)
        if not success:
            raise Exception(f"保存试卷失败: {error}")
        
        return success, None 