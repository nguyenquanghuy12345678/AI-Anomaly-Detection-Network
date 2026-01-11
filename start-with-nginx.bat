@echo off
title AI Anomaly Detection - Quick Start with Nginx
color 0A

echo ================================================
echo   AI ANOMALY DETECTION SYSTEM
echo   Quick Start with Nginx
echo ================================================
echo.

REM Check if Nginx is installed
if not exist "nginx\nginx-1.24.0\nginx.exe" (
    echo [!] Nginx not found. Running setup...
    echo.
    cd nginx
    call setup-nginx.bat
    cd ..
    echo.
    echo Press any key to continue...
    pause >nul
    cls
)

echo [1/4] Checking Backend...
curl.exe http://127.0.0.1:5000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo   Backend not running. Starting...
    cd backend
    start "Backend Server" cmd /k "python app.py"
    cd ..
    echo   Waiting for backend to start...
    timeout /t 5 /nobreak >nul
) else (
    echo   Backend already running!
)

echo.
echo [2/4] Stopping existing Nginx...
cd nginx\nginx-1.24.0
nginx.exe -s quit >nul 2>&1
timeout /t 2 /nobreak >nul
cd ..\..

echo.
echo [3/4] Starting Nginx...
cd nginx\nginx-1.24.0
start /B nginx.exe
cd ..\..
timeout /t 2 /nobreak >nul

REM Verify Nginx started
tasklist | find /i "nginx.exe" >nul
if %errorlevel% equ 0 (
    echo   Nginx started successfully!
) else (
    echo   [!] Failed to start Nginx. Check logs.
    pause
    exit /b 1
)

echo.
echo [4/4] Opening application...
timeout /t 2 /nobreak >nul
start http://localhost

echo.
echo ================================================
echo   APPLICATION STARTED!
echo ================================================
echo.
echo   Frontend:   http://localhost
echo   API:        http://localhost/api/health
echo   WebSocket:  http://localhost/test-websocket.html
echo.
echo   Control:
echo   - Stop Nginx:   nginx\stop-nginx.bat
echo   - Reload:       nginx\reload-nginx.bat
echo   - View Logs:    nginx\nginx-1.24.0\logs\
echo.
echo ================================================
echo.
pause
