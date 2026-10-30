@echo off
REM Silent Visual Dashboard Launcher - No Terminal Window

cd /d "%~dp0.."

REM Find and use the correct virtual environment with pythonw.exe (no console)
if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\pythonw.exe" "visual_advanced_gui.py"
) else if exist "gmail_ai_env\Scripts\pythonw.exe" (
    "gmail_ai_env\Scripts\pythonw.exe" "visual_advanced_gui.py"
) else (
    REM Fallback to system Python with no console window
    pythonw.exe "visual_advanced_gui.py"
)