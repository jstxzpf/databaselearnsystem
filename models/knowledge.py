"""
知识库模型
"""
import json
import os
from flask import current_app

class KnowledgeBase:
    """知识库管理类"""
    
    def __init__(self):
        self.data = None
        self.load_from_json()
    
    def load_from_json(self):
        """从JSON文件加载知识库"""
        try:
            # 尝试从应用配置获取文件路径，如果失败则使用默认路径
            try:
                file_path = current_app.config['KNOWLEDGE_BASE_FILE']
            except RuntimeError:
                # 应用上下文不可用时使用默认路径
                file_path = 'kownlgebase.json'

            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            # 安全地记录日志
            try:
                current_app.logger.info("知识库加载成功")
            except RuntimeError:
                print("知识库加载成功")

        except FileNotFoundError:
            try:
                current_app.logger.error(f"知识库文件未找到: {file_path}")
            except (RuntimeError, NameError):
                print(f"知识库文件未找到: kownlgebase.json")
            self.data = {"科目": "数据库原理", "章节": {}}
        except json.JSONDecodeError as e:
            try:
                current_app.logger.error(f"知识库JSON解析错误: {e}")
            except RuntimeError:
                print(f"知识库JSON解析错误: {e}")
            self.data = {"科目": "数据库原理", "章节": {}}
    
    def get_subject(self):
        """获取科目名称"""
        return self.data.get("科目", "数据库原理")
    
    def get_chapters(self):
        """获取所有章节"""
        chapters = self.data.get("章节", {})
        return list(chapters.keys())
    
    def get_chapter_data(self, chapter_name):
        """获取指定章节的完整数据"""
        chapters = self.data.get("章节", {})
        return chapters.get(chapter_name, {})
    
    def get_concepts(self, chapter_name):
        """获取章节的主要概念"""
        chapter_data = self.get_chapter_data(chapter_name)
        return chapter_data.get("mainConcepts", [])
    
    def get_contents(self, chapter_name):
        """获取章节的主要内容"""
        chapter_data = self.get_chapter_data(chapter_name)
        return chapter_data.get("mainContents", [])
    
    def search_knowledge(self, keyword):
        """搜索知识点"""
        results = []
        chapters = self.data.get("章节", {})
        
        for chapter_name, chapter_data in chapters.items():
            # 搜索概念
            concepts = chapter_data.get("mainConcepts", [])
            for concept in concepts:
                if keyword.lower() in concept.lower():
                    results.append({
                        'type': 'concept',
                        'chapter': chapter_name,
                        'content': concept
                    })
            
            # 搜索内容
            contents = chapter_data.get("mainContents", [])
            for content in contents:
                if keyword.lower() in content.lower():
                    results.append({
                        'type': 'content',
                        'chapter': chapter_name,
                        'content': content
                    })
        
        return results
    
    def get_all_concepts_and_contents(self, chapter_name):
        """获取章节的所有概念和内容"""
        concepts = self.get_concepts(chapter_name)
        contents = self.get_contents(chapter_name)
        
        items = []
        for concept in concepts:
            items.append({'type': 'concept', 'text': concept})
        for content in contents:
            items.append({'type': 'content', 'text': content})
        
        return items

    def get_chapter_content(self, chapter_name):
        """获取章节内容（用于批量生成）"""
        chapter_data = self.get_chapter_data(chapter_name)
        if not chapter_data:
            return None

        return {
            'mainConcepts': chapter_data.get('mainConcepts', []),
            'mainContents': chapter_data.get('mainContents', [])
        }
