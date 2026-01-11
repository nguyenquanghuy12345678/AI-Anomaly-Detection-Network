@echo off
cd /d "%~dp0nginx-1.24.0"
echo Starting Nginx...
start nginx.exe
echo Nginx started!
echo.
echo Frontend: http://localhost
echo Backend API: http://localhost/api/health
echo.
pause
