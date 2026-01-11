# 🚀 Hướng dẫn Chạy Dự án với Nginx

## 📋 Tổng quan

Dự án AI Anomaly Detection chạy với kiến trúc:
- **Nginx** (Port 80): Reverse proxy, serve static files
- **Backend Flask** (Port 5000): API và WebSocket server
- **Frontend**: Static HTML/CSS/JS files

## 🔧 Cài đặt và Khởi động

### Bước 1: Setup Nginx

Chạy script tự động cài đặt:

```powershell
cd nginx
.\setup-nginx.bat
```

Script sẽ:
- ✅ Tải Nginx 1.24.0 từ nginx.org
- ✅ Giải nén và cấu hình cho Windows
- ✅ Tạo nginx.conf với proxy đến backend
- ✅ Tạo scripts start/stop/reload
- ✅ Test cấu hình
- ✅ Hỏi có muốn start Nginx ngay không

**Hoặc cài đặt thủ công:**

```powershell
# Tải Nginx
Invoke-WebRequest -Uri "http://nginx.org/download/nginx-1.24.0.zip" -OutFile "nginx.zip"

# Giải nén
Expand-Archive nginx.zip -DestinationPath .

# Copy nginx.conf vào nginx-1.24.0/conf/
```

### Bước 2: Start Backend

```powershell
cd backend
python app.py
```

Backend sẽ chạy trên http://127.0.0.1:5000

### Bước 3: Start Nginx

```powershell
cd nginx
.\start-nginx.bat
```

Hoặc:

```powershell
cd nginx\nginx-1.24.0
start nginx.exe
```

### Bước 4: Truy cập Application

Mở trình duyệt:
- **Frontend**: http://localhost
- **API Health**: http://localhost/api/health
- **WebSocket Test**: http://localhost/test-websocket.html

## 🎮 Điều khiển Nginx

### Start Nginx
```powershell
cd nginx
.\start-nginx.bat
```

### Stop Nginx
```powershell
cd nginx
.\stop-nginx.bat
```

### Reload Configuration (sau khi sửa nginx.conf)
```powershell
cd nginx
.\reload-nginx.bat
```

### Kiểm tra Nginx đang chạy
```powershell
Get-Process -Name nginx
```

### Kiểm tra cổng 80
```powershell
netstat -ano | findstr :80
```

## 📂 Cấu trúc Nginx

```
nginx/
├── nginx-1.24.0/          # Nginx binary và files
│   ├── nginx.exe          # Nginx executable
│   ├── conf/
│   │   └── nginx.conf     # Configuration file
│   ├── logs/
│   │   ├── access.log     # Access logs
│   │   └── error.log      # Error logs
│   └── html/              # Default HTML (not used)
├── setup-nginx.ps1        # Setup script
├── setup-nginx.bat        # Setup launcher
├── start-nginx.bat        # Start script
├── stop-nginx.bat         # Stop script
└── reload-nginx.bat       # Reload script
```

## ⚙️ Cấu hình Nginx

### nginx.conf chính

```nginx
# Upstream backend
upstream backend_api {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name localhost;
    
    # Frontend static files
    location / {
        root D:/CODE_WORD/AI-Anomaly-Detection-Network/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket proxy
    location /socket.io/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Sửa đổi cấu hình

1. Edit file: `nginx\nginx-1.24.0\conf\nginx.conf`
2. Test cấu hình:
   ```powershell
   cd nginx\nginx-1.24.0
   .\nginx.exe -t
   ```
3. Reload:
   ```powershell
   .\nginx.exe -s reload
   ```

## 🔍 Troubleshooting

### Lỗi: Port 80 đã bị sử dụng

**Kiểm tra process nào đang dùng port 80:**
```powershell
netstat -ano | findstr :80
```

**Giải pháp 1: Dừng process khác**
```powershell
# Tìm PID từ netstat, sau đó:
Stop-Process -Id <PID> -Force
```

**Giải pháp 2: Đổi port Nginx**
Edit `nginx.conf`:
```nginx
server {
    listen 8080;  # Đổi từ 80 sang 8080
    ...
}
```

Truy cập: http://localhost:8080

### Lỗi: 502 Bad Gateway

**Nguyên nhân:** Backend không chạy hoặc không thể connect

**Giải pháp:**
```powershell
# 1. Kiểm tra backend
curl.exe http://127.0.0.1:5000/api/health

# 2. Nếu không response, start backend
cd backend
python app.py

