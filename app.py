"""
Flask应用主入口 - 数据库学习系统
"""
import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
import logging

# 初始化扩展
# 初始化扩展
from extensions import db

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 配置日志
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 导入模型以确保它们被注册
    with app.app_context():
        # 注册User模型
        from models.user import get_user_model
        User = get_user_model()

        # 导入其他模型
        from models.records import LearningRecord, ExamRecord, ReviewRecord

        # 创建数据库表
        db.create_all()
    
    return app

def register_blueprints(app):
    """注册蓝图"""
    try:
        from routes import main_bp, api_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        app.logger.error(f"导入蓝图失败: {e}")
        raise

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({'error': '文件太大，请选择小于16MB的文件'}), 413

def init_db():
    """初始化数据库"""
    db.create_all()
    print("数据库初始化完成")

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
