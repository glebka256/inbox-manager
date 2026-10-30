@echo off
echo Starting Advanced Gmail AI Manager...
echo.

REM Check if virtual environment exists
if not exist "gmail_ai_env\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call gmail_ai_env\Scripts\activate.bat

REM Install additional requirements for advanced features
echo Installing advanced features...
pip install matplotlib seaborn pandas>=2.0.0 numpy>=1.24.0

REM Launch advanced GUI
echo.
echo Launching Advanced Gmail AI Manager...
python advanced_gmail_ai.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)