@echo off
title Gmail AI Manager
echo Starting Gmail AI Manager...

cd /d "%~dp0"
call gmail_ai_env\Scripts\activate.bat
python gmail_ai_gui.py

echo.
echo Press any key to exit...
pause >nul
exit