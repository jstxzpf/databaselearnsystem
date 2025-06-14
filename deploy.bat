@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM Database Learning System Deployment Script (Windows)
REM Usage: deploy.bat [dev|prod]

set MODE=%1
if "%MODE%"=="" set MODE=dev

echo.
echo ==================================================
echo Database Learning System - Deployment Script
echo ==================================================
echo Mode: %MODE%
echo.

REM Check Python version
echo [1/6] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python and add to PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python version %PYTHON_VERSION%

REM Check Ollama service
echo.
echo [2/6] Checking Ollama service...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama service not running or not accessible
    echo Please ensure Ollama is installed and running: ollama serve
    echo Then download required model: ollama pull qwen3:14b
) else (
    echo OK: Ollama service is running
)

REM Install dependencies
echo.
echo [3/6] Installing Python dependencies...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

echo OK: Dependencies installed

REM Create necessary directories
echo.
echo [4/6] Creating necessary directories...
if not exist "data" mkdir data
if not exist "data\explanations" mkdir data\explanations
if not exist "static\uploads" mkdir static\uploads
if not exist "logs" mkdir logs

echo OK: Directories created

REM Initialize database
echo.
echo [5/6] Initializing database...
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized successfully')"

echo OK: Database initialized

REM Start application based on mode
echo.
echo [6/6] Starting application...
if "%MODE%"=="prod" (
    echo Production mode startup...

    REM Check if gunicorn is installed
    pip show gunicorn >nul 2>&1
    if errorlevel 1 (
        echo Installing Gunicorn...
        pip install gunicorn -i https://mirrors.aliyun.com/pypi/simple/
    )

    echo Starting production server...
    echo Access URL: http://0.0.0.0:5000
    gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile logs/access.log --error-logfile logs/error.log app:app

) else (
    echo Development mode startup...
    echo Access URL: http://127.0.0.1:5000
    python run.py
)

pause
