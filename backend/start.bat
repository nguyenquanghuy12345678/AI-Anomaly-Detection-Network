@echo off
REM Quick Start Script for Windows Development
REM Start backend with Gunicorn

echo Starting AI Anomaly Detection Backend...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

REM Load environment variables from .env
if exist .env (
    for /F "tokens=*" %%i in (.env) do set %%i
)

REM Start with Gunicorn
echo.
echo Starting Gunicorn server...
echo.
gunicorn ^
    --config gunicorn.conf.py ^
    --bind 0.0.0.0:5000 ^
    --workers 2 ^
    --worker-class eventlet ^
    --reload ^
    wsgi:application
