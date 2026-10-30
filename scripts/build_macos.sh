#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv-build
.venv-build/bin/python -m pip install -r requirements-build.txt
.venv-build/bin/python -m PyInstaller --noconfirm --clean --windowed --name LingfengFinance --paths src --collect-binaries ortools src/launcher.py
.venv-build/bin/python -c 'import subprocess; subprocess.run(["dist/LingfengFinance.app/Contents/MacOS/LingfengFinance", "--smoke-test"], check=True, timeout=60)'
ditto -c -k --sequesterRsrc --keepParent dist/LingfengFinance.app "dist/LingfengFinance-macOS-$(uname -m).zip"
echo "Build complete: dist/LingfengFinance-macOS-$(uname -m).zip"
