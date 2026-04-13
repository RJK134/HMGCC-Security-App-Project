@echo off
title Security Research Assistant - Shutdown
echo.
echo  Stopping SRA services...
echo.
taskkill /FI "WINDOWTITLE eq SRA Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq SRA Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Security Research Assistant*" /F >nul 2>&1
echo  [OK] All SRA services stopped.
echo  (Ollama left running - close it from the system tray if needed)
echo.
pause
