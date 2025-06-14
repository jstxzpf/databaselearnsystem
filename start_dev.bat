@echo off
chcp 65001 >nul 2>&1

echo.
echo ==================================================
echo Database Learning System - Development Server
echo ==================================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found, using system Python
)

REM Create data directory if not exists
if not exist "data" mkdir data

REM Start development server
echo Starting development server...
echo.
python run.py

pause
