@echo off
setlocal EnableDelayedExpansion

:: Set window properties
title Gmail AI Manager
mode con: cols=80 lines=25
color 0A

:: Show startup message
echo.
echo ================================================
echo          Gmail AI Manager Launcher
echo ================================================
echo.
echo Starting up... Please wait...
echo.

:: Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check if we're in the right directory
if not exist "gmail_ai_gui.py" (
    echo ERROR: Cannot find gmail_ai_gui.py
    echo Make sure this batch file is in the Email_Scraper folder
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

:: Check virtual environment
if not exist "gmail_ai_env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo [Step 1/3] Activating Python virtual environment...
call "%SCRIPT_DIR%gmail_ai_env\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

echo             ✓ Virtual environment activated
echo.

:: Check if Python is working
echo [Step 2/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found in virtual environment
    echo.
    pause
    exit /b 1
)

echo             ✓ Python is ready
echo.

:: Launch the GUI
echo [Step 3/3] Launching Gmail AI Manager GUI...
echo.
echo ================================================
echo  The GUI window should appear now...
echo  You can minimize this console window.
echo  
echo  If you see any errors, they will appear below:
echo ================================================
echo.

:: Run the Python GUI
python "%SCRIPT_DIR%gmail_ai_gui.py"

:: Check if GUI ran successfully
if errorlevel 1 (
    echo.
    echo ================================================
    echo  ERROR: The GUI encountered an error
    echo ================================================
    echo.
) else (
    echo.
    echo ================================================
    echo  Gmail AI Manager closed normally
    echo ================================================
    echo.
)

echo Press any key to close this window...
pause >nul