@echo off
echo ========================================
echo   GMAIL AI MANAGER - ULTIMATE EDITION
echo ========================================
echo.

REM Test basic functionality
echo Testing virtual environment...

REM Check for virtual environments (try both .venv and gmail_ai_env)
if exist ".venv\Scripts\activate.bat" (
    echo Found .venv virtual environment
    echo Activating .venv virtual environment...
    call .venv\Scripts\activate.bat
    echo Virtual environment activated successfully!
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    echo Found gmail_ai_env virtual environment
    echo Activating gmail_ai_env virtual environment...
    call gmail_ai_env\Scripts\activate.bat
    echo Virtual environment activated successfully!
) else (
    echo Error: No virtual environment found!
    echo Please run setup.bat first to create the environment.
    echo Looking for: .venv\Scripts\activate.bat or gmail_ai_env\Scripts\activate.bat
    echo Current directory contents:
    dir
    echo.
    pause
    exit /b 1
)

echo.
echo Testing Python...
python --version
if errorlevel 1 (
    echo Error: Python not found in virtual environment!
    pause
    exit /b 1
)

echo.
echo Checking for GUI file...
if exist "gmail_ai_gui.py" (
    echo gmail_ai_gui.py found!
    echo.
    echo Launching Gmail AI GUI...
    python gmail_ai_gui.py
) else (
    echo Error: gmail_ai_gui.py not found!
    echo Current directory files:
    dir *.py
    pause
    exit /b 1
)

REM Check for errors
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERROR OCCURRED
    echo ========================================
    echo.
    echo An error occurred while running the application.
    echo.
    echo Troubleshooting tips:
    echo 1. Make sure you have created the .env file with your Gmail credentials
    echo 2. Ensure your Gmail App Password is correct (16 characters, no spaces)
    echo 3. Check that all dependencies are installed
    echo 4. Try running: pip install -r requirements.txt
    echo.
    pause
) else (
    echo.
    echo Application completed successfully!
    pause
)

echo.
echo Press any key to exit...
pause >nul