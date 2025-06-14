#!/bin/bash

# 数据库学习系统 - Docker快速启动脚本
# 使用方法: ./docker-start.sh [dev|prod] [build]

set -e

MODE=${1:-prod}
BUILD_FLAG=$2

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "========================================"
echo "数据库学习系统 - Docker快速启动"
echo "========================================"
echo "模式: $MODE"
echo "时间: $(date)"
echo "========================================"

# 检查Docker环境
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker或Docker Compose未安装"
    exit 1
fi

# 检查环境变量文件
if [[ ! -f ".env" && -f ".env.example" ]]; then
    log_warning "复制环境变量模板文件"
    cp .env.example .env
fi

# 构建镜像（如果需要）
if [[ "$BUILD_FLAG" == "build" ]]; then
    log_info "构建Docker镜像..."
    if [[ "$MODE" == "dev" ]]; then
        docker-compose -f docker-compose.dev.yml build
    else
        docker-compose build
    fi
fi

# 启动服务
log_info "启动Docker服务..."
if [[ "$MODE" == "dev" ]]; then
    docker-compose -f docker-compose.dev.yml up -d
    COMPOSE_FILE="docker-compose.dev.yml"
else
    docker-compose up -d
    COMPOSE_FILE="docker-compose.yml"
fi

# 等待服务启动
log_info "等待服务启动..."
sleep 10

# 检查服务状态
log_info "检查服务状态..."
docker-compose -f "$COMPOSE_FILE" ps

# 健康检查
log_info "执行健康检查..."
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health &>/dev/null; then
        log_success "应用启动成功!"
        break
    fi
    if [[ $i -eq 30 ]]; then
        log_warning "健康检查超时，请手动检查应用状态"
        break
    fi
    sleep 2
done

echo "========================================"
log_success "Docker服务启动完成!"
echo "========================================"
echo ""
echo "访问信息:"
echo "  应用地址: http://localhost:5000"
echo "  健康检查: http://localhost:5000/api/health"
echo ""
echo "管理命令:"
echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "  停止服务: docker-compose -f $COMPOSE_FILE down"
echo "  重启服务: docker-compose -f $COMPOSE_FILE restart"
echo ""
