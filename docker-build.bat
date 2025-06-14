@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM 数据库学习系统 - Docker构建脚本 (Windows版本)
REM 使用方法: docker-build.bat [dev|prod] [--no-cache]

set MODE=%1
if "%MODE%"=="" set MODE=prod

set NO_CACHE=%2

echo ========================================
echo Database Learning System - Docker Build
echo ========================================
echo Mode: %MODE%
echo Time: %date% %time%
echo ========================================

REM 检查参数
if "%1"=="-h" goto :show_usage
if "%1"=="--help" goto :show_usage

if not "%MODE%"=="dev" if not "%MODE%"=="prod" (
    echo [ERROR] Invalid mode: %MODE% (supported: dev, prod)
    goto :show_usage
)

REM 检查Docker环境
echo [INFO] Checking Docker environment...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not installed
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose not installed
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker service not running
    exit /b 1
)

echo [SUCCESS] Docker environment check passed

REM 检查必要文件
echo [INFO] Checking required files...
set MISSING_FILES=
if not exist "Dockerfile" set MISSING_FILES=!MISSING_FILES! Dockerfile
if not exist "requirements.txt" set MISSING_FILES=!MISSING_FILES! requirements.txt
if not exist "app.py" set MISSING_FILES=!MISSING_FILES! app.py
if not exist "config.py" set MISSING_FILES=!MISSING_FILES! config.py
if not exist "kownlgebase.json" set MISSING_FILES=!MISSING_FILES! kownlgebase.json
if not exist "testmodel.json" set MISSING_FILES=!MISSING_FILES! testmodel.json

if not "!MISSING_FILES!"=="" (
    echo [ERROR] Missing required files: !MISSING_FILES!
    exit /b 1
)

echo [SUCCESS] File check passed

REM 创建必要目录
echo [INFO] Creating necessary directories...
if not exist "data" mkdir data
if not exist "data\explanations" mkdir data\explanations
if not exist "static\uploads" mkdir static\uploads
if not exist "logs" mkdir logs

echo [SUCCESS] Directories created

REM 检查环境变量文件
echo [INFO] Checking environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo [WARNING] .env file not found, copying from .env.example
        copy .env.example .env >nul
        echo [INFO] Please edit .env file with actual parameters
    ) else (
        echo [WARNING] .env file not found, will use default configuration
    )
) else (
    echo [SUCCESS] Environment file exists
)

REM 构建Docker镜像
echo [INFO] Building Docker image (mode: %MODE%)...

if "%MODE%"=="dev" (
    set IMAGE_TAG=database-learning-system:dev
    set DOCKERFILE=Dockerfile.dev
) else (
    set IMAGE_TAG=database-learning-system:latest
    set DOCKERFILE=Dockerfile
)

set BUILD_ARGS=
if "%NO_CACHE%"=="--no-cache" (
    set BUILD_ARGS=--no-cache
    echo [INFO] Building with --no-cache flag
)

echo [INFO] Building image: !IMAGE_TAG!
docker build !BUILD_ARGS! -f "!DOCKERFILE!" -t "!IMAGE_TAG!" .
if errorlevel 1 (
    echo [ERROR] Image build failed
    exit /b 1
)

echo [SUCCESS] Image built successfully: !IMAGE_TAG!

REM 验证镜像
echo [INFO] Verifying Docker image...
docker images | findstr "database-learning-system" >nul
if errorlevel 1 (
    echo [ERROR] Image verification failed
    exit /b 1
)

echo [SUCCESS] Image verification passed

REM 显示镜像信息
echo [INFO] Image information:
docker images | findstr "database-learning-system"

REM 清理旧镜像
echo [INFO] Cleaning up old Docker images...
for /f "tokens=3" %%i in ('docker images -f "dangling=true" -q 2^>nul') do (
    docker rmi %%i >nul 2>&1
)
echo [SUCCESS] Image cleanup completed

echo ========================================
echo [SUCCESS] Docker image build completed!
echo ========================================

echo.
echo Next steps:
if "%MODE%"=="dev" (
    echo   Start development: docker-compose -f docker-compose.dev.yml up -d
    echo   View logs:         docker-compose -f docker-compose.dev.yml logs -f
) else (
    echo   Start production:  docker-compose up -d
    echo   View logs:         docker-compose logs -f
)
echo   Access application: http://localhost:5000
echo   Health check:       curl http://localhost:5000/api/health
echo.

goto :eof

:show_usage
echo Database Learning System - Docker Build Script
echo.
echo Usage:
echo   %0 [dev^|prod] [--no-cache]
echo.
echo Parameters:
echo   dev        Build development environment image
echo   prod       Build production environment image (default)
echo   --no-cache Build without cache
echo.
echo Examples:
echo   %0                    # Build production image
echo   %0 dev                # Build development image
echo   %0 prod --no-cache    # Build production image without cache
goto :eof
