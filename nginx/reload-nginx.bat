@echo off
cd /d "%~dp0nginx-1.24.0"
echo Reloading Nginx configuration...
nginx.exe -s reload
echo Configuration reloaded!
pause
