@echo off
cd /d "%~dp0"

REM Silent launch - no console window
if exist ".venv\Scripts\pythonw.exe" (
    start "" /B ".venv\Scripts\pythonw.exe" "visual_advanced_gui.py"
) else if exist "gmail_ai_env\Scripts\pythonw.exe" (
    start "" /B "gmail_ai_env\Scripts\pythonw.exe" "visual_advanced_gui.py"
) else (
    start "" /B pythonw.exe "visual_advanced_gui.py"
)