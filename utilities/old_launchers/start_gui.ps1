# Gmail AI Manager Launcher (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Gmail AI Manager Launcher" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (-not (Test-Path "gmail_ai_env\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.bat first to create the virtual environment." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Activate virtual environment
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\gmail_ai_env\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Check if GUI file exists
if (-not (Test-Path "gmail_ai_gui.py")) {
    Write-Host "ERROR: gmail_ai_gui.py not found!" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Run the GUI
Write-Host "[2/3] Starting Gmail AI Manager GUI..." -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: The GUI window should open now." -ForegroundColor Cyan
Write-Host "      If you see errors, they will appear in this window." -ForegroundColor Cyan
Write-Host "      You can close this window after the GUI opens." -ForegroundColor Cyan
Write-Host ""

try {
    python gmail_ai_gui.py
    Write-Host ""
    Write-Host "[3/3] GUI has closed normally." -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Error running GUI: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")