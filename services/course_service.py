"""
课程服务
"""
import json
from models.course import Course
from services.ai_service import AIService
from flask import current_app

class CourseService:
    """课程服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def get_all_courses(self):
        """获取所有课程"""
        try:
            return Course.get_all_courses()
        except Exception as e:
            current_app.logger.error(f"获取课程列表失败: {e}")
            return []
    
    def get_course_by_name(self, name):
        """根据名称获取课程"""
        try:
            return Course.get_course_by_name(name)
        except Exception as e:
            current_app.logger.error(f"获取课程失败: {e}")
            return None
    
    def create_course_with_ai(self, course_name, description=""):
        """使用AI创建课程知识库"""
        try:
            current_app.logger.info(f"开始为课程 '{course_name}' 生成知识库")
            
            # 构建AI提示词
            prompt = self._build_knowledge_generation_prompt(course_name, description)
            
            # 调用AI生成知识库
            ai_response = self.ai_service._make_request(prompt, max_tokens=4000)
            
            if not ai_response or ai_response.startswith("抱歉") or ai_response.startswith("无法连接"):
                return {
                    'success': False,
                    'error': ai_response or "AI服务暂时不可用"
                }
            
            # 解析AI响应，提取JSON
            knowledge_data = self._parse_ai_response(ai_response, course_name)
            
            if not knowledge_data:
                return {
                    'success': False,
                    'error': "AI生成的知识库格式无效"
                }
            
            # 创建课程
            course = Course.create_course(course_name, description, knowledge_data)
            
            return {
                'success': True,
                'course': course.to_dict(),
                'knowledge_data': knowledge_data
            }
            
        except Exception as e:
            current_app.logger.error(f"创建课程失败: {e}")
            return {
                'success': False,
                'error': f"创建课程失败: {str(e)}"
            }
    
    def _build_knowledge_generation_prompt(self, course_name, description):
        """构建知识库生成提示词"""
        prompt = f"""
作为一名资深的教育专家和课程设计师，请为"{course_name}"课程生成完整的知识库结构。

课程描述：{description if description else '无'}

请严格按照以下JSON格式生成知识库，确保结构完全一致：

{{
  "科目": "{course_name}",
  "章节": {{
    "第一章 课程名称": {{
      "mainConcepts": [
        "概念1",
        "概念2",
        "概念3"
      ],
      "mainContents": [
        "知识点1",
        "知识点2", 
        "知识点3"
      ]
    }},
    "第二章 课程名称": {{
      "mainConcepts": [
        "概念1",
        "概念2"
      ],
      "mainContents": [
        "知识点1",
        "知识点2"
      ]
    }}
  }}
}}

要求：
1. 生成8-12个章节，章节名称要具体且符合该课程的教学体系
2. 每个章节包含3-5个主要概念(mainConcepts)
3. 每个章节包含3-6个主要知识点(mainContents)
4. 概念应该是理论性的核心概念
5. 知识点应该是具体的技能或应用点
6. 内容要准确、全面、符合本科教学水平
7. 必须返回有效的JSON格式，不要包含任何其他文字说明

注意：生成的概念和知识点将用于AI讲解，AI会为每个概念和知识点生成包含以下元素的详细内容：
- 文字说明：详细的理论解释
- 对比表格：特点、优缺点、适用场景等的表格对比
- 流程图：使用Mermaid语法的操作流程或原理图
- 实例演示：具体的应用案例
因此请确保概念和知识点的命名清晰、具体，便于生成丰富的多媒体教学内容。

请直接返回JSON内容：
"""
        return prompt
    
    def _parse_ai_response(self, ai_response, course_name):
        """解析AI响应，提取JSON数据"""
        try:
            # 尝试直接解析JSON
            if ai_response.strip().startswith('{'):
                return json.loads(ai_response.strip())
            
            # 查找JSON块
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # 如果找不到有效JSON，返回基础结构
            current_app.logger.warning("AI响应中未找到有效JSON，使用基础结构")
            return {
                "科目": course_name,
                "章节": {
                    f"第一章 {course_name}概述": {
                        "mainConcepts": [
                            "基本概念",
                            "发展历史",
                            "应用领域"
                        ],
                        "mainContents": [
                            "基础知识",
                            "核心原理",
                            "实际应用"
                        ]
                    }
                }
            }
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON解析失败: {e}")
            current_app.logger.error(f"AI响应内容: {ai_response[:500]}...")
            return None
        except Exception as e:
            current_app.logger.error(f"解析AI响应失败: {e}")
            return None
    
    def delete_course(self, course_name):
        """删除课程"""
        try:
            Course.delete_course(course_name)
            return {
                'success': True,
                'message': f'课程 "{course_name}" 已删除'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_course_knowledge_base(self, course_name):
        """获取课程知识库"""
        try:
            course = Course.get_course_by_name(course_name)
            if not course:
                return None
            
            return course.load_knowledge_base()
        except Exception as e:
            current_app.logger.error(f"获取课程知识库失败: {e}")
            return None
    
    def validate_course_data(self, knowledge_data):
        """验证课程数据格式"""
        try:
            if not isinstance(knowledge_data, dict):
                return False
            
            if '科目' not in knowledge_data or '章节' not in knowledge_data:
                return False
            
            chapters = knowledge_data['章节']
            if not isinstance(chapters, dict):
                return False
            
            for chapter_name, chapter_data in chapters.items():
                if not isinstance(chapter_data, dict):
                    return False
                
                if 'mainConcepts' not in chapter_data or 'mainContents' not in chapter_data:
                    return False
                
                if not isinstance(chapter_data['mainConcepts'], list) or \
                   not isinstance(chapter_data['mainContents'], list):
                    return False
            
            return True
        except Exception:
            return False
