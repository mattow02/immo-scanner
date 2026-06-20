@echo off
echo.
echo  ============================================
echo   Immo-Scanner - Quick Setup ^& Run
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo         Download it from: https://www.python.org/downloads/
    echo         IMPORTANT: Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)

:: Create venv if needed
if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

:: Install if needed
pip show immo-scanner >nul 2>&1
if errorlevel 1 (
    echo [2/3] Installing immo-scanner...
    pip install -e . >nul 2>&1
    python -m playwright install chromium >nul 2>&1
)

:: Copy .env if needed
if not exist ".env" (
    if exist ".env.example" (
        echo [3/3] Creating .env from template...
        copy .env.example .env >nul
        echo         Edit .env to set your preferences, then re-run this script.
        notepad .env
        pause
        exit /b 0
    )
)

echo.
echo  Starting Immo-Scanner...
echo  ========================
echo.
immo-scanner
