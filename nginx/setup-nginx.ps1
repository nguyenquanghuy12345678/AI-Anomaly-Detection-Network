# ================================================
# Nginx Setup Script for Windows
# AI Anomaly Detection System
# ================================================

Write-Host "=== Nginx Installation and Configuration ===" -ForegroundColor Green
Write-Host ""

# Configuration
$NginxVersion = "1.24.0"
$NginxUrl = "http://nginx.org/download/nginx-$NginxVersion.zip"
$ProjectRoot = "D:\CODE_WORD\AI-Anomaly-Detection-Network"
$NginxDir = Join-Path $ProjectRoot "nginx"
$NginxBinDir = Join-Path $NginxDir "nginx-$NginxVersion"
$DownloadPath = Join-Path $NginxDir "nginx.zip"

# Create nginx directory if not exists
if (-not (Test-Path $NginxDir)) {
    New-Item -ItemType Directory -Path $NginxDir | Out-Null
}

# Step 1: Download Nginx
Write-Host "[1/6] Downloading Nginx $NginxVersion..." -ForegroundColor Cyan
if (Test-Path $NginxBinDir) {
    Write-Host "  Nginx already downloaded. Skipping..." -ForegroundColor Yellow
} else {
    try {
        Invoke-WebRequest -Uri $NginxUrl -OutFile $DownloadPath -UseBasicParsing
        Write-Host "  Download complete!" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Failed to download Nginx: $_" -ForegroundColor Red
        exit 1
    }
    
    # Extract
    Write-Host "[2/6] Extracting Nginx..." -ForegroundColor Cyan
    try {
        Expand-Archive -Path $DownloadPath -DestinationPath $NginxDir -Force
        Remove-Item $DownloadPath
        Write-Host "  Extraction complete!" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Failed to extract Nginx: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Configure paths for Windows
Write-Host "[3/6] Configuring Nginx for Windows..." -ForegroundColor Cyan

$FrontendPath = Join-Path $ProjectRoot "frontend"
$FrontendPath = $FrontendPath -replace '\\', '/'

# Create Windows-specific nginx.conf
$NginxConfContent = @"
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
    
    # Upstream backend
    upstream backend_api {
        server 127.0.0.1:5000;
        keepalive 32;
    }
    
    server {
        listen       80;
        server_name  localhost;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Frontend static files
        location / {
            root   $FrontendPath;
            index  index.html;
            try_files `$uri `$uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
        
        # Backend API
        location /api/ {
            proxy_pass http://backend_api;
            proxy_http_version 1.1;
            
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
            proxy_set_header Connection "";
            
            # CORS
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
            
            if (`$request_method = OPTIONS) {
                return 204;
            }
        }
        
        # WebSocket - Socket.IO
        location /socket.io/ {
            proxy_pass http://backend_api;
            proxy_http_version 1.1;
            
            # WebSocket headers
            proxy_set_header Upgrade `$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            
            proxy_buffering off;
            proxy_read_timeout 86400;
        }
        
        # Health check
        location /api/health {
            proxy_pass http://backend_api;
            access_log off;
        }
    }
}
"@

# Write nginx.conf
$NginxConfPath = Join-Path $NginxBinDir "conf\nginx.conf"
$NginxConfContent | Out-File -FilePath $NginxConfPath -Encoding UTF8 -Force
Write-Host "  Configuration created at: $NginxConfPath" -ForegroundColor Green

# Step 3: Create start/stop scripts
Write-Host "[4/6] Creating control scripts..." -ForegroundColor Cyan

# Start script
$StartScript = @"
@echo off
cd /d "%~dp0nginx-$NginxVersion"
echo Starting Nginx...
start nginx.exe
echo Nginx started!
echo.
echo Frontend: http://localhost
echo Backend API: http://localhost/api/health
echo.
pause
"@

$StartScript | Out-File -FilePath (Join-Path $NginxDir "start-nginx.bat") -Encoding ASCII -Force

# Stop script
$StopScript = @"
@echo off
cd /d "%~dp0nginx-$NginxVersion"
echo Stopping Nginx...
nginx.exe -s quit
echo Nginx stopped!
pause
"@

$StopScript | Out-File -FilePath (Join-Path $NginxDir "stop-nginx.bat") -Encoding ASCII -Force

# Reload script
$ReloadScript = @"
@echo off
cd /d "%~dp0nginx-$NginxVersion"
echo Reloading Nginx configuration...
nginx.exe -s reload
echo Configuration reloaded!
pause
"@

$ReloadScript | Out-File -FilePath (Join-Path $NginxDir "reload-nginx.bat") -Encoding ASCII -Force

Write-Host "  Control scripts created!" -ForegroundColor Green

# Step 4: Test configuration
Write-Host "[5/6] Testing Nginx configuration..." -ForegroundColor Cyan
Set-Location $NginxBinDir
$TestResult = & ".\nginx.exe" -t 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Configuration test passed!" -ForegroundColor Green
} else {
    Write-Host "  Configuration test output:" -ForegroundColor Yellow
    Write-Host "  $TestResult" -ForegroundColor Yellow
}

# Step 5: Check if backend is running
Write-Host "[6/6] Checking backend status..." -ForegroundColor Cyan
try {
    $Response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "  Backend is running!" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Backend is not running on port 5000" -ForegroundColor Yellow
    Write-Host "  You need to start the backend before accessing the application" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Control Scripts:" -ForegroundColor Cyan
Write-Host "  Start:  nginx\start-nginx.bat" -ForegroundColor White
Write-Host "  Stop:   nginx\stop-nginx.bat" -ForegroundColor White
Write-Host "  Reload: nginx\reload-nginx.bat" -ForegroundColor White
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost" -ForegroundColor White
Write-Host "  API:      http://localhost/api/" -ForegroundColor White
Write-Host "  Health:   http://localhost/api/health" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend: cd backend && python app.py" -ForegroundColor White
Write-Host "  2. Start Nginx: cd nginx && .\start-nginx.bat" -ForegroundColor White
Write-Host "  3. Open browser: http://localhost" -ForegroundColor White
Write-Host ""

# Ask to start Nginx now
$StartNow = Read-Host "Do you want to start Nginx now? (Y/N)"
if ($StartNow -eq "Y" -or $StartNow -eq "y") {
    Write-Host ""
    Write-Host "Starting Nginx..." -ForegroundColor Green
    Set-Location $NginxBinDir
    Start-Process "nginx.exe" -WindowStyle Hidden
    Start-Sleep -Seconds 2
    
    # Verify Nginx is running
    $NginxProcess = Get-Process -Name nginx -ErrorAction SilentlyContinue
    if ($NginxProcess) {
        Write-Host "Nginx started successfully!" -ForegroundColor Green
        Write-Host "Open http://localhost in your browser" -ForegroundColor Cyan
        
        # Open browser
        Start-Process "http://localhost"
    } else {
        Write-Host "Failed to start Nginx. Check logs for errors." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
