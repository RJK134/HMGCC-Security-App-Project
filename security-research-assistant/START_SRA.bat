@echo off
title Security Research Assistant - Launcher
color 0A
echo.
echo  ============================================================
echo   Security Research Assistant v0.1.0
echo   HMGCC Co-Creation Challenge (CH-2026-001)
echo  ============================================================
echo.
echo  Starting all services...
echo.

cd /d "%~dp0"

set PYTHON="C:\Users\Richards XPS\AppData\Roaming\uv\python\cpython-3.13.13-windows-x86_64-none\python.exe"
set PYTHONPATH=%~dp0

:: Check Python exists
if not exist %PYTHON% (
    echo  [ERROR] Python not found. Please run setup first.
    pause
    exit /b 1
)

:: Check Ollama is running
echo  [1/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo        Ollama not running - attempting to start...
    start "" "ollama" serve
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo        [WARNING] Ollama could not be started. LLM features unavailable.
        echo        Please start Ollama manually from the system tray.
    ) else (
        echo        [OK] Ollama started.
    )
) else (
    echo        [OK] Ollama running.
)

:: Start Backend
echo.
echo  [2/3] Starting backend server...
start "SRA Backend" /min cmd /c "%PYTHON% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload 2>&1"
echo        Waiting for backend...
timeout /t 6 /nobreak >nul

curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% neq 0 (
    echo        [WARNING] Backend may still be starting. Give it a moment.
) else (
    echo        [OK] Backend running on http://localhost:8000
)

:: Start Frontend
echo.
echo  [3/3] Starting frontend...
cd frontend
start "SRA Frontend" /min cmd /c "npm run dev 2>&1"
cd ..
timeout /t 4 /nobreak >nul
echo        [OK] Frontend starting on http://localhost:1420

:: Open browser
echo.
echo  ============================================================
echo   All services started!
echo   Opening browser...
echo  ============================================================
echo.
echo   App:     http://localhost:1420
echo   API:     http://localhost:8000/docs
echo   Health:  http://localhost:8000/api/v1/health
echo.
echo   This window manages the services.
echo   Press Ctrl+C or close this window to stop everything.
echo  ============================================================
echo.

timeout /t 2 /nobreak >nul
start "" http://localhost:1420

:: Keep alive and monitor
:loop
timeout /t 30 /nobreak >nul
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% neq 0 (
    echo  [%time%] WARNING: Backend not responding. Check the SRA Backend window.
)
goto loop
