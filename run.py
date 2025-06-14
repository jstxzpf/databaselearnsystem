#!/usr/bin/env python3
"""
数据库学习系统启动脚本
"""
import os
import sys
from app import create_app

def main():
    """主函数"""
    print("=" * 50)
    print("数据库学习系统 - Flask Web应用")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 检查必要文件
    required_files = ['kownlgebase.json', 'testmodel.json']
    for file in required_files:
        if not os.path.exists(file):
            print(f"警告: 找不到文件 {file}")
    
    # 创建应用
    try:
        app = create_app()
        print("✅ 应用初始化成功")
    except Exception as e:
        print(f"❌ 应用初始化失败: {e}")
        sys.exit(1)
    
    # 显示启动信息
    print("\n🚀 启动信息:")
    print(f"   - 应用地址: http://127.0.0.1:5000")
    print(f"   - 调试模式: {'开启' if app.debug else '关闭'}")
    print(f"   - 数据库: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"   - Ollama API: {app.config['OLLAMA_API_URL']}")
    print(f"   - AI模型: {app.config['OLLAMA_MODEL']}")

    # 测试AI连接
    print("\n🔍 测试AI服务连接...")
    try:
        import requests
        test_payload = {
            "model": app.config['OLLAMA_MODEL'],
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        }
        response = requests.post(
            app.config['OLLAMA_API_URL'],
            json=test_payload,
            timeout=30  # 增加超时时间到30秒
        )
        if response.status_code == 200:
            print("   ✅ AI服务连接正常")
        else:
            print(f"   ⚠️  AI服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI服务连接失败: {str(e)}")
        print("   请确保Ollama服务正在运行并已安装指定模型")
    
    print("\n📖 使用说明:")
    print("   1. 确保Ollama服务正在运行")
    print("   2. 在浏览器中访问 http://127.0.0.1:5000")
    print("   3. 开始使用数据库学习系统")
    print("   4. 按 Ctrl+C 停止服务器")
    
    print("\n" + "=" * 50)
    
    # 启动应用
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
