@echo off
title Gmail AI Manager Launcher
echo ========================================
echo Gmail AI Manager Launcher
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "gmail_ai_env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call gmail_ai_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Check if GUI file exists
if not exist "gmail_ai_gui.py" (
    echo ERROR: gmail_ai_gui.py not found!
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Run the GUI
echo [2/3] Starting Gmail AI Manager GUI...
echo.
echo NOTE: The GUI window should open now.
echo       If you see errors, they will appear in this window.
echo       You can close this window after the GUI opens.
echo.
python gmail_ai_gui.py

echo.
echo [3/3] GUI has closed.
echo Press any key to exit this launcher...
pause >nul