"""
学习功能控制器 - 处理学习功能的业务逻辑
"""

import os
import re
from src.config.config import Config

class LearningController:
    """学习功能控制器类，处理学习功能的业务逻辑"""
    
    def __init__(self, knowledge_base, test_model=None, api_client=None):
        """初始化学习控制器
        
        Args:
            knowledge_base: 知识库实例
            test_model: 测试模型实例
            api_client: API客户端实例
        """
        self.api_client = api_client
        self.knowledge_base = knowledge_base
        self.test_model = test_model
        
        # 确保解析结果目录存在
        os.makedirs(Config.EXPLANATIONS_DIR, exist_ok=True)
    
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
    
    def get_chapter_concepts(self, chapter):
        """获取章节的主要概念
        
        Args:
            chapter: 章节名称
            
        Returns:
            list: 主要概念列表
        """
        if not self.knowledge_base or "章节" not in self.knowledge_base:
            return []
            
        # 从章节字典中获取主要概念
        chapters = self.knowledge_base["章节"]
        if chapter not in chapters:
            return []
            
        return chapters[chapter].get("mainConcepts", [])
    
    def get_chapter_contents(self, chapter):
        """获取章节的主要知识点
        
        Args:
            chapter: 章节名称
            
        Returns:
            list: 主要知识点列表
        """
        if not self.knowledge_base or "章节" not in self.knowledge_base:
            return []
            
        # 从章节字典中获取主要知识点
        chapters = self.knowledge_base["章节"]
        if chapter not in chapters:
            return []
            
        return chapters[chapter].get("mainContents", [])
    
    def get_contents(self, chapter):
        """获取章节的所有内容
        
        Args:
            chapter: 章节名称
            
        Returns:
            dict: 包含概念和知识点的字典
        """
        concepts = self.get_chapter_concepts(chapter)
        knowledge_points = self.get_chapter_contents(chapter)
        
        return {
            "concepts": concepts,
            "knowledge_points": knowledge_points
        }
    
    def get_explanation(self, chapter, content, force_update=False):
        """获取内容的解释
        
        Args:
            chapter: 章节名称
            content: 内容名称
            force_update: 是否强制更新缓存
            
        Returns:
            str: 内容解释
        """
        # 检查API客户端是否可用
        if not self.api_client:
            return "错误：API客户端未初始化，无法生成解析。请在设置中检查API连接。"
            
        print(f"请求解析章节「{chapter}」的内容「{content}」")
        
        # 检查是否有缓存文件
        cache_file = self._get_cache_filename(chapter, content)
        if os.path.exists(cache_file) and not force_update:
            print(f"找到缓存文件，直接加载：{cache_file}")
            explanation = self._load_explanation_from_file(cache_file)
            # 返回纯净的内容，不添加额外修饰
            return explanation
            
        # 检查是否为概念
        concepts = self.get_chapter_concepts(chapter)
        if content in concepts:
            explanation = self.get_concept_explanation(content)
        else:
            # 否则作为知识点
            explanation = self.get_content_explanation(content)
            
        # 保存解析结果到文件
        self._save_explanation_to_file(cache_file, explanation)
        # 返回纯净的内容，不添加额外修饰
        return explanation
    
    def _get_cache_filename(self, chapter, content):
        """获取缓存文件名
        
        Args:
            chapter: 章节名称
            content: 内容名称
            
        Returns:
            str: 缓存文件路径
        """
        # 将章节和内容名称转换为合法的文件名
        safe_chapter = re.sub(r'[\\/*?:"<>|]', '_', chapter)
        safe_content = re.sub(r'[\\/*?:"<>|]', '_', content)
        
        # 构建文件名
        filename = f"{safe_chapter}_{safe_content}.txt"
        return os.path.join(Config.EXPLANATIONS_DIR, filename)
    
    def _save_explanation_to_file(self, filepath, explanation):
        """保存解析结果到文件
        
        Args:
            filepath: 文件路径
            explanation: 解析内容
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(explanation)
            print(f"解析结果已保存到：{filepath}")
        except Exception as e:
            print(f"保存解析结果失败: {str(e)}")
            
    def _load_explanation_from_file(self, filepath):
        """从文件加载解析结果
        
        Args:
            filepath: 文件路径
            
        Returns:
            str: 解析内容
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"加载解析结果失败: {str(e)}")
            return f"加载缓存内容失败: {str(e)}"
    
    def get_concept_explanation(self, concept_name):
        """获取概念解释"""
        try:
            # 检查是否为概念
            concepts = []
            for chapter in self.get_chapters():
                concepts.extend(self.get_chapter_concepts(chapter))
                
            if concept_name not in concepts:
                return f"错误：'{concept_name}'不是一个已知的概念"
                
            # 构建提示词
            prompt = f"""你是数据库教学AI助手，请详细讲解数据库领域中的概念："{concept_name}"。
要求：
1. 用生动形象的语言和贴近生活的例子进行解释
2. 给出准确完整的定义
3. 解释概念的重要性和应用场景
4. 提供具体示例帮助理解
5. 如果适用，用mermaid图表描述概念的关系或流程

请使用Markdown格式进行排版，例如使用# ## ###表示标题层级，使用**文本**表示加粗，*文本*表示斜体，`代码`表示代码，```代码块```表示代码块等。

关于Mermaid图表，必须严格按照如下格式添加，并确保语法完全正确:

```mermaid
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
```

请注意以下几点：
1. 第一行必须是 ```mermaid (不能有多余空格)
2. 第二行必须是 graph TD 或其他正确的图表类型声明
3. 后续行必须使用正确的Mermaid语法
4. 所有括号必须使用英文字符，如[]()，不要使用中文字符如（）
5. 箭头必须使用英文符号，如-->而非中文箭头
6. 最后一行必须是 ``` 表示代码块结束

请用通俗易懂的语言解释，适合大学生学习数据库课程。"""

            # 获取解释
            return self.api_client.get_completion(prompt)
        except Exception as e:
            print(f"获取概念解释出错: {e}")
            return f"获取概念解释出错: {str(e)}"

    def get_content_explanation(self, content_name):
        """获取知识点解释"""
        try:
            # 检查是否为知识点
            knowledge_points = []
            for chapter in self.get_chapters():
                knowledge_points.extend(self.get_chapter_contents(chapter))
                
            if content_name not in knowledge_points:
                return f"错误：'{content_name}'不是一个已知的知识点"
                
            # 构建提示词
            prompt = f"""你是数据库教学AI助手，请详细讲解数据库领域中的知识点："{content_name}"。
要求：
1. 用生动形象的语言和贴近生活的例子进行解释
2. 给出完整的定义和原理
3. 解释在数据库系统中的作用
4. 提供实际应用场景和示例
5. 如果适用，提供相关SQL代码或实现方法
6. 如果适用，用mermaid图表描述流程或关系

请使用Markdown格式进行排版，例如：
- 使用# ## ###表示标题层级
- 使用**文本**表示加粗，*文本*表示斜体
- 代码应放在```sql```代码块中
- 使用>引用重要概念
- 使用- 或1. 2. 3.创建列表

关于Mermaid图表，必须严格按照如下格式添加，并确保语法完全正确:

流程图示例:
```mermaid
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
```

时序图示例:
```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
```

请注意以下几点：
1. 第一行必须是 ```mermaid (不能有多余空格或换行)
2. 第二行必须是有效的图表类型声明(graph TD, sequenceDiagram等)
3. 所有括号必须使用英文字符，如[]()，不要使用中文字符如（）
4. 所有箭头、符号必须使用英文符号
5. 最后一行必须是 ``` 表示代码块结束
6. 图表内的文本应简洁明了，避免过长的描述

请用通俗易懂的语言解释，适合大学生学习数据库课程。"""

            # 获取解释
            return self.api_client.get_completion(prompt)
        except Exception as e:
            print(f"获取知识点解释出错: {e}")
            return f"获取知识点解释出错: {str(e)}" 