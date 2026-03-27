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

cd /d "%~dp0"

:: Create venv if it doesn't exist
if not exist ".venv" (
    echo  [1/2] Creating virtual environment...
    python -m venv .venv
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install Python deps if needed
if not exist ".venv\Lib\site-packages\fastapi" (
    echo  [2/2] Installing dependencies (first run only)...
    pip install -e . >nul 2>&1
    if errorlevel 1 (
        echo  [ERROR] Failed to install dependencies.
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

:: Tell the server to open the browser when it's ready
set SOFTNET_OPEN_BROWSER=1
set SOFTNET_PORT=8000

:: Start server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
