"""
设置控制器 - 处理应用程序设置的业务逻辑
"""

from src.config.config import Config

class SettingsController:
    """设置控制器类，处理应用程序设置的业务逻辑"""
    
    def __init__(self):
        """初始化设置控制器"""
        self.api_client = None
    
    def set_api_client(self, api_client):
        """设置API客户端
        
        Args:
            api_client: API客户端实例
        """
        self.api_client = api_client
    
    def get_api_url(self):
        """获取API URL
        
        Returns:
            str: API URL
        """
        if self.api_client:
            return self.api_client.base_url
        return "http://127.0.0.1:11434"
    
    def get_model_name(self):
        """获取模型名称
        
        Returns:
            str: 模型名称
        """
        if self.api_client:
            return self.api_client.model_name
        return Config.MODEL_NAME
    
    def update_settings(self, api_url, model_name):
        """更新API设置
        
        Args:
            api_url: 新的API URL
            model_name: 新的模型名称
            
        Returns:
            tuple: (成功标志, 错误消息)
        """
        if not self.api_client:
            return False, "未初始化API客户端"
            
        try:
            self.api_client.update_settings(api_url, model_name)
            return True, None
        except Exception as e:
            return False, f"更新设置失败: {str(e)}"
    
    def test_connection(self):
        """测试API连接
        
        Returns:
            tuple: (成功标志, 错误消息)
        """
        if not self.api_client:
            return False, "未初始化API客户端"
            
        return self.api_client.check_availability() 