@echo off
cd /d "%~dp0nginx-1.24.0"
echo Stopping Nginx...
nginx.exe -s quit
echo Nginx stopped!
pause
