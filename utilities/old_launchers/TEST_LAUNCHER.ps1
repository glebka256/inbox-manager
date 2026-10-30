# PowerShell Test Launcher for Gmail AI
Write-Host "=== Gmail AI Test Launcher (PowerShell) ===" -ForegroundColor Green
Write-Host "Starting diagnostic checks..." -ForegroundColor Yellow

# Check current directory
Write-Host "`nCurrent directory: $PWD" -ForegroundColor Cyan

# Check for virtual environments
$venvExists = Test-Path ".\.venv\Scripts\python.exe"
$gmailEnvExists = Test-Path ".\gmail_ai_env\Scripts\python.exe"

Write-Host "`nVirtual Environment Check:" -ForegroundColor Yellow
Write-Host "  .venv exists: $venvExists" -ForegroundColor $(if($venvExists){"Green"}else{"Red"})
Write-Host "  gmail_ai_env exists: $gmailEnvExists" -ForegroundColor $(if($gmailEnvExists){"Green"}else{"Red"})

# Determine which Python to use
if ($venvExists) {
    $pythonExe = ".\.venv\Scripts\python.exe"
    Write-Host "`nUsing .venv environment" -ForegroundColor Green
} elseif ($gmailEnvExists) {
    $pythonExe = ".\gmail_ai_env\Scripts\python.exe"
    Write-Host "`nUsing gmail_ai_env environment" -ForegroundColor Green
} else {
    Write-Host "`nERROR: No virtual environment found!" -ForegroundColor Red
    Write-Host "Please run setup.bat first to create the environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Test Python
Write-Host "`nTesting Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "  Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Cannot run Python: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for GUI file
$guiExists = Test-Path "gmail_ai_gui.py"
Write-Host "`nGUI file check:" -ForegroundColor Yellow
Write-Host "  gmail_ai_gui.py exists: $guiExists" -ForegroundColor $(if($guiExists){"Green"}else{"Red"})

if (-not $guiExists) {
    Write-Host "  ERROR: gmail_ai_gui.py not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Test tkinter
Write-Host "`nTesting tkinter..." -ForegroundColor Yellow
try {
    $tkinterTest = & $pythonExe -c "import tkinter; print('Tkinter OK')" 2>&1
    Write-Host "  $tkinterTest" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Tkinter not available: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nAll checks passed! Launching GUI..." -ForegroundColor Green
Write-Host "If a GUI window doesn't appear, check for error messages below:" -ForegroundColor Yellow

# Launch the GUI
try {
    & $pythonExe gmail_ai_gui.py
} catch {
    Write-Host "`nERROR launching GUI: $_" -ForegroundColor Red
    Write-Host "Check the error message above for details." -ForegroundColor Yellow
}

Write-Host "`nGUI closed. Press Enter to exit launcher." -ForegroundColor Cyan
Read-Host