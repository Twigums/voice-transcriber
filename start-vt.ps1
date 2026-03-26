$ErrorActionPreference = "Continue"

# Navigate to the directory where the script is located
Set-Location $PSScriptRoot

Write-Host "Starting Voice Transcriber initialization..." -ForegroundColor Cyan

# Check for a virtual environment and activate it if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Found local virtual environment. Activating..." -ForegroundColor Green
    . ".\venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\activate.bat") {
    Write-Host "✅ Found local virtual environment (Batch style). Activating..." -ForegroundColor Green
    cmd.exe /c ".\venv\Scripts\activate.bat"
} else {
    Write-Host "⚠️  No local 'venv' folder found. We will use your global Python environment." -ForegroundColor Yellow
}

# Run the transcriber
Write-Host "🚀 Launching Voice Transcriber..." -ForegroundColor Cyan
python src\main.py

# Keep the window open if the script crashes or completes
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ App exited unexpectedly with code $LASTEXITCODE." -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
