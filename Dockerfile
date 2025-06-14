# 数据库学习系统 - Docker镜像
# 基于Python 3.11 Alpine Linux，优化镜像大小
FROM python:3.11-alpine

# 设置维护者信息
LABEL maintainer="Database Learning System"
LABEL description="Flask-based Database Learning System with AI Integration"
LABEL version="1.0"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    FLASK_CONFIG=production

# 安装系统依赖
# 包括构建工具和运行时依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    curl \
    && rm -rf /var/cache/apk/*

# 复制requirements.txt并安装Python依赖
# 先复制requirements.txt以利用Docker缓存
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p data/explanations static/uploads logs && \
    chmod -R 755 data static logs

# 创建非root用户以提高安全性
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# 设置目录权限
RUN chown -R appuser:appgroup /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "app:app"]
