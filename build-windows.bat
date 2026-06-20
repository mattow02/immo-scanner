@echo off
echo.
echo  ============================================
echo   Immo-Scanner - Windows Build Script
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.12+ from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
pip install -e . >nul 2>&1
pip install pyinstaller >nul 2>&1

echo [3/4] Building executable...
python build.py

echo.
echo [4/4] Done!
echo.
echo  Your executable is at: dist\immo-scanner.exe
echo  Copy .env.example to .env next to the exe and edit it.
echo.
pause
