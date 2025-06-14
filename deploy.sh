#!/bin/bash

# 数据库学习系统部署脚本
# 使用方法: ./deploy.sh [dev|prod]

set -e

MODE=${1:-dev}

echo "🚀 开始部署数据库学习系统 (模式: $MODE)"

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查Ollama服务
echo "📋 检查Ollama服务..."
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  警告: Ollama服务未运行或不可访问"
    echo "   请确保Ollama已安装并运行: ollama serve"
    echo "   然后下载所需模型: ollama pull gemma3:12b-it-q4_K_M"
else
    echo "✅ Ollama服务检查通过"
fi

# 安装依赖
echo "📦 安装Python依赖..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ 依赖安装完成"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data/explanations
mkdir -p static/uploads
mkdir -p logs

echo "✅ 目录创建完成"

# 初始化数据库
echo "🗄️  初始化数据库..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"

echo "✅ 数据库初始化完成"

# 根据模式启动应用
if [ "$MODE" = "prod" ]; then
    echo "🌐 生产模式启动..."
    
    # 检查是否安装了gunicorn
    if ! pip show gunicorn > /dev/null 2>&1; then
        echo "安装Gunicorn..."
        pip install gunicorn
    fi
    
    echo "启动生产服务器..."
    echo "访问地址: http://0.0.0.0:5000"
    gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile logs/access.log --error-logfile logs/error.log app:app
    
else
    echo "🔧 开发模式启动..."
    echo "访问地址: http://127.0.0.1:5000"
    python run.py
fi
