# 🐧 Hướng dẫn Chạy trên Ubuntu Linux

## 📋 Yêu cầu hệ thống

- Ubuntu 20.04+ (hoặc Debian-based distro)
- Python 3.9+
- Docker & Docker Compose (tùy chọn)
- 2GB RAM (tối thiểu), 4GB RAM (khuyến nghị)
- 10GB disk space

---

## 🚀 Cách 1: Docker Compose (Khuyến nghị - Đơn giản nhất)

### Bước 1: Cài đặt Docker

```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (không cần sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### Bước 2: Clone và chạy project

```bash
# Clone repository
git clone https://github.com/nguyenquanghuy12345678/AI-Anomaly-Detection-Network.git
cd AI-Anomaly-Detection-Network/backend

# Tạo file environment
cp .env.example .env
# Hoặc tạo .env với nội dung mẫu bên dưới

# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f backend
```

### Bước 3: Kiểm tra

```bash
# Check services status
docker-compose ps

# Test API
curl http://localhost:5000/api/health

# Truy cập ứng dụng
# Frontend: http://localhost:8080 (Zabbix)
# Backend API: http://localhost:5000
```

### Quản lý Docker services

```bash
# Dừng services
docker-compose stop

# Khởi động lại
docker-compose restart

# Xóa containers
docker-compose down

# Xóa cả volumes (data)
docker-compose down -v
```

---

## 🔧 Cách 2: Cài đặt thủ công (Development)

### Bước 1: Cài đặt dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & tools
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib redis-server \
    libpq-dev gcc g++ libpcap-dev tcpdump \
    nginx curl git

# Start services
sudo systemctl start postgresql redis-server
sudo systemctl enable postgresql redis-server
```

### Bước 2: Setup Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Trong PostgreSQL shell:
CREATE DATABASE anomaly_detection;
CREATE USER anomaly_user WITH PASSWORD 'anomaly_pass';
GRANT ALL PRIVILEGES ON DATABASE anomaly_detection TO anomaly_user;
\q
```

### Bước 3: Setup Backend

```bash
# Clone project
git clone https://github.com/nguyenquanghuy12345678/AI-Anomaly-Detection-Network.git
cd AI-Anomaly-Detection-Network/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
API_PORT=5000

# Database
DATABASE_URL=postgresql://anomaly_user:anomaly_pass@localhost:5432/anomaly_detection

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# Zabbix (optional)
ZABBIX_API_URL=http://localhost:8080/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
EOF

# Initialize database
python setup.py

# Run application
python app.py
```

### Bước 4: Setup Frontend

```bash
# Mở terminal mới
cd AI-Anomaly-Detection-Network/frontend

# Serve với Python HTTP server
python3 -m http.server 3000

# Hoặc dùng Nginx (xem bên dưới)
```

---

## 🚀 Cách 3: Production với Gunicorn + Nginx

### Setup Backend với Gunicorn

```bash
cd AI-Anomaly-Detection-Network/backend
source .venv/bin/activate

# Install Gunicorn
pip install gunicorn eventlet

# Chạy với Gunicorn
chmod +x production.sh
./production.sh

# Hoặc chạy trực tiếp:
gunicorn --config gunicorn.conf.py wsgi:application
```

### Setup Nginx

```bash
# Copy Nginx config
sudo cp nginx/nginx.conf /etc/nginx/sites-available/ai-anomaly-detection

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-anomaly-detection \
            /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Tạo Systemd Service (Auto-start)

```bash
# Tạo service file
sudo nano /etc/systemd/system/ai-anomaly-detection.service
```

Nội dung file:

```ini
[Unit]
Description=AI Anomaly Detection Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-anomaly-detection/backend
Environment="PATH=/opt/ai-anomaly-detection/backend/.venv/bin"
ExecStart=/opt/ai-anomaly-detection/backend/.venv/bin/gunicorn \
    --config gunicorn.conf.py wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Kích hoạt service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable và start service
sudo systemctl enable ai-anomaly-detection
sudo systemctl start ai-anomaly-detection

# Check status
sudo systemctl status ai-anomaly-detection

# View logs
sudo journalctl -u ai-anomaly-detection -f
```

---

## 🔥 Cách 4: Quick Start Script (Tự động)

```bash
# Clone project
git clone https://github.com/nguyenquanghuy12345678/AI-Anomaly-Detection-Network.git
cd AI-Anomaly-Detection-Network/backend

# Chạy script tự động
chmod +x start.sh
./start.sh
```

Script sẽ tự động:
- Tạo virtual environment
- Cài dependencies
- Khởi động với Gunicorn

---

## 📊 Kiểm tra & Test

### Health Check

```bash
# Check backend
curl http://localhost:5000/api/health

# Check với jq (pretty JSON)
sudo apt install jq
curl -s http://localhost:5000/api/health | jq
```

### Test API endpoints

```bash
# Recent anomalies
curl http://localhost:5000/api/anomalies/recent

# System status
curl http://localhost:5000/api/system/status

# Traffic stats
curl http://localhost:5000/api/traffic/stats
```

### Monitor logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Nginx access log
sudo tail -f /var/log/nginx/access.log

# Nginx error log
sudo tail -f /var/log/nginx/error.log

# System journal
sudo journalctl -f
```

---

## 🔧 Troubleshooting

### Port đã được sử dụng

```bash
# Check port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Permission issues

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/AI-Anomaly-Detection-Network

# Fix execute permissions
chmod +x backend/*.sh
```

### Database connection error

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check if database exists
sudo -u postgres psql -l | grep anomaly
```

### Redis connection error

```bash
# Check Redis
redis-cli ping

# Restart Redis
sudo systemctl restart redis-server

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Missing dependencies

```bash
# Reinstall Python packages
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## 🛡️ Security & Production Tips

### Firewall Setup

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend (nếu expose public)
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Environment Variables Security

```bash
# Secure .env file
chmod 600 backend/.env
chown $USER:$USER backend/.env

# Never commit .env to git
echo ".env" >> .gitignore
```

---

## 📱 Access Points

Sau khi setup thành công:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost | Web Dashboard |
| **Backend API** | http://localhost/api | REST API |
| **Health Check** | http://localhost/api/health | Status endpoint |
| **Zabbix** | http://localhost:8080 | Monitoring (nếu dùng Docker) |
| **WebSocket** | ws://localhost/socket.io | Real-time updates |

---

## 🎯 Recommendations

**Development:** Dùng **Python HTTP server** hoặc **start.sh**
**Production:** Dùng **Docker Compose** hoặc **Gunicorn + Nginx + Systemd**

Để deploy production đầy đủ:
```bash
# Chạy script deploy tự động
cd backend
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

---

## 📚 Tài liệu thêm

- [QUICKSTART.md](backend/QUICKSTART.md) - Hướng dẫn khởi động nhanh
- [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) - Setup production chi tiết
- [NGINX_SETUP.md](NGINX_SETUP.md) - Cấu hình Nginx
- [AI_ML_SETUP.md](backend/AI_ML_SETUP.md) - Setup ML models

---

## ❓ Cần giúp đỡ?

- Check logs: `docker-compose logs -f` hoặc `sudo journalctl -f`
- GitHub Issues: https://github.com/nguyenquanghuy12345678/AI-Anomaly-Detection-Network/issues
- Documentation: Đọc các file .md trong project
