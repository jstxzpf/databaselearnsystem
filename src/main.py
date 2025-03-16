"""
主入口模块 - 启动数据库学习系统
"""

import sys
import os

# 将项目根目录添加到Python模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 现在可以正确导入
from src.app import App

def main():
    """主入口函数"""
    app = App()
    app.run()

if __name__ == "__main__":
    main() 