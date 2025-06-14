"""
数据库工具类
"""
from app import db
from models import User, LearningRecord, ExamRecord, ReviewRecord

def init_database():
    """初始化数据库"""
    try:
        # 创建所有表
        db.create_all()
        
        # 创建默认用户（如果不存在）
        default_user = User.query.filter_by(username='admin').first()
        if not default_user:
            default_user = User(username='admin')
            db.session.add(default_user)
            db.session.commit()
            print("创建默认用户: admin")
        
        print("数据库初始化完成")
        return True
        
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return False

def reset_database():
    """重置数据库"""
    try:
        # 删除所有表
        db.drop_all()
        
        # 重新创建表
        db.create_all()
        
        print("数据库重置完成")
        return True
        
    except Exception as e:
        print(f"数据库重置失败: {str(e)}")
        return False

def get_database_stats():
    """获取数据库统计信息"""
    try:
        stats = {
            'users': User.query.count(),
            'learning_records': LearningRecord.query.count(),
            'exam_records': ExamRecord.query.count(),
            'review_records': ReviewRecord.query.count()
        }
        return stats
    except Exception as e:
        print(f"获取数据库统计失败: {str(e)}")
        return {}
