"""
设置服务
"""
import os
import json
import subprocess
import requests
from flask import current_app

class SettingsService:
    """设置服务类"""
    
    SETTINGS_FILE = 'data/settings.json'
    
    def __init__(self):
        self.ensure_settings_file()
    
    def ensure_settings_file(self):
        """确保设置文件存在"""
        try:
            if not os.path.exists(self.SETTINGS_FILE):
                os.makedirs(os.path.dirname(self.SETTINGS_FILE), exist_ok=True)
                default_settings = {
                    'ollama_api_url': 'http://127.0.0.1:11434/api/chat',
                    'ollama_model': 'gemma3:27b',
                    'current_course': '数据库原理',
                    'created_at': '2024-01-01T00:00:00',
                    'updated_at': '2024-01-01T00:00:00'
                }
                self.save_settings(default_settings)
            else:
                # 验证现有文件是否有效
                try:
                    with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            raise ValueError("文件为空")
                        json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    # 文件损坏，重新创建
                    current_app.logger.warning("设置文件损坏，重新创建")
                    default_settings = self.get_default_settings()
                    self.save_settings(default_settings)
        except Exception as e:
            current_app.logger.error(f"初始化设置文件失败: {e}")
    
    def load_settings(self):
        """加载设置"""
        try:
            with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.error(f"加载设置失败: {e}")
            return self.get_default_settings()
    
    def save_settings(self, settings):
        """保存设置"""
        try:
            # 更新时间戳
            from datetime import datetime
            settings['updated_at'] = datetime.utcnow().isoformat()
            
            # 原子写入：先写入临时文件，再重命名
            temp_file = f"{self.SETTINGS_FILE}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # Windows下重命名需要先删除目标文件
            if os.path.exists(self.SETTINGS_FILE):
                try:
                    os.replace(temp_file, self.SETTINGS_FILE)
                except OSError:
                    # 如果replace失败（如文件被占用），尝试删除后重命名
                    os.remove(self.SETTINGS_FILE)
                    os.rename(temp_file, self.SETTINGS_FILE)
            else:
                os.rename(temp_file, self.SETTINGS_FILE)
                
            return True
        except Exception as e:
            current_app.logger.error(f"保存设置失败: {e}")
            if os.path.exists(f"{self.SETTINGS_FILE}.tmp"):
                try:
                    os.remove(f"{self.SETTINGS_FILE}.tmp")
                except:
                    pass
            return False
    
    def get_default_settings(self):
        """获取默认设置"""
        return {
            'ollama_api_url': 'http://127.0.0.1:11434/api/chat',
            'ollama_model': 'gemma3:27b',
            'current_course': '数据库原理',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
    
    def get_available_models(self):
        """获取可用的Ollama模型"""
        try:
            # 尝试从配置获取API URL，如果失败则使用默认值
            settings = self.load_settings()
            api_url = settings.get('ollama_api_url', 'http://127.0.0.1:11434/api/chat')
            
            # 构造tags API URL (假设API URL是 /api/chat，我们需要 /api/tags)
            base_url = api_url.replace('/api/chat', '')
            tags_url = f"{base_url}/api/tags"
            
            try:
                response = requests.get(tags_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    if 'models' in data:
                        for model in data['models']:
                            models.append(model['name'])
                    return models
            except Exception as e:
                current_app.logger.warning(f"通过API获取模型失败: {e}")
            
            # 如果API失败，尝试使用默认列表或返回空
            return []
            
        except Exception as e:
            current_app.logger.error(f"获取模型列表异常: {e}")
            return []
    
    def test_ollama_connection(self, api_url, model_name):
        """测试Ollama连接"""
        try:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "stream": False,
                "options": {
                    "num_predict": 10,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                api_url,
                json=payload,
                timeout=30,  # 增加超时时间到30秒
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    return {
                        'success': True,
                        'message': '连接成功',
                        'response': result['message']['content'][:50] + '...'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'API响应格式错误'
                    }
            else:
                return {
                    'success': False,
                    'message': f'API错误: {response.status_code} - {response.text}'
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': '无法连接到Ollama服务，请确保服务正在运行'
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': '连接超时，请检查网络或服务状态'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'连接测试失败: {str(e)}'
            }
    
    def update_ollama_settings(self, api_url, model_name):
        """更新Ollama设置"""
        try:
            settings = self.load_settings()
            settings['ollama_api_url'] = api_url
            settings['ollama_model'] = model_name
            
            if self.save_settings(settings):
                # 更新应用配置（需要重启才能完全生效）
                current_app.config['OLLAMA_API_URL'] = api_url
                current_app.config['OLLAMA_MODEL'] = model_name
                return {
                    'success': True,
                    'message': '设置已保存，重启应用后完全生效'
                }
            else:
                return {
                    'success': False,
                    'message': '保存设置失败'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'更新设置失败: {str(e)}'
            }
    
    def get_current_course(self):
        """获取当前课程"""
        settings = self.load_settings()
        return settings.get('current_course', '数据库原理')
    
    def set_current_course(self, course_name):
        """设置当前课程"""
        try:
            settings = self.load_settings()
            settings['current_course'] = course_name
            
            if self.save_settings(settings):
                return {
                    'success': True,
                    'message': '课程切换成功'
                }
            else:
                return {
                    'success': False,
                    'message': '保存课程设置失败'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'切换课程失败: {str(e)}'
            }
