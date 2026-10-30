@echo off
REM Gmail Email Classifier Setup Script for Windows
REM This batch file will guide you through the setup process

echo.
echo ============================================================
echo    Gmail Email Classifier Setup for Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env configuration file...
    copy ".env.example" ".env"
    echo.
    echo IMPORTANT: You need to edit the .env file with your Gmail credentials
    echo.
    echo To get a Gmail App Password:
    echo 1. Enable 2-Factor Authentication on your Google Account
    echo 2. Go to Google Account Settings ^> Security ^> 2-Step Verification
    echo 3. Click "App passwords" and generate a password for "Mail"
    echo 4. Edit the .env file with your email and app password
    echo.
    
    set /p edit_env="Would you like to open .env file for editing now? (y/N): "
    if /i "%edit_env%"=="y" (
        notepad .env
    )
) else (
    echo .env file already exists
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your Gmail credentials (if not done already)
echo 2. Test connection: python test_gmail_connection.py
echo 3. Collect training data: python training_data_collector.py
echo 4. Train model: python ml_email_classifier.py
echo 5. Run classification: python Gmail_scraper.py
echo.
echo See README.md for detailed instructions
echo.

set /p test_now="Would you like to test the Gmail connection now? (y/N): "
if /i "%test_now%"=="y" (
    echo.
    echo Testing Gmail connection...
    python test_gmail_connection.py
)

echo.
echo Setup script completed!
pause