"""
审批服务
"""
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from models.records import ReviewRecord
from models.user import User
from models.knowledge import KnowledgeBase
from services.ai_service import AIService
from app import db
from flask import current_app

class ReviewService:
    """审批服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.knowledge_base = KnowledgeBase()
    
    def upload_exam_file(self, username, file):
        """上传试卷文件"""
        try:
            if not file or file.filename == '':
                return {
                    'success': False,
                    'error': '没有选择文件'
                }
            
            # 检查文件类型
            if not self._allowed_file(file.filename):
                return {
                    'success': False,
                    'error': '不支持的文件类型，请上传txt、pdf、doc或docx文件'
                }
            
            # 获取用户
            user = User.get_or_create(username)
            
            # 保存文件
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            
            file.save(file_path)
            
            # 创建审批记录
            review_record = ReviewRecord(
                user_id=user.id,
                original_filename=file.filename,
                file_path=file_path,
                status='uploaded'
            )
            
            db.session.add(review_record)
            db.session.commit()
            
            return {
                'success': True,
                'record_id': review_record.id,
                'filename': filename,
                'original_filename': file.filename
            }
            
        except Exception as e:
            current_app.logger.error(f"上传文件失败: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f"上传失败: {str(e)}"
            }
    
    def _allowed_file(self, filename):
        """检查文件类型是否允许"""
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    def parse_exam_file(self, record_id):
        """解析试卷文件"""
        try:
            review_record = ReviewRecord.query.get(record_id)
            if not review_record:
                return {
                    'success': False,
                    'error': '记录不存在'
                }
            
            file_path = review_record.file_path
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': '文件不存在'
                }
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            
            # 简单解析试卷内容
            parsed_content = self._parse_exam_content(content)
            
            return {
                'success': True,
                'content': content,
                'parsed_content': parsed_content
            }
            
        except Exception as e:
            current_app.logger.error(f"解析试卷文件失败: {str(e)}")
            return {
                'success': False,
                'error': f"解析失败: {str(e)}"
            }
    
    def _parse_exam_content(self, content):
        """解析试卷内容"""
        lines = content.strip().split('\n')
        questions = []
        current_question = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是题目开始（简单的数字匹配）
            if line and (line[0].isdigit() or '题' in line[:10]):
                if current_question:
                    questions.append(current_question.strip())
                current_question = line
            else:
                if current_question:
                    current_question += "\n" + line
        
        # 添加最后一个题目
        if current_question:
            questions.append(current_question.strip())
        
        return {
            'total_questions': len(questions),
            'questions': questions[:10]  # 只返回前10个题目作为预览
        }
    
    def review_exam(self, record_id):
        """审批试卷"""
        try:
            review_record = ReviewRecord.query.get(record_id)
            if not review_record:
                return {
                    'success': False,
                    'error': '记录不存在'
                }
            
            # 解析试卷内容
            parse_result = self.parse_exam_file(record_id)
            if not parse_result['success']:
                return parse_result
            
            content = parse_result['content']
            
            # 获取相关知识背景
            knowledge_context = self._get_knowledge_context()
            
            # 调用AI进行批改
            current_app.logger.info("开始AI批改试卷")
            review_result = self.ai_service.review_answers(content, knowledge_context)
            
            if not review_result or review_result.startswith("抱歉"):
                return {
                    'success': False,
                    'error': review_result or "AI批改服务暂时不可用"
                }
            
            # 分析薄弱环节
            weak_points = self._analyze_weak_points(review_result)
            
            # 生成学习建议
            suggestions = self.ai_service.get_learning_advice(weak_points, knowledge_context)
            
            # 更新审批记录
            review_record.review_result = review_result
            review_record.suggestions = suggestions
            review_record.status = 'reviewed'
            
            # 简单的分数提取（从AI回复中）
            score = self._extract_score(review_result)
            if score:
                review_record.score = score
            
            db.session.commit()
            
            return {
                'success': True,
                'review_result': review_result,
                'suggestions': suggestions,
                'score': score,
                'weak_points': weak_points
            }
            
        except Exception as e:
            current_app.logger.error(f"审批试卷失败: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f"审批失败: {str(e)}"
            }
    
    def _get_knowledge_context(self):
        """获取知识背景"""
        try:
            chapters = self.knowledge_base.get_chapters()
            context_parts = []
            
            for chapter in chapters[:3]:  # 只取前3章作为背景
                concepts = self.knowledge_base.get_concepts(chapter)
                contents = self.knowledge_base.get_contents(chapter)
                context_parts.append(f"{chapter}: {', '.join(concepts[:5])}")
            
            return "; ".join(context_parts)
        except:
            return "数据库原理相关知识"
    
    def _analyze_weak_points(self, review_result):
        """分析薄弱环节"""
        # 简单的关键词分析
        weak_keywords = ['错误', '不正确', '不准确', '需要改进', '薄弱', '不足']
        weak_points = []
        
        lines = review_result.split('\n')
        for line in lines:
            for keyword in weak_keywords:
                if keyword in line:
                    weak_points.append(line.strip())
                    break
        
        return weak_points[:5]  # 最多返回5个薄弱点
    
    def _extract_score(self, review_result):
        """从批改结果中提取分数"""
        import re
        
        # 查找分数模式
        score_patterns = [
            r'总分[：:]\s*(\d+)',
            r'得分[：:]\s*(\d+)',
            r'分数[：:]\s*(\d+)',
            r'(\d+)\s*分'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, review_result)
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def get_review_history(self, username):
        """获取审批历史"""
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return []
            
            review_records = ReviewRecord.query.filter_by(user_id=user.id)\
                .order_by(ReviewRecord.created_at.desc()).all()
            
            return [record.to_dict() for record in review_records]
            
        except Exception as e:
            current_app.logger.error(f"获取审批历史失败: {str(e)}")
            return []
