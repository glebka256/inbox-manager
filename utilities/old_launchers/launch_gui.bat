@echo off
title Gmail AI Manager
color 0A
echo.
echo ========================================
echo Gmail AI Manager Launcher
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "gmail_ai_env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call gmail_ai_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [2/3] Starting GUI...
echo.
echo The Gmail AI Manager window should open now...
echo You can minimize this window once the GUI appears.
echo.

python gmail_ai_gui.py

echo.
echo [3/3] GUI closed.
echo.
pause