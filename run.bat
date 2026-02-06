@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Running setup.ps1...
  powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
  if not exist ".venv\Scripts\python.exe" (
    echo Setup failed. Please run setup.ps1 manually.
    pause
    exit /b 1
  )
)

".venv\Scripts\python.exe" "main.py"
if errorlevel 1 (
  echo.
  echo App exited with an error.
  pause
)
endlocal