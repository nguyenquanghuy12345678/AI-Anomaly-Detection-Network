@echo off
title AI Anomaly Detection - Status Check
color 0B

echo ================================================
echo   AI ANOMALY DETECTION - STATUS CHECK
echo ================================================
echo.

echo [1] Checking Nginx Processes...
tasklist | find /i "nginx.exe" >nul
if %errorlevel% equ 0 (
    echo   [OK] Nginx is running
    tasklist | find /i "nginx.exe"
) else (
    echo   [X] Nginx is NOT running
)

echo.
echo [2] Checking Backend (Python)...
curl.exe http://127.0.0.1:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Backend is running on port 5000
    curl.exe http://127.0.0.1:5000/api/health
) else (
    echo   [X] Backend is NOT running
)

echo.
echo [3] Checking Nginx Proxy...
curl.exe http://localhost/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Nginx proxy is working
    curl.exe http://localhost/api/health
) else (
    echo   [X] Nginx proxy is NOT working
)

echo.
echo [4] Checking Frontend...
curl.exe -I http://localhost/ 2>&1 | find "200 OK" >nul
if %errorlevel% equ 0 (
    echo   [OK] Frontend is accessible
) else (
    echo   [X] Frontend is NOT accessible
)

echo.
echo [5] Port Status...
echo   Port 80 (Nginx):
netstat -ano | findstr :80 | findstr LISTENING
echo   Port 5000 (Backend):
netstat -ano | findstr :5000 | findstr LISTENING

echo.
echo ================================================
echo   QUICK ACTIONS
echo ================================================
echo   1. Start Everything:  start-with-nginx.bat
echo   2. Stop Nginx:        nginx\stop-nginx.bat
echo   3. Reload Nginx:      nginx\reload-nginx.bat
echo   4. View Logs:         nginx\nginx-1.24.0\logs\error.log
echo   5. Open Browser:      http://localhost
echo ================================================
echo.
pause
