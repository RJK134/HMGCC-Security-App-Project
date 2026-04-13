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
set PYTHONPATH=%~dp0

:: Find Python - try uv python first, then system python
set PYTHON=
for /f "delims=" %%i in ('where python 2^>nul') do (
    if not defined PYTHON set PYTHON=%%i
)

:: Check if uv's 3.13 is available (preferred)
set UV_PYTHON=%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.13.13-windows-x86_64-none\python.exe
"%UV_PYTHON%" --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=%UV_PYTHON%
    echo  [OK] Found Python 3.13 via uv
) else (
    :: Try the shorter uv path
    set UV_PYTHON2=%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\python.exe
    "%UV_PYTHON2%" --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON=%UV_PYTHON2%
        echo  [OK] Found Python 3.13 via uv
    )
)

:: Verify we have Python
if not defined PYTHON (
    echo  [ERROR] Python not found. Install Python 3.11+ or run: uv python install 3.13
    pause
    exit /b 1
)

echo  Using: %PYTHON%
echo.

:: Check Ollama is running
echo  [1/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo        Ollama not running - attempting to start...
    start "" "ollama" serve
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo        [WARNING] Could not start Ollama. Start it from the system tray.
    ) else (
        echo        [OK] Ollama started.
    )
) else (
    echo        [OK] Ollama running.
)

:: Start Backend
echo.
echo  [2/3] Starting backend server...
start "SRA Backend" /min cmd /c ""%PYTHON%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
echo        Waiting for backend...
timeout /t 8 /nobreak >nul

curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% neq 0 (
    echo        [..] Backend still starting, please wait...
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:8000/api/v1/health >nul 2>&1
    if %errorlevel% neq 0 (
        echo        [WARNING] Backend may need more time to start.
    ) else (
        echo        [OK] Backend running.
    )
) else (
    echo        [OK] Backend running on http://localhost:8000
)

:: Start Frontend
echo.
echo  [3/3] Starting frontend...
start "SRA Frontend" /min cmd /c "cd /d "%~dp0frontend" && npm run dev"
timeout /t 5 /nobreak >nul
echo        [OK] Frontend starting on http://localhost:1420

:: Open browser
echo.
echo  ============================================================
echo   All services started! Opening browser...
echo  ============================================================
echo.
echo   App:     http://localhost:1420
echo   API:     http://localhost:8000/docs
echo   Health:  http://localhost:8000/api/v1/health
echo.
echo   Close this window to stop monitoring.
echo   Use STOP_SRA.bat to stop all services.
echo  ============================================================
echo.

timeout /t 2 /nobreak >nul
start "" http://localhost:1420

:: Keep alive and monitor
:loop
timeout /t 30 /nobreak >nul
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% neq 0 (
    echo  [%time%] WARNING: Backend not responding.
)
goto loop
