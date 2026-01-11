@echo off
echo ================================================
echo Nginx Setup for Windows
echo AI Anomaly Detection System
echo ================================================
echo.

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0setup-nginx.ps1"

pause
