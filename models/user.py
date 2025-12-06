"""
用户模型
"""
from datetime import datetime, timezone
from extensions import db

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
        # 在函数内部导入db,确保使用已绑定到当前app的db实例
        from extensions import db
        
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
            from flask import current_app
            current_app.logger.error(f"User.get_or_create failed: {e}")
            # 不返回临时对象,而是抛出异常让调用者处理
            raise

def get_user_model():
    """获取User模型类"""
    return User
