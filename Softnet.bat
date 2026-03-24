@echo off
title Softnet - Network Analysis
color 0A

echo.
echo   ============================
echo    Softnet - Network Analysis
echo   ============================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.11+ from python.org
    echo.
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js not found. Install Node.js 18+ from nodejs.org
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

:: Create venv if it doesn't exist
if not exist ".venv" (
    echo  [1/4] Creating virtual environment...
    python -m venv .venv
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install Python deps if needed
if not exist ".venv\Lib\site-packages\fastapi" (
    echo  [2/4] Installing Python dependencies...
    pip install -e . >nul 2>&1
    if errorlevel 1 (
        echo  [ERROR] Failed to install Python dependencies.
        pause
        exit /b 1
    )
)

:: Install and build frontend if needed
if not exist "frontend\dist\index.html" (
    echo  [3/4] Installing frontend dependencies...
    cd frontend
    call npm install >nul 2>&1
    echo  [4/4] Building frontend...
    call npm run build >nul 2>&1
    cd ..
    if not exist "frontend\dist\index.html" (
        echo  [ERROR] Frontend build failed.
        pause
        exit /b 1
    )
)

echo.
echo  Starting Softnet...
echo  Opening http://localhost:8000
echo.
echo  Press Ctrl+C to stop.
echo.

:: Open browser after a short delay
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: Start server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
