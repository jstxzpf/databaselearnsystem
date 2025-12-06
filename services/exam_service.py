"""
考试服务
"""
import json
import os
from datetime import datetime
from models.exam import ExamModel
from models.records import ExamRecord
from models.user import User
from services.ai_service import AIService
from extensions import db
from flask import current_app

class ExamService:
    """考试服务类"""
    
    def __init__(self):
        self.exam_model = ExamModel()
        self.ai_service = AIService()
    
    def create_exam(self, username, selected_chapters, selected_types=None):
        """创建考试"""
        try:
            # 确保在应用上下文中运行
            from flask import current_app

            # 获取或创建用户（使用简化的User模型）
            from models.user import User
            user = User.get_or_create(username)

            # 生成试卷
            exam_paper = self.exam_model.generate_exam_paper(selected_chapters, selected_types)

            # 保存考试记录（使用原生SQL）
            import sqlite3
            import os

            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')
            # 获取当前课程名称
            from services.settings_service import SettingsService
            settings_service = SettingsService()
            current_course = settings_service.get_current_course()
            exam_name = f"{current_course}考试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # 确保exam_records表存在
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exam_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        exam_id VARCHAR(50) NOT NULL,
                        exam_name VARCHAR(100) NOT NULL,
                        chapters TEXT NOT NULL,
                        questions TEXT,
                        score INTEGER,
                        status VARCHAR(20) DEFAULT 'generated',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 插入考试记录
                cursor.execute('''
                    INSERT INTO exam_records (user_id, exam_id, exam_name, chapters, questions, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user.id,
                    exam_paper['id'],
                    exam_name,
                    json.dumps(selected_chapters, ensure_ascii=False),
                    json.dumps(exam_paper, ensure_ascii=False),
                    'generated'
                ))

                exam_record_id = cursor.lastrowid
                conn.commit()

            return {
                'success': True,
                'exam_id': exam_paper['id'],
                'exam_record_id': exam_record_id,
                'exam_paper': exam_paper
            }

        except Exception as e:
            current_app.logger.error(f"创建考试失败: {str(e)}")
            try:
                db.session.rollback()
            except:
                pass
            return {
                'success': False,
                'error': f"创建考试失败: {str(e)}"
            }
    
    def generate_questions(self, exam_id, use_ai=True):
        """生成题目"""
        try:
            # 获取考试记录（使用原生SQL）
            import sqlite3
            import os

            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT questions, chapters FROM exam_records WHERE exam_id = ?",
                    (exam_id,)
                )
                result = cursor.fetchone()

                if not result:
                    return {
                        'success': False,
                        'error': '考试记录不存在'
                    }

                exam_paper = json.loads(result[0])
                chapters = json.loads(result[1])
            
                if not use_ai:
                    # 不使用AI，返回基础试卷格式
                    formatted_paper = self.exam_model.format_exam_paper(exam_paper)
                    return {
                        'success': True,
                        'formatted_paper': formatted_paper,
                        'exam_paper': exam_paper
                    }

                # 使用AI生成题目
                generated_questions = []

                # 获取当前课程名称
                from services.settings_service import SettingsService
                settings_service = SettingsService()
                current_course = settings_service.get_current_course()

                for section in exam_paper['questions']:
                    current_app.logger.info(f"生成{section['type_name']}题目")

                    questions_text = self.ai_service.generate_questions(
                        section['type_name'],
                        chapters,
                        section['count'],
                        current_course
                    )

                    if questions_text and not questions_text.startswith("抱歉"):
                        # 简单解析生成的题目
                        questions = self._parse_generated_questions(questions_text)
                        generated_questions.append(questions)
                    else:
                        # AI生成失败，使用占位符
                        placeholder_questions = [f"[{section['type_name']}题目 {i+1}]"
                                               for i in range(section['count'])]
                        generated_questions.append(placeholder_questions)

                # 格式化完整试卷
                formatted_paper = self.exam_model.format_exam_paper(exam_paper, generated_questions)

                # 更新考试记录
                exam_paper['generated_questions'] = generated_questions
                cursor.execute(
                    "UPDATE exam_records SET questions = ? WHERE exam_id = ?",
                    (json.dumps(exam_paper, ensure_ascii=False), exam_id)
                )
                conn.commit()
            
            return {
                'success': True,
                'formatted_paper': formatted_paper,
                'exam_paper': exam_paper
            }
            
        except Exception as e:
            current_app.logger.error(f"生成题目失败: {str(e)}")
            return {
                'success': False,
                'error': f"生成题目失败: {str(e)}"
            }
    
    def _parse_generated_questions(self, questions_text):
        """解析AI生成的题目"""
        try:
            # 尝试解析JSON
            import json
            import re
            
            # 清理可能存在的代码块标记
            cleaned_text = re.sub(r'```json\s*', '', questions_text)
            cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
            cleaned_text = cleaned_text.strip()
            
            questions = json.loads(cleaned_text)
            if isinstance(questions, list):
                return questions
            
            # 如果不是列表，可能解析错误，回退到普通文本处理
            current_app.logger.warning(f"解析结果不是列表: {type(questions)}")
        except Exception as e:
            current_app.logger.warning(f"JSON解析失败，回退到文本模式: {e}")
        
        # 回退逻辑：普通文本解析
        questions = []
        lines = questions_text.strip().split('\n')
        current_question = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_question:
                    questions.append(current_question.strip())
                    current_question = ""
                continue
            
            # 检查是否是新题目的开始（以数字开头）
            if line and (line[0].isdigit() or line.startswith('第')):
                if current_question:
                    questions.append(current_question.strip())
                current_question = line
            else:
                current_question += "\n" + line
        
        # 添加最后一个题目
        if current_question:
            questions.append(current_question.strip())
        
        return questions
    
    def save_exam_file(self, exam_id, formatted_paper):
        """保存试卷文件"""
        try:
            # 确保上传目录存在
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exam_{exam_id}_{timestamp}.txt"
            file_path = os.path.join(upload_dir, filename)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_paper)
            
            return {
                'success': True,
                'filename': filename,
                'file_path': file_path
            }
            
        except Exception as e:
            current_app.logger.error(f"保存试卷文件失败: {str(e)}")
            return {
                'success': False,
                'error': f"保存文件失败: {str(e)}"
            }
    
    def get_exam_history(self, username):
        """获取考试历史"""
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return []
            
            exam_records = ExamRecord.query.filter_by(user_id=user.id)\
                .order_by(ExamRecord.created_at.desc()).all()
            
            return [record.to_dict() for record in exam_records]
            
        except Exception as e:
            current_app.logger.error(f"获取考试历史失败: {str(e)}")
            return []
    
    def get_exam_by_id(self, exam_id):
        """根据ID获取考试"""
        try:
            exam_record = ExamRecord.query.filter_by(exam_id=exam_id).first()
            if exam_record:
                return exam_record.to_dict()
            return None
        except Exception as e:
            current_app.logger.error(f"获取考试失败: {str(e)}")
            return None
