$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -e .
python -m pytest

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
python -m PyInstaller --clean --noconfirm modbussid.spec

Write-Host ""
Write-Host "EXE ready: dist\\modbussid-converter.exe"
