"""
知识库数据模型 - 表示知识库数据结构
"""

class KnowledgeBase:
    """知识库数据模型类，表示知识库数据结构"""
    
    def __init__(self, data=None):
        """初始化知识库模型
        
        Args:
            data: 知识库数据字典
        """
        self.data = data or {}
        self.subject = self.data.get("科目", "")
        self.chapters = self.data.get("章节", {})
    
    def get_subject(self):
        """获取科目名称
        
        Returns:
            str: 科目名称
        """
        return self.subject
    
    def get_chapters(self):
        """获取所有章节
        
        Returns:
            list: 章节名称列表
        """
        return list(self.chapters.keys())
    
    def get_chapter_concepts(self, chapter):
        """获取章节的主要概念
        
        Args:
            chapter: 章节名称
            
        Returns:
            list: 主要概念列表
        """
        if chapter in self.chapters:
            return self.chapters[chapter].get("mainConcepts", [])
        return []
    
    def get_chapter_contents(self, chapter):
        """获取章节的主要知识点
        
        Args:
            chapter: 章节名称
            
        Returns:
            list: 主要知识点列表
        """
        if chapter in self.chapters:
            return self.chapters[chapter].get("mainContents", [])
        return []
    
    def is_empty(self):
        """检查知识库是否为空
        
        Returns:
            bool: 如果知识库为空返回True，否则返回False
        """
        return not bool(self.data) 