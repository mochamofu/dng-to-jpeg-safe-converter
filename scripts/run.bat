@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.9 or newer first.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\pythonw.exe" (
  py -m venv .venv
  if errorlevel 1 goto :error
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto :error
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto :error
)

start "" ".venv\Scripts\pythonw.exe" "%CD%\src\dng_to_jpeg_gui.py"
exit /b 0

:error
echo Setup failed. Review the messages above.
pause
exit /b 1

