@echo off
setlocal
cd /d "%~dp0.."
python -m venv .venv-build
if errorlevel 1 goto failed
.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
if errorlevel 1 goto failed
.venv-build\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name LingfengFinance --paths src src/launcher.py
if errorlevel 1 goto failed
echo.
echo Build complete: dist\LingfengFinance.exe
if /I not "%~1"=="--ci" pause
exit /b 0
:failed
echo Build failed. See the error above.
if /I not "%~1"=="--ci" pause
exit /b 1
