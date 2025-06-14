"""
学习服务
"""
from models.knowledge import KnowledgeBase
from models.course import Course
from services.ai_service import AIService
from services.settings_service import SettingsService
from flask import current_app, session

class LearningService:
    """学习服务类"""

    def __init__(self):
        self.ai_service = AIService()
        self.settings_service = SettingsService()

    def get_current_knowledge_base(self):
        """获取当前课程的知识库"""
        try:
            # 获取当前课程
            current_course = self.settings_service.get_current_course()
            course = Course.get_course_by_name(current_course)

            if course and course.filename:
                # 创建知识库实例并加载指定文件
                knowledge_base = KnowledgeBase()
                # 临时修改文件路径
                original_file = knowledge_base.data
                try:
                    import json
                    with open(course.filename, 'r', encoding='utf-8') as f:
                        knowledge_base.data = json.load(f)
                    return knowledge_base
                except Exception as e:
                    current_app.logger.error(f"加载课程知识库失败: {e}")
                    # 回退到默认知识库
                    knowledge_base.data = original_file
                    return knowledge_base
            else:
                # 使用默认知识库
                return KnowledgeBase()
        except Exception as e:
            current_app.logger.error(f"获取知识库失败: {e}")
            return KnowledgeBase()
    
    def get_chapter_content(self, chapter_name):
        """获取章节内容"""
        try:
            knowledge_base = self.get_current_knowledge_base()
            chapter_data = knowledge_base.get_chapter_data(chapter_name)
            if not chapter_data:
                return None

            return {
                'chapter': chapter_name,
                'concepts': knowledge_base.get_concepts(chapter_name),
                'contents': knowledge_base.get_contents(chapter_name),
                'items': knowledge_base.get_all_concepts_and_contents(chapter_name)
            }
        except Exception as e:
            current_app.logger.error(f"获取章节内容失败: {str(e)}")
            return None
    
    def explain_concept(self, username, chapter, concept, concept_type):
        """解释概念"""
        try:
            current_app.logger.info(f"生成AI讲解: {chapter} - {concept}")

            # 获取当前课程名称
            current_course = self.settings_service.get_current_course()

            # 首先尝试从缓存加载
            cached_explanation = self._load_explanation_cache(chapter, concept, concept_type)
            if cached_explanation:
                current_app.logger.info(f"从缓存加载讲解: {chapter} - {concept}")
                return {
                    'success': True,
                    'explanation': cached_explanation,
                    'from_cache': True
                }

            # 缓存中没有，生成新的讲解
            try:
                explanation = self.ai_service.generate_explanation(chapter, concept, concept_type, current_course)
            except NameError as ne:
                current_app.logger.error(f"NameError in AI service: {str(ne)}")
                return {
                    'success': False,
                    'error': f"AI服务内部错误: {str(ne)}"
                }
            except SyntaxError as se:
                current_app.logger.error(f"SyntaxError in AI service: {str(se)}")
                return {
                    'success': False,
                    'error': f"AI服务语法错误: {str(se)}"
                }

            if not explanation or explanation.startswith("抱歉") or explanation.startswith("无法连接"):
                return {
                    'success': False,
                    'error': explanation or "AI服务暂时不可用"
                }

            # 验证返回的内容是否安全
            if self._contains_dangerous_content(explanation):
                current_app.logger.warning("AI返回内容包含潜在危险字符，已过滤")
                explanation = self._sanitize_content(explanation)

            # 保存到缓存
            self._save_explanation_cache(chapter, concept, concept_type, explanation)

            return {
                'success': True,
                'explanation': explanation,
                'from_cache': False
            }

        except Exception as e:
            current_app.logger.error(f"解释概念失败: {str(e)}")
            current_app.logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"服务器错误: {str(e)}"
            }
    
    def track_progress(self, username):
        """跟踪学习进度"""
        try:
            # 简化版本：返回模拟数据
            return {
                'chapters_studied': 3,
                'concepts_learned': 15,
                'recent_activity': [
                    {
                        'chapter': '第一章 数据库系统的世界(概述)',
                        'concept': '数据库',
                        'concept_type': 'concept',
                        'created_at': '2024-01-01T10:00:00'
                    }
                ]
            }

        except Exception as e:
            current_app.logger.error(f"跟踪学习进度失败: {str(e)}")
            return {'chapters_studied': 0, 'concepts_learned': 0, 'recent_activity': []}

    def batch_explain_chapter(self, username, chapter, progress_callback=None):
        """批量生成章节讲解"""
        try:
            # 获取章节的所有概念和知识点
            knowledge_base = self.get_current_knowledge_base()
            chapter_data = knowledge_base.get_chapter_content(chapter)

            if not chapter_data:
                return {
                    'success': False,
                    'error': f'章节 "{chapter}" 不存在'
                }

            # 准备批量生成的概念列表
            concepts_to_generate = []

            # 添加主要概念
            for concept in chapter_data.get('mainConcepts', []):
                concepts_to_generate.append((chapter, concept, 'concept'))

            # 添加主要知识点
            for content in chapter_data.get('mainContents', []):
                concepts_to_generate.append((chapter, content, 'content'))

            if not concepts_to_generate:
                return {
                    'success': False,
                    'error': f'章节 "{chapter}" 没有找到概念或知识点'
                }

            # 执行批量生成
            current_app.logger.info(f"开始批量生成章节 '{chapter}' 的 {len(concepts_to_generate)} 个讲解")

            def batch_progress_callback(current, total, chapter_name, concept_name, error=None):
                if progress_callback:
                    progress_callback({
                        'current': current,
                        'total': total,
                        'chapter': chapter_name,
                        'concept': concept_name,
                        'error': error,
                        'percentage': round((current / total) * 100, 1)
                    })

            # 获取当前课程名称
            current_course = self.settings_service.get_current_course()

            results = self.ai_service.batch_generate_explanations(
                concepts_to_generate,
                batch_progress_callback,
                current_course
            )

            # 保存成功生成的讲解到缓存
            success_count = 0
            error_count = 0

            for key, result in results.items():
                if result['success']:
                    self._save_explanation_cache(
                        result['chapter'],
                        result['concept'],
                        result['concept_type'],
                        result['explanation']
                    )
                    success_count += 1
                else:
                    error_count += 1

            return {
                'success': True,
                'total': len(concepts_to_generate),
                'success_count': success_count,
                'error_count': error_count,
                'results': results
            }

        except Exception as e:
            current_app.logger.error(f"批量生成章节讲解失败: {str(e)}")
            return {
                'success': False,
                'error': f"批量生成失败: {str(e)}"
            }
    
    def recommend_content(self, username):
        """推荐学习内容"""
        try:
            # 简化版本：推荐第一章
            knowledge_base = self.get_current_knowledge_base()
            all_chapters = knowledge_base.get_chapters()
            return {
                'recommended_chapter': all_chapters[0] if all_chapters else '第一章 课程概述',
                'reason': '建议从基础概念开始学习'
            }

        except Exception as e:
            current_app.logger.error(f"推荐学习内容失败: {str(e)}")
            return {
                'recommended_chapter': None,
                'reason': '推荐系统暂时不可用'
            }
    
    def search_knowledge(self, keyword):
        """搜索知识点"""
        try:
            knowledge_base = self.get_current_knowledge_base()
            return knowledge_base.search_knowledge(keyword)
        except Exception as e:
            current_app.logger.error(f"搜索知识点失败: {str(e)}")
            return []

    def _contains_dangerous_content(self, content):
        """检查内容是否包含潜在危险的字符或代码"""
        if not content:
            return False

        # 检查是否包含可能导致执行的字符串
        dangerous_patterns = [
            'eval(',
            'exec(',
            'Function(',
            '__import__',
            'compile(',
            'globals(',
            'locals(',
            'vars(',
            'dir(',
            'getattr(',
            'setattr(',
            'hasattr(',
            'delattr('
        ]

        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return True

        return False

    def _sanitize_content(self, content):
        """清理内容中的潜在危险字符"""
        if not content:
            return content

        # 移除可能的执行代码
        import re

        # 移除可能的Python代码执行
        content = re.sub(r'eval\s*\([^)]*\)', '[已过滤]', content, flags=re.IGNORECASE)
        content = re.sub(r'exec\s*\([^)]*\)', '[已过滤]', content, flags=re.IGNORECASE)
        content = re.sub(r'Function\s*\([^)]*\)', '[已过滤]', content, flags=re.IGNORECASE)

        # 移除可能的变量引用问题
        content = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\s\-_\[\]{}().,;:!?\'"`~@#$%^&*+=|\\/<>]', '', content)

        return content

    def batch_explain_all(self, username, progress_callback=None):
        """批量生成全部讲解"""
        try:
            knowledge_base = self.get_current_knowledge_base()
            all_chapters = knowledge_base.get_chapters()

            if not all_chapters:
                return {
                    'success': False,
                    'error': '没有找到任何章节'
                }

            # 统计总数
            total_concepts = 0
            all_concepts_to_generate = []

            for chapter in all_chapters:
                chapter_data = knowledge_base.get_chapter_content(chapter)
                if chapter_data:
                    # 添加主要概念
                    for concept in chapter_data.get('mainConcepts', []):
                        all_concepts_to_generate.append((chapter, concept, 'concept'))
                        total_concepts += 1

                    # 添加主要知识点
                    for content in chapter_data.get('mainContents', []):
                        all_concepts_to_generate.append((chapter, content, 'content'))
                        total_concepts += 1

            if not all_concepts_to_generate:
                return {
                    'success': False,
                    'error': '没有找到任何概念或知识点'
                }

            current_app.logger.info(f"开始批量生成全部 {total_concepts} 个讲解")

            def batch_progress_callback(current, total, chapter_name, concept_name, error=None):
                if progress_callback:
                    progress_callback({
                        'current': current,
                        'total': total,
                        'chapter': chapter_name,
                        'concept': concept_name,
                        'error': error,
                        'percentage': round((current / total) * 100, 1)
                    })

            # 获取当前课程名称
            current_course = self.settings_service.get_current_course()

            results = self.ai_service.batch_generate_explanations(
                all_concepts_to_generate,
                batch_progress_callback,
                current_course
            )

            # 保存成功生成的讲解到缓存
            success_count = 0
            error_count = 0

            for key, result in results.items():
                if result['success']:
                    self._save_explanation_cache(
                        result['chapter'],
                        result['concept'],
                        result['concept_type'],
                        result['explanation']
                    )
                    success_count += 1
                else:
                    error_count += 1

            return {
                'success': True,
                'total': total_concepts,
                'success_count': success_count,
                'error_count': error_count,
                'results': results
            }

        except Exception as e:
            current_app.logger.error(f"批量生成全部讲解失败: {str(e)}")
            return {
                'success': False,
                'error': f"批量生成失败: {str(e)}"
            }

    def regenerate_explanation(self, username, chapter, concept, concept_type):
        """重新生成讲解"""
        try:
            current_app.logger.info(f"重新生成讲解: {chapter} - {concept}")

            # 删除现有缓存
            self._delete_explanation_cache(chapter, concept, concept_type)

            # 获取当前课程名称
            current_course = self.settings_service.get_current_course()

            # 重新生成
            explanation = self.ai_service.generate_explanation(chapter, concept, concept_type, current_course)

            if not explanation or explanation.startswith("抱歉") or explanation.startswith("无法连接"):
                return {
                    'success': False,
                    'error': explanation or "AI服务暂时不可用"
                }

            # 保存新的缓存
            self._save_explanation_cache(chapter, concept, concept_type, explanation)

            return {
                'success': True,
                'explanation': explanation,
                'from_cache': False
            }

        except Exception as e:
            current_app.logger.error(f"重新生成讲解失败: {str(e)}")
            return {
                'success': False,
                'error': f"重新生成失败: {str(e)}"
            }

    def _save_explanation_cache(self, chapter, concept, concept_type, explanation):
        """保存讲解到缓存"""
        try:
            import os

            # 确保缓存目录存在
            cache_dir = 'data/explanations'
            os.makedirs(cache_dir, exist_ok=True)

            # 生成缓存文件名
            safe_filename = f"{chapter}_{concept}.txt"
            # 替换文件名中的非法字符
            safe_filename = safe_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

            cache_file = os.path.join(cache_dir, safe_filename)

            # 保存到文件
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(explanation)

            current_app.logger.info(f"讲解已缓存到: {cache_file}")

        except Exception as e:
            current_app.logger.error(f"保存讲解缓存失败: {str(e)}")

    def _load_explanation_cache(self, chapter, concept, concept_type):
        """从缓存加载讲解"""
        try:
            import os

            # 生成缓存文件名
            safe_filename = f"{chapter}_{concept}.txt"
            safe_filename = safe_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

            cache_file = os.path.join('data/explanations', safe_filename)

            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                current_app.logger.info(f"从缓存加载讲解: {cache_file}")
                return content

            return None

        except Exception as e:
            current_app.logger.error(f"加载讲解缓存失败: {str(e)}")
            return None

    def _delete_explanation_cache(self, chapter, concept, concept_type):
        """删除讲解缓存"""
        try:
            import os

            # 生成缓存文件名
            safe_filename = f"{chapter}_{concept}.txt"
            safe_filename = safe_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

            cache_file = os.path.join('data/explanations', safe_filename)

            if os.path.exists(cache_file):
                os.remove(cache_file)
                current_app.logger.info(f"删除讲解缓存: {cache_file}")

        except Exception as e:
            current_app.logger.error(f"删除讲解缓存失败: {str(e)}")
