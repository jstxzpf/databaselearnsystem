"""
用户模型
"""
from datetime import datetime, timezone
from app import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_or_create(username):
        """获取或创建用户"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                user = User(username=username)
                db.session.add(user)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    # 可能并发创建了，重试查询
                    user = User.query.filter_by(username=username).first()
                    if not user:
                        raise e
            
            return user

        except Exception as e:
            print(f"User.get_or_create failed: {e}")
            # 如果数据库操作彻底失败，返回一个临时对象（不保存到数据库）
            # 注意：这可能会导致后续外键关联失败，但在极端情况下比崩溃好
            return User(id=0, username=username)

def get_user_model():
    """获取User模型类"""
    return User
