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

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install -e . >nul 2>&1
pip install -r requirements-build.txt >nul 2>&1

echo [3/5] Downloading browser (chromium, ~150 MB, first time only)...
:: PLAYWRIGHT_BROWSERS_PATH=0 installs chromium INSIDE the playwright package so
:: PyInstaller (--collect-all playwright) bundles it into the standalone exe.
set PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium

echo [4/5] Building executable (this can take a few minutes)...
python build.py

echo.
echo [5/5] Done!
echo.
echo  Your executable is at: dist\immo-scanner.exe
echo  It is self-contained (chromium included) - no Python needed to run it.
echo  Copy .env.example to .env next to the exe and edit it.
echo.
pause
