#!/bin/bash

# 数据库学习系统 - Docker构建脚本
# 使用方法: ./docker-build.sh [dev|prod] [--no-cache]

set -e

# 默认参数
MODE=${1:-prod}
NO_CACHE=${2}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查必要文件
check_files() {
    log_info "检查必要文件..."
    
    required_files=(
        "Dockerfile"
        "requirements.txt"
        "app.py"
        "config.py"
        "kownlgebase.json"
        "testmodel.json"
    )
    
    missing_files=()
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_error "缺少必要文件: ${missing_files[*]}"
        exit 1
    fi
    
    log_success "文件检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    directories=(
        "data"
        "data/explanations"
        "static/uploads"
        "logs"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "创建目录: $dir"
        fi
    done
    
    log_success "目录创建完成"
}

# 构建Docker镜像
build_image() {
    log_info "开始构建Docker镜像 (模式: $MODE)..."
    
    # 设置镜像标签
    if [[ "$MODE" == "dev" ]]; then
        IMAGE_TAG="database-learning-system:dev"
        DOCKERFILE="Dockerfile.dev"
    else
        IMAGE_TAG="database-learning-system:latest"
        DOCKERFILE="Dockerfile"
    fi
    
    # 构建参数
    BUILD_ARGS=""
    if [[ "$NO_CACHE" == "--no-cache" ]]; then
        BUILD_ARGS="--no-cache"
        log_info "使用 --no-cache 参数构建"
    fi
    
    # 执行构建
    log_info "构建镜像: $IMAGE_TAG"
    if docker build $BUILD_ARGS -f "$DOCKERFILE" -t "$IMAGE_TAG" .; then
        log_success "镜像构建成功: $IMAGE_TAG"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 检查环境变量文件
check_env_file() {
    log_info "检查环境变量配置..."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            log_warning ".env文件不存在，从.env.example复制"
            cp .env.example .env
            log_info "请编辑.env文件配置实际参数"
        else
            log_warning ".env文件不存在，将使用默认配置"
        fi
    else
        log_success "环境变量文件存在"
    fi
}

# 验证镜像
verify_image() {
    log_info "验证Docker镜像..."
    
    if [[ "$MODE" == "dev" ]]; then
        IMAGE_TAG="database-learning-system:dev"
    else
        IMAGE_TAG="database-learning-system:latest"
    fi
    
    if docker images | grep -q "$IMAGE_TAG"; then
        log_success "镜像验证成功: $IMAGE_TAG"
        
        # 显示镜像信息
        log_info "镜像信息:"
        docker images | grep "database-learning-system"
    else
        log_error "镜像验证失败"
        exit 1
    fi
}

# 清理旧镜像
cleanup_old_images() {
    log_info "清理旧的Docker镜像..."
    
    # 清理悬空镜像
    if docker images -f "dangling=true" -q | grep -q .; then
        docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true
        log_info "已清理悬空镜像"
    fi
    
    log_success "镜像清理完成"
}

# 显示使用说明
show_usage() {
    echo "数据库学习系统 - Docker构建脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 [dev|prod] [--no-cache]"
    echo ""
    echo "参数说明:"
    echo "  dev        构建开发环境镜像"
    echo "  prod       构建生产环境镜像 (默认)"
    echo "  --no-cache 不使用缓存构建"
    echo ""
    echo "示例:"
    echo "  $0                    # 构建生产环境镜像"
    echo "  $0 dev                # 构建开发环境镜像"
    echo "  $0 prod --no-cache    # 不使用缓存构建生产环境镜像"
}

# 主函数
main() {
    echo "========================================"
    echo "数据库学习系统 - Docker构建脚本"
    echo "========================================"
    echo "模式: $MODE"
    echo "时间: $(date)"
    echo "========================================"
    
    # 检查参数
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    if [[ "$MODE" != "dev" && "$MODE" != "prod" ]]; then
        log_error "无效的模式: $MODE (支持: dev, prod)"
        show_usage
        exit 1
    fi
    
    # 执行构建流程
    check_docker
    check_files
    create_directories
    check_env_file
    build_image
    verify_image
    cleanup_old_images
    
    echo "========================================"
    log_success "Docker镜像构建完成!"
    echo "========================================"
    
    # 显示后续操作建议
    echo ""
    echo "后续操作:"
    if [[ "$MODE" == "dev" ]]; then
        echo "  启动开发环境: docker-compose -f docker-compose.dev.yml up -d"
        echo "  查看日志:     docker-compose -f docker-compose.dev.yml logs -f"
    else
        echo "  启动生产环境: docker-compose up -d"
        echo "  查看日志:     docker-compose logs -f"
    fi
    echo "  访问应用:     http://localhost:5000"
    echo "  健康检查:     curl http://localhost:5000/api/health"
    echo ""
}

# 执行主函数
main "$@"
