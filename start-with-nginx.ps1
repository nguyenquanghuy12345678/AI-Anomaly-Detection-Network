# ================================================
# Quick Start Script with Nginx
# AI Anomaly Detection System
# ================================================

$ErrorActionPreference = "Stop"

function Write-Step {
    param($Number, $Total, $Message)
    Write-Host "[$Number/$Total] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "  $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "  $Message" -ForegroundColor Red
}

Clear-Host
Write-Host "================================================" -ForegroundColor Green
Write-Host "  AI ANOMALY DETECTION SYSTEM" -ForegroundColor Green
Write-Host "  Quick Start with Nginx" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

$ProjectRoot = "D:\CODE_WORD\AI-Anomaly-Detection-Network"
Set-Location $ProjectRoot

# Step 1: Check/Install Nginx
Write-Step 1 4 "Checking Nginx..."
$NginxExe = Join-Path $ProjectRoot "nginx\nginx-1.24.0\nginx.exe"
if (-not (Test-Path $NginxExe)) {
    Write-Warning "Nginx not found. Running setup..."
    & ".\nginx\setup-nginx.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Nginx setup failed!"
        exit 1
    }
} else {
    Write-Success "Nginx already installed"
}

# Step 2: Check/Start Backend
Write-Host ""
Write-Step 2 4 "Checking Backend..."
try {
    $Response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -UseBasicParsing -TimeoutSec 2
    Write-Success "Backend already running"
} catch {
    Write-Warning "Backend not running. Starting..."
    $BackendPath = Join-Path $ProjectRoot "backend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendPath'; python app.py" -WindowStyle Normal
    
    Write-Host "  Waiting for backend to start..." -ForegroundColor Yellow
    $MaxRetries = 10
    $RetryCount = 0
    $BackendReady = $false
    
    while ($RetryCount -lt $MaxRetries -and -not $BackendReady) {
        Start-Sleep -Seconds 2
        try {
            $Response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -UseBasicParsing -TimeoutSec 1
            $BackendReady = $true
            Write-Success "Backend started successfully!"
        } catch {
            $RetryCount++
            Write-Host "." -NoNewline
        }
    }
    
    if (-not $BackendReady) {
        Write-Error-Custom "Backend failed to start within 20 seconds"
        Write-Host "Please start backend manually: cd backend && python app.py"
        exit 1
    }
}

# Step 3: Stop existing Nginx
Write-Host ""
Write-Step 3 4 "Managing Nginx..."
Set-Location (Join-Path $ProjectRoot "nginx\nginx-1.24.0")
Write-Host "  Stopping any existing Nginx..." -ForegroundColor Yellow
& ".\nginx.exe" -s quit 2>$null
Start-Sleep -Seconds 2

# Kill any remaining nginx processes
Get-Process -Name nginx -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Step 4: Start Nginx
Write-Host "  Starting Nginx..." -ForegroundColor Yellow
Start-Process -FilePath ".\nginx.exe" -WindowStyle Hidden
Start-Sleep -Seconds 2

# Verify Nginx started
$NginxProcess = Get-Process -Name nginx -ErrorAction SilentlyContinue
if ($NginxProcess) {
    Write-Success "Nginx started successfully!"
    Write-Host "  Processes: $($NginxProcess.Count)" -ForegroundColor Gray
} else {
    Write-Error-Custom "Failed to start Nginx!"
    Write-Host "  Check logs: nginx\nginx-1.24.0\logs\error.log"
    exit 1
}

# Step 5: Verify application
Write-Host ""
Write-Step 4 4 "Verifying Application..."
try {
    $Response = Invoke-WebRequest -Uri "http://localhost/api/health" -UseBasicParsing -TimeoutSec 3
    Write-Success "Application responding correctly!"
    
    # Parse response
    $HealthData = $Response.Content | ConvertFrom-Json
    Write-Host "  Service: $($HealthData.service)" -ForegroundColor Gray
    Write-Host "  Status: $($HealthData.status)" -ForegroundColor Gray
    Write-Host "  Version: $($HealthData.version)" -ForegroundColor Gray
} catch {
    Write-Warning "Application health check failed. May still be starting..."
}

# Step 6: Open browser
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 1
Start-Process "http://localhost"

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  APPLICATION STARTED!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  Frontend:        " -NoNewline; Write-Host "http://localhost" -ForegroundColor White
Write-Host "  API Health:      " -NoNewline; Write-Host "http://localhost/api/health" -ForegroundColor White
Write-Host "  WebSocket Test:  " -NoNewline; Write-Host "http://localhost/test-websocket.html" -ForegroundColor White
Write-Host ""
Write-Host "Control Scripts:" -ForegroundColor Cyan
Write-Host "  Stop Nginx:      " -NoNewline; Write-Host "nginx\stop-nginx.bat" -ForegroundColor White
Write-Host "  Reload Config:   " -NoNewline; Write-Host "nginx\reload-nginx.bat" -ForegroundColor White
Write-Host "  View Logs:       " -NoNewline; Write-Host "nginx\nginx-1.24.0\logs\" -ForegroundColor White
Write-Host ""
Write-Host "Processes:" -ForegroundColor Cyan
$BackendProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object -First 1
$NginxProcesses = Get-Process -Name nginx -ErrorAction SilentlyContinue
Write-Host "  Backend (Python): " -NoNewline
if ($BackendProcess) {
    Write-Host "Running (PID: $($BackendProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "Not detected" -ForegroundColor Yellow
}
Write-Host "  Nginx:            " -NoNewline
if ($NginxProcesses) {
    Write-Host "Running ($($NginxProcesses.Count) processes)" -ForegroundColor Green
} else {
    Write-Host "Not running" -ForegroundColor Red
}
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Set-Location $ProjectRoot
