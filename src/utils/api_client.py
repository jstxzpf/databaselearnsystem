"""
API客户端工具 - 负责与Ollama API的所有交互
"""

import requests
import json
from src.config.config import Config

class ApiClient:
    """Ollama API客户端类，处理所有与API的交互"""
    
    def __init__(self, api_url=None, model_name=None):
        """初始化API客户端
        
        Args:
            api_url: API基础URL，默认使用配置中的URL
            model_name: 使用的模型名称，默认使用配置中的模型名称
        """
        self.base_url = "http://127.0.0.1:11434"
        self.generate_url = f"{self.base_url}/api/generate"
        self.model_name = model_name or Config.MODEL_NAME
    
    def check_availability(self):
        """检查API是否可用
        
        Returns:
            tuple: (是否可用, 错误消息)
        """
        try:
            # 首先检查API是否运行
            response = requests.get(f"{self.base_url}/api/tags", timeout=Config.API_TIMEOUT)
            
            if response.status_code != 200:
                return False, f"API返回错误状态码: {response.status_code}"
            
            # 检查模型是否可用
            models_data = response.json()
            available_models = [model["name"] for model in models_data.get("models", [])]
            
            if self.model_name not in available_models:
                return False, f"模型 {self.model_name} 未在Ollama中安装，可用模型: {', '.join(available_models)}"
            
            # 简单测试模型生成
            test_data = {
                "model": self.model_name,
                "prompt": "Hello"
            }
            
            test_response = requests.post(
                self.generate_url,
                json=test_data,
                timeout=Config.API_TIMEOUT * 2
            )
            
            if test_response.status_code != 200:
                return False, f"模型测试失败，状态码: {test_response.status_code}"
            
            return True, f"API可用，使用模型: {self.model_name}"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到API服务"
        except Exception as e:
            return False, f"检查API时发生错误: {str(e)}"
    
    def get_completion(self, prompt):
        """获取AI回答
        
        Args:
            prompt: 提示文本
        
        Returns:
            str: AI回答
            
        Raises:
            Exception: 当API请求失败时抛出异常
        """
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # 增加超时时间，复杂解析可能需要更长时间
            response = requests.post(self.generate_url, json=data, timeout=Config.API_TIMEOUT * 20)
            
            if response.status_code == 200:
                response_json = response.json()
                
                # 确保我们有一个响应对象
                if isinstance(response_json, dict):
                    if "response" in response_json:
                        return response_json["response"]
                    elif "error" in response_json:
                        raise Exception(f"API返回错误: {response_json['error']}")
                    else:
                        # 如果没有找到预期的字段，打印响应以便调试
                        print(f"API响应格式异常: {response_json}")
                        return str(response_json)
                else:
                    # 如果不是字典，尝试将整个响应作为字符串返回
                    return str(response_json)
            else:
                # 尝试获取更详细的错误信息
                error_detail = ""
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = f": {error_json['error']}"
                except:
                    error_detail = f": {response.text}"
                
                raise Exception(f"API请求失败，状态码: {response.status_code}{error_detail}")
        except requests.exceptions.Timeout:
            raise Exception("API请求超时，生成解析需要较长时间，请重试")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到API服务，请确保Ollama服务正在运行")
        except Exception as e:
            raise Exception(f"获取AI回答失败: {str(e)}")
    
    def update_settings(self, api_url, model_name):
        """更新API设置
        
        Args:
            api_url: 新的API URL
            model_name: 新的模型名称
        """
        if api_url:
            # 提取基础URL
            self.base_url = api_url.split("/api/")[0]
            self.generate_url = f"{self.base_url}/api/generate"
        
        self.model_name = model_name 