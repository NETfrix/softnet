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

:: Start server (builds frontend if needed, opens browser automatically)
set SOFTNET_OPEN_BROWSER=1
python run.py

pause
