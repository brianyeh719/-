$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

function Find-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    return $null
}

$pyCmd = Find-Python
if (-not $pyCmd) {
    Write-Host "Python not found. Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

$venvPath = Join-Path $PSScriptRoot ".venv"
$venvPy = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPy)) {
    Write-Host "Creating virtual environment..."
    & $pyCmd -m venv $venvPath
}

if (-not (Test-Path $venvPy)) {
    Write-Host "Failed to create virtual environment." -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies..."
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r "requirements.txt"

Write-Host "Installing Playwright browser (chromium)..."
& $venvPy -m playwright install chromium

Write-Host "Setup complete. You can now run run.bat" -ForegroundColor Green