@echo off
echo Starting SRA Backend...
echo.
cd /d "%~dp0"
set PYTHONPATH=%~dp0
set VIRTUAL_ENV=%~dp0.venv
set PATH=%~dp0.venv\Scripts;%PATH%
"C:\Users\Richards XPS\AppData\Roaming\uv\python\cpython-3.13.13-windows-x86_64-none\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
