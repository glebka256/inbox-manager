@echo off
echo ========================================
echo   GMAIL AI MANAGER - ULTIMATE EDITION
echo ========================================
echo.

REM Check for virtual environments (try both .venv and gmail_ai_env)
if exist ".venv\Scripts\activate.bat" (
    echo Found .venv virtual environment
    echo Activating .venv virtual environment...
    call .venv\Scripts\activate.bat
    set PYTHON_EXE=.venv\Scripts\python.exe
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    echo Found gmail_ai_env virtual environment
    echo Activating gmail_ai_env virtual environment...
    call gmail_ai_env\Scripts\activate.bat
    set PYTHON_EXE=gmail_ai_env\Scripts\python.exe
) else (
    echo Error: No virtual environment found!
    echo Please run setup.bat first to create the environment.
    echo Looking for: .venv\Scripts\activate.bat or gmail_ai_env\Scripts\activate.bat
    echo.
    pause
    exit /b 1
)

REM Install all advanced requirements
echo.
echo Installing advanced dependencies...
pip install matplotlib seaborn pandas numpy schedule flask flask-cors

REM Check for .env file
if not exist ".env" (
    echo.
    echo Warning: .env file not found!
    echo Please create .env file with your Gmail credentials.
    echo Example:
    echo EMAIL_ADDRESS=your_email@gmail.com
    echo EMAIL_PASSWORD=your_app_password
    echo.
    pause
)

echo.
echo ========================================
echo   CHOOSE YOUR EXPERIENCE
echo ========================================
echo.
echo 1. Launch Advanced GUI (Recommended)
echo 2. Launch Mobile API Server
echo 3. Run Master System Demo
echo 4. Run Security Compliance Demo
echo 5. Run Business Intelligence Demo
echo 6. Launch Original GUI (Basic)
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting Advanced Gmail AI GUI...
    echo Please wait while the GUI loads...
    %PYTHON_EXE% advanced_gmail_ai.py
    if errorlevel 1 (
        echo.
        echo ERROR: Advanced GUI failed to start!
        echo Check the error messages above.
        pause
    ) else (
        echo.
        echo Advanced GUI closed successfully.
    )
) else if "%choice%"=="2" (
    echo.
    echo Starting Mobile API Server...
    echo API will be available at: http://localhost:5000
    echo.
    %PYTHON_EXE% mobile_api.py
    if errorlevel 1 (
        echo.
        echo ERROR: Mobile API failed to start!
        pause
    )
) else if "%choice%"=="3" (
    echo.
    echo Running Master System Demo...
    %PYTHON_EXE% master_gmail_ai.py
    if errorlevel 1 (
        echo.
        echo ERROR: Master System failed to start!
        pause
    )
) else if "%choice%"=="4" (
    echo.
    echo Running Security & Compliance Demo...
    %PYTHON_EXE% security_compliance.py
    if errorlevel 1 (
        echo.
        echo ERROR: Security & Compliance demo failed!
        pause
    )
) else if "%choice%"=="5" (
    echo.
    echo Running Business Intelligence Demo...
    %PYTHON_EXE% business_intelligence.py
    if errorlevel 1 (
        echo.
        echo ERROR: Business Intelligence demo failed!
        pause
    )
) else if "%choice%"=="6" (
    echo.
    echo Starting Original Gmail AI GUI...
    %PYTHON_EXE% gmail_ai_gui.py
    if errorlevel 1 (
        echo.
        echo ERROR: Original GUI failed to start!
        pause
    ) else (
        echo.
        echo Original GUI closed successfully.
    )
) else (
    echo Invalid choice. Starting Advanced GUI by default...
    %PYTHON_EXE% advanced_gmail_ai.py
    if errorlevel 1 (
        echo.
        echo ERROR: Advanced GUI failed to start!
        pause
    )
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
    echo 4. Try running setup.bat again if issues persist
    echo.
    echo Recent log files:
    dir *.log /o-d 2>nul | head -3
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo   APPLICATION COMPLETED SUCCESSFULLY
    echo ========================================
    echo.
    echo Thank you for using Gmail AI Manager Ultimate Edition!
    echo.
    echo Generated files you can review:
    echo - Analytics reports in 'analytics_output' folder
    echo - Master reports: master_report_*.json
    echo - Configuration: master_config.json
    echo - API documentation: api_documentation.json
    echo.
    pause
)

echo.
echo Press any key to exit...
pause >nul