"""
数据模型包初始化
"""
from .user import User
from .knowledge import KnowledgeBase
from .exam import ExamModel
from .records import LearningRecord, ExamRecord, ReviewRecord
from .course import Course

__all__ = [
    'User',
    'KnowledgeBase',
    'ExamModel',
    'LearningRecord',
    'ExamRecord',
    'ReviewRecord',
    'Course'
]
