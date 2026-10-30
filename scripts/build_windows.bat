@echo off
setlocal
cd /d "%~dp0.."
python -m venv .venv-build
if errorlevel 1 goto failed
.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
if errorlevel 1 goto failed
.venv-build\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name LingfengFinance --paths src --collect-binaries ortools src/launcher.py
if errorlevel 1 goto failed
.venv-build\Scripts\python.exe -c "import subprocess; subprocess.run([r'dist\LingfengFinance.exe', '--smoke-test'], check=True, timeout=60)"
if errorlevel 1 goto failed
echo.
echo Build complete: dist\LingfengFinance.exe
if /I not "%~1"=="--ci" pause
exit /b 0
:failed
echo Build failed. See the error above.
if /I not "%~1"=="--ci" pause
exit /b 1
