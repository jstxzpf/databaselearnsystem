"""
数据加载器 - 负责加载和处理数据文件
"""

import json
from src.config.config import Config

class DataLoader:
    """数据加载器类，处理JSON文件的加载和解析"""
    
    @staticmethod
    def load_json_file(file_path):
        """加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            tuple: (成功标志, 数据/错误消息)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                data = json.loads(file_content)
                return True, data
        except FileNotFoundError:
            return False, f"找不到文件: {file_path}"
        except json.JSONDecodeError:
            return False, f"文件格式错误: {file_path}"
        except Exception as e:
            return False, f"加载文件时发生错误: {str(e)}"
    
    @staticmethod
    def load_knowledge_base():
        """加载知识库数据
        
        Returns:
            tuple: (成功标志, 数据/错误消息)
        """
        return DataLoader.load_json_file(Config.KNOWLEDGE_BASE_FILE)
    
    @staticmethod
    def load_test_model():
        """加载考试模型数据
        
        Returns:
            tuple: (成功标志, 数据/错误消息)
        """
        return DataLoader.load_json_file(Config.TEST_MODEL_FILE)
    
    @staticmethod
    def save_to_file(file_path, content):
        """保存内容到文件
        
        Args:
            file_path: 文件路径
            content: 要保存的内容
            
        Returns:
            tuple: (成功标志, 错误消息)
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, None
        except Exception as e:
            return False, f"保存文件时发生错误: {str(e)}"
    
    @staticmethod
    def load_text_file(file_path):
        """加载文本文件
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            tuple: (成功标志, 内容/错误消息)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"加载文件时发生错误: {str(e)}" 