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

if not exist ".build-venv\Scripts\python.exe" (
  py -m venv .build-venv
  if errorlevel 1 goto :error
)

".build-venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".build-venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto :error
".build-venv\Scripts\ruff.exe" check src tests
if errorlevel 1 goto :error
".build-venv\Scripts\ruff.exe" format --check src tests
if errorlevel 1 goto :error
".build-venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 goto :error

".build-venv\Scripts\python.exe" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "DNG-to-JPEG" ^
  --collect-all rawpy ^
  --collect-all PIL ^
  src\dng_to_jpeg_gui.py
if errorlevel 1 goto :error

echo Build complete: dist\DNG-to-JPEG.exe
pause
exit /b 0

:error
echo Build failed. Review the messages above.
pause
exit /b 1
