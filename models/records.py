"""
记录模型 - 学习记录、考试记录、审批记录
"""
from datetime import datetime
from app import db

class LearningRecord(db.Model):
    """学习记录模型"""
    __tablename__ = 'learning_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter = db.Column(db.String(100), nullable=False)
    concept = db.Column(db.String(200), nullable=False)
    concept_type = db.Column(db.String(20), nullable=False)  # 'concept' or 'content'
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LearningRecord {self.chapter}: {self.concept}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'chapter': self.chapter,
            'concept': self.concept,
            'concept_type': self.concept_type,
            'explanation': self.explanation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExamRecord(db.Model):
    """考试记录模型"""
    __tablename__ = 'exam_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.String(50), nullable=False)  # UUID
    exam_name = db.Column(db.String(100), nullable=False)
    chapters = db.Column(db.Text, nullable=False)  # JSON格式存储
    questions = db.Column(db.Text)  # JSON格式存储题目
    score = db.Column(db.Integer)
    status = db.Column(db.String(20), default='generated')  # generated, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExamRecord {self.exam_name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exam_id': self.exam_id,
            'exam_name': self.exam_name,
            'chapters': self.chapters,
            'questions': self.questions,
            'score': self.score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ReviewRecord(db.Model):
    """审批记录模型"""
    __tablename__ = 'review_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500))
    review_result = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    score = db.Column(db.Integer)
    status = db.Column(db.String(20), default='uploaded')  # uploaded, reviewed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReviewRecord {self.original_filename}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'review_result': self.review_result,
            'suggestions': self.suggestions,
            'score': self.score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
