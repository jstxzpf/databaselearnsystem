@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM 数据库学习系统 - Docker快速启动脚本 (Windows版本)
REM 使用方法: docker-start.bat [dev|prod] [build]

set MODE=%1
if "%MODE%"=="" set MODE=prod

set BUILD_FLAG=%2

echo ========================================
echo Database Learning System - Docker Start
echo ========================================
echo Mode: %MODE%
echo Time: %date% %time%
echo ========================================

REM 检查Docker环境
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

REM 检查环境变量文件
if not exist ".env" (
    if exist ".env.example" (
        echo [WARNING] Copying environment template file
        copy .env.example .env >nul
    )
)

REM 构建镜像（如果需要）
if "%BUILD_FLAG%"=="build" (
    echo [INFO] Building Docker image...
    if "%MODE%"=="dev" (
        docker-compose -f docker-compose.dev.yml build
    ) else (
        docker-compose build
    )
    if errorlevel 1 (
        echo [ERROR] Build failed
        exit /b 1
    )
)

REM 启动服务
echo [INFO] Starting Docker services...
if "%MODE%"=="dev" (
    docker-compose -f docker-compose.dev.yml up -d
    set COMPOSE_FILE=docker-compose.dev.yml
) else (
    docker-compose up -d
    set COMPOSE_FILE=docker-compose.yml
)

if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)

REM 等待服务启动
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo [INFO] Checking service status...
docker-compose -f "!COMPOSE_FILE!" ps

REM 健康检查
echo [INFO] Performing health check...
set HEALTH_CHECK_PASSED=0
for /l %%i in (1,1,30) do (
    curl -f http://localhost:5000/api/health >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] Application started successfully!
        set HEALTH_CHECK_PASSED=1
        goto :health_check_done
    )
    timeout /t 2 /nobreak >nul
)

:health_check_done
if !HEALTH_CHECK_PASSED!==0 (
    echo [WARNING] Health check timeout, please check application status manually
)

echo ========================================
echo [SUCCESS] Docker services started!
echo ========================================
echo.
echo Access Information:
echo   Application URL: http://localhost:5000
echo   Health Check:    http://localhost:5000/api/health
echo.
echo Management Commands:
echo   View logs:    docker-compose -f !COMPOSE_FILE! logs -f
echo   Stop services: docker-compose -f !COMPOSE_FILE! down
echo   Restart:      docker-compose -f !COMPOSE_FILE! restart
echo.

pause
