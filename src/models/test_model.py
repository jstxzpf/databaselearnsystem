"""
考试模型数据类 - 表示考试模型的数据结构
"""

class TestModel:
    """考试模型数据类，表示考试模型的数据结构"""
    
    def __init__(self, data=None):
        """初始化考试模型
        
        Args:
            data: 考试模型数据字典
        """
        self.data = data or {}
        self.exam_info = self.data.get("考试信息", {})
        self.exam_name = self.exam_info.get("考试名称", "")
        self.duration = self.exam_info.get("总时长", "")
        self.question_types = self.exam_info.get("题型列表", [])
    
    def get_exam_name(self):
        """获取考试名称
        
        Returns:
            str: 考试名称
        """
        return self.exam_name
    
    def get_duration(self):
        """获取考试时长
        
        Returns:
            str: 考试时长
        """
        return self.duration
    
    def get_question_types(self):
        """获取所有题型
        
        Returns:
            list: 题型列表
        """
        return self.question_types
    
    def get_question_type_info(self, index):
        """获取特定题型的信息
        
        Args:
            index: 题型索引
            
        Returns:
            dict: 题型信息字典
        """
        if 0 <= index < len(self.question_types):
            return self.question_types[index]
        return {}
    
    def is_empty(self):
        """检查考试模型是否为空
        
        Returns:
            bool: 如果考试模型为空返回True，否则返回False
        """
        return not bool(self.data) 