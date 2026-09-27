@echo off
title VARSHAAI - SIH 26080 Intelligence Launcher
echo ======================================================================
echo   VARSHAAI - Regime-Aware AI Rainfall Forecast Post-Processing
echo ======================================================================
echo Starting FastAPI ML Backend and Launching Web Interface...
echo.

cd /d "%~dp0"

:: Clear corrupted environment variables that cause "No module named encodings"
set "PYTHONHOME="
set "PYTHONPATH="

:: Try the official Windows Python launcher first (py -3)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 run_server.py
    goto end
)

:: Try standard python
python --version >nul 2>&1
if not errorlevel 1 (
    python run_server.py
    goto end
)

echo.
echo Python was not found or has an environment issue.
echo Opening the web interface directly in your default browser...
start "" "%~dp0index.html"

:end
pause