# 3. Reload Nginx
cd ..\nginx
.\reload-nginx.bat
```

### Lỗi: 404 Not Found cho frontend

**Nguyên nhân:** Đường dẫn root sai trong nginx.conf

**Giải pháp:**
1. Kiểm tra đường dẫn frontend:
   ```powershell
   Test-Path "D:\CODE_WORD\AI-Anomaly-Detection-Network\frontend\index.html"
   ```

2. Sửa nginx.conf nếu cần:
   ```nginx
   location / {
       root D:/CODE_WORD/AI-Anomaly-Detection-Network/frontend;
       # Lưu ý: Dùng / thay vì \
   }
   ```

3. Reload Nginx

### WebSocket không kết nối

**Kiểm tra:**
1. Backend có chạy không: http://127.0.0.1:5000/api/health
2. Nginx proxy WebSocket đúng không:
   ```nginx
   location /socket.io/ {
       proxy_pass http://backend_api;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

3. Browser console có errors không (F12)

### Xem Nginx logs

**Access log:**
```powershell
Get-Content nginx\nginx-1.24.0\logs\access.log -Tail 50
```

**Error log:**
```powershell
Get-Content nginx\nginx-1.24.0\logs\error.log -Tail 50
```

**Live monitoring:**
```powershell
Get-Content nginx\nginx-1.24.0\logs\error.log -Wait
```

## 🚀 Production Deployment

### Sử dụng production backend

Thay vì `python app.py`, dùng Waitress:

```powershell
cd backend
python production.py
```

Hoặc Gunicorn (trên Linux):
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

### SSL/HTTPS Configuration

1. Lấy SSL certificate (Let's Encrypt, mkcert, etc.)

2. Update nginx.conf:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of config
}

# HTTP redirect to HTTPS
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

3. Reload Nginx

### Performance Tuning

Edit nginx.conf:
```nginx
worker_processes auto;  # Sử dụng tất cả CPU cores

events {
    worker_connections 4096;  # Tăng connections
    use epoll;  # Linux only
}

http {
    # Caching
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cache:10m;
    
    # Compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Keepalive
    keepalive_timeout 65;
    keepalive_requests 100;
}
```

## 📊 Monitoring

### Check Nginx status
```powershell
curl.exe http://localhost/api/health
```

### Monitor connections
```powershell
netstat -ano | findstr :80
```

### Check process resources
```powershell
Get-Process nginx | Select-Object CPU,WorkingSet,Id
```

## 🔄 Complete Restart

Khởi động lại toàn bộ hệ thống:

```powershell
# 1. Stop everything
cd nginx
.\stop-nginx.bat
Stop-Process -Name python -Force

# 2. Start backend
cd ..\backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py"

# 3. Wait for backend
Start-Sleep -Seconds 5

# 4. Start Nginx
cd ..\nginx
.\start-nginx.bat

# 5. Open browser
Start-Process "http://localhost"
```

## 📝 Quick Reference

| Action | Command |
|--------|---------|
| Setup Nginx | `cd nginx && .\setup-nginx.bat` |
| Start Backend | `cd backend && python app.py` |
| Start Nginx | `cd nginx && .\start-nginx.bat` |
| Stop Nginx | `cd nginx && .\stop-nginx.bat` |
| Reload Config | `cd nginx && .\reload-nginx.bat` |
| Test Config | `cd nginx\nginx-1.24.0 && .\nginx.exe -t` |
| View Logs | `Get-Content nginx\nginx-1.24.0\logs\error.log` |
| Check Health | `curl.exe http://localhost/api/health` |

## 🎯 Advantages của Nginx

**Tại sao dùng Nginx thay vì Flask dev server:**

1. **Performance**: Nginx serve static files nhanh hơn rất nhiều
2. **Production-ready**: Xử lý nhiều concurrent connections
3. **Load Balancing**: Có thể chạy nhiều backend instances
4. **Caching**: Cache API responses, giảm load backend
5. **Security**: Rate limiting, request filtering, SSL/TLS
6. **Reverse Proxy**: Ẩn backend architecture
7. **Compression**: Tự động gzip/brotli compression
8. **WebSocket**: Hỗ trợ WebSocket proxy tốt hơn

## 🌟 Best Practices

1. **Development**: Chạy backend trực tiếp, Nginx serve frontend
2. **Testing**: Dùng Nginx để test giống production
3. **Production**: Nginx + Gunicorn/Waitress + systemd/supervisor
4. **Monitoring**: Log rotation, analytics, error tracking
5. **Security**: HTTPS, rate limiting, firewall rules

---

**Tài liệu này cung cấp mọi thông tin cần thiết để chạy dự án với Nginx!**
