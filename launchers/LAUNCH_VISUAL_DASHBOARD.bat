@echo off
REM Visual Dashboard Direct Launcher - No Terminal Window

REM Find and use the correct virtual environment
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "visual_advanced_gui.py"
) else if exist "gmail_ai_env\Scripts\pythonw.exe" (
    start "" "gmail_ai_env\Scripts\pythonw.exe" "visual_advanced_gui.py"
) else (
    echo Error: No virtual environment found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Close this terminal window after launching
exit