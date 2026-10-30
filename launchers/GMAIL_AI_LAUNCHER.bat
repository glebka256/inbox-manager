@echo off
color 0A
title Gmail AI Manager - Main Launcher

:menu
cls
echo ========================================
echo      GMAIL AI MANAGER - MAIN MENU
echo ========================================
echo.
echo [1] Basic Gmail Interface (Recommended)
echo [2] Visual Dashboard (Advanced Charts)
echo [3] Master System Integration
echo [4] Test Connection
echo [5] Install Dependencies
echo [9] Exit
echo.
set /p choice="Select option (1-5, 9): "

if "%choice%"=="1" goto basic
if "%choice%"=="2" goto visual
if "%choice%"=="3" goto master
if "%choice%"=="4" goto test
if "%choice%"=="5" goto install
if "%choice%"=="9" goto exit
goto menu

:basic
cls
echo Starting Basic Gmail Interface...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python gmail_ai_gui.py
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    call gmail_ai_env\Scripts\activate.bat
    python gmail_ai_gui.py
) else (
    echo Error: No virtual environment found!
    pause
)
goto menu

:visual
cls
echo Starting Visual Dashboard...
if exist ".venv\Scripts\activate.bat" (
    echo Launching Visual Dashboard (terminal will close)...
    start "" .venv\Scripts\pythonw.exe visual_advanced_gui.py
    timeout /t 2 /nobreak >nul
    exit
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    echo Launching Visual Dashboard (terminal will close)...
    start "" gmail_ai_env\Scripts\pythonw.exe visual_advanced_gui.py
    timeout /t 2 /nobreak >nul
    exit
) else (
    echo Error: No virtual environment found!
    pause
)
goto menu

:master
cls
echo Starting Master System...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python master_gmail_ai.py
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    call gmail_ai_env\Scripts\activate.bat
    python master_gmail_ai.py
) else (
    echo Error: No virtual environment found!
    pause
)
goto menu

:test
cls
echo Testing Gmail Connection...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python utilities\test_gmail_connection.py
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    call gmail_ai_env\Scripts\activate.bat
    python utilities\test_gmail_connection.py
) else (
    echo Error: No virtual environment found!
    pause
)
goto menu

:install
cls
echo Installing Dependencies...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else if exist "gmail_ai_env\Scripts\activate.bat" (
    call gmail_ai_env\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo Error: No virtual environment found!
    pause
)
pause
goto menu

:exit
echo Goodbye!
exit