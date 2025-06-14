"""
文件处理工具类
"""
import os
import mimetypes
from werkzeug.utils import secure_filename
from flask import current_app

class FileHandler:
    """文件处理工具类"""
    
    @staticmethod
    def allowed_file(filename):
        """检查文件类型是否允许"""
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'txt'})
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def secure_save_file(file, upload_folder, prefix=""):
        """安全保存文件"""
        try:
            if not file or file.filename == '':
                return None, "没有选择文件"
            
            if not FileHandler.allowed_file(file.filename):
                return None, "不支持的文件类型"
            
            # 确保上传目录存在
            os.makedirs(upload_folder, exist_ok=True)
            
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            if prefix:
                filename = f"{prefix}_{filename}"
            
            file_path = os.path.join(upload_folder, filename)
            
            # 如果文件已存在，添加数字后缀
            counter = 1
            original_path = file_path
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_path)
                file_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 保存文件
            file.save(file_path)
            
            return file_path, None
            
        except Exception as e:
            return None, f"保存文件失败: {str(e)}"
    
    @staticmethod
    def read_text_file(file_path, encodings=['utf-8', 'gbk', 'gb2312']):
        """读取文本文件，自动尝试多种编码"""
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read(), None
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return None, f"读取文件失败: {str(e)}"
        
        return None, "无法识别文件编码"
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'mime_type': mime_type,
                'extension': os.path.splitext(file_path)[1].lower()
            }
        except Exception:
            return None
    
    @staticmethod
    def delete_file(file_path):
        """安全删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def clean_old_files(directory, max_age_days=30):
        """清理旧文件"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            cleaned_count = 0
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        if FileHandler.delete_file(file_path):
                            cleaned_count += 1
            
            return cleaned_count
        except Exception:
            return 0
