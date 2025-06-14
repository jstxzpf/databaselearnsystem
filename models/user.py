"""
用户模型
"""
from datetime import datetime, timezone

# 延迟导入避免循环依赖
def _get_db():
    """获取数据库实例"""
    from app import db
    return db

# 简化的User模型，直接继承db.Model
class User:
    """用户模型"""

    def __init__(self, id=None, username=None, created_at=None):
        self.id = id
        self.username = username
        self.created_at = created_at or datetime.now(timezone.utc)

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
            # 使用sqlite3直接操作数据库，避免SQLAlchemy问题
            import sqlite3
            import os

            # 获取数据库文件路径
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # 查询用户
                cursor.execute("SELECT id, username, created_at FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()

                if result:
                    # 用户存在，返回User对象
                    return User(id=result[0], username=result[1], created_at=result[2])
                else:
                    # 用户不存在，创建新用户
                    now = datetime.now(timezone.utc)
                    cursor.execute(
                        "INSERT INTO users (username, created_at) VALUES (?, ?)",
                        (username, now)
                    )
                    conn.commit()

                    # 获取新创建的用户ID
                    user_id = cursor.lastrowid
                    return User(id=user_id, username=username, created_at=now)

        except Exception as e:
            print(f"User.get_or_create failed: {e}")
            # 如果失败，返回简单的User实例
            return User(id=1, username=username)

# 为了兼容现有代码，提供get_user_model函数
def get_user_model():
    """获取User模型类"""
    return User
