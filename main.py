"""
主入口模块 - 启动数据库学习系统
"""

from src.app import App

def main():
    """主入口函数"""
    app = App()
    app.run()

if __name__ == "__main__":
    main() 