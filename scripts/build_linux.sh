#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv-build
.venv-build/bin/python -m pip install -r requirements-build.txt
.venv-build/bin/python -m PyInstaller --noconfirm --clean --onedir --name LingfengFinance --paths src --collect-binaries ortools src/launcher.py
.venv-build/bin/python -c 'import subprocess; subprocess.run(["dist/LingfengFinance/LingfengFinance", "--smoke-test"], check=True, timeout=60)'
tar -czf "dist/LingfengFinance-Linux-$(uname -m).tar.gz" -C dist LingfengFinance
echo "Build complete: dist/LingfengFinance-Linux-$(uname -m).tar.gz"
