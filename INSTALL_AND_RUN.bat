@echo off
echo.
echo ========================================
echo  Inbox-Manager - Ultimate Edition
echo ========================================
echo.
echo Welcome! This will install and run your AI Gmail Manager.
echo.
echo What this script will do:
echo 1. Check if Python is installed
echo 2. Install required packages
echo 3. Launch the AI Gmail Manager
echo.
pause

echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
echo ✅ Python is installed!

echo.
echo [2/3] Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install packages
    echo Try running this script as Administrator
    pause
    exit /b 1
)
echo ✅ Packages installed successfully!

echo.
echo [3/3] Launching Inbox-Manager...
echo.
echo The application window will open shortly.
echo If you see any errors, check the console output.
echo.
echo REMEMBER:
echo - Start with DEMO MODE for safe testing
echo - Use your Gmail App Password (not regular password)
echo - Have fun organizing your emails!
echo.

cd /d "%~dp0"
python gui/Inbox_ManagerV3_GUI.py

if %errorlevel% neq 0 (
    echo.
    echo The application encountered an error.
    echo Check the error messages above for details.
    pause
)

echo.
echo Thanks for using Inbox-Manager!
pause
