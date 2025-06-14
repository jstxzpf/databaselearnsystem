# Database Learning System - Development Server Startup Script
# PowerShell version for better Unicode support

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Database Learning System - Development Server" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found, using system Python" -ForegroundColor Yellow
}

# Create data directory if not exists
if (!(Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
}

# Start development server
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host ""

try {
    python run.py
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
