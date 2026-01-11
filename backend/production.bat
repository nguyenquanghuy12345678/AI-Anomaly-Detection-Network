@echo off
REM Production Start Script for Windows
REM Uses Waitress WSGI server

echo ========================================
echo AI Anomaly Detection - Production Mode
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install dependencies: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if waitress is installed
python -c "import waitress" 2>nul
if errorlevel 1 (
    echo Installing Waitress...
    pip install waitress
)

REM Load environment variables
if exist .env (
    echo Loading environment variables...
    for /F "tokens=*" %%i in (.env) do set %%i
)

REM Start production server
echo.
echo Starting production server with Waitress...
echo.
python production.py
