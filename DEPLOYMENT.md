# Production Deployment Guide
## AI Anomaly Detection System

This guide covers deploying the application to production using Gunicorn and Nginx.

## 📋 Prerequisites

### System Requirements
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.9+
- Nginx 1.18+
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ disk space

### Required Software
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx
```

## 🚀 Quick Deployment (Linux)

### 1. Clone Repository
```bash
sudo mkdir -p /opt/ai-anomaly-detection
cd /opt/ai-anomaly-detection
git clone <repository-url> .
```

### 2. Run Deployment Script
```bash
cd backend
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

The script will automatically:
- ✅ Install dependencies
- ✅ Set up Python virtual environment
- ✅ Configure Gunicorn service
- ✅ Configure Nginx reverse proxy
- ✅ Start all services

## 🔧 Manual Deployment

### Step 1: Set Up Backend

```bash
# Create project directory
sudo mkdir -p /opt/ai-anomaly-detection/backend
cd /opt/ai-anomaly-detection/backend

# Copy backend files
cp -r /path/to/backend/* .

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with production values
```

### Step 2: Configure Gunicorn Service

```bash
# Copy service file
sudo cp ai-anomaly-detection.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/ai-anomaly-detection.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable ai-anomaly-detection
sudo systemctl start ai-anomaly-detection

# Check status
sudo systemctl status ai-anomaly-detection
```

### Step 3: Configure Nginx

```bash
# Copy Nginx configuration
sudo cp /opt/ai-anomaly-detection/nginx/nginx.conf /etc/nginx/sites-available/ai-anomaly-detection

# Edit domain/paths if needed
sudo nano /etc/nginx/sites-available/ai-anomaly-detection

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-anomaly-detection /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 4: Deploy Frontend

```bash
# Copy frontend files
sudo mkdir -p /opt/ai-anomaly-detection/frontend
sudo cp -r /path/to/frontend/* /opt/ai-anomaly-detection/frontend/

# Set permissions
sudo chown -R www-data:www-data /opt/ai-anomaly-detection/frontend
sudo chmod -R 755 /opt/ai-anomaly-detection/frontend
```

## 🔐 SSL/HTTPS Setup (Let's Encrypt)

### Install Certbot
```bash
sudo apt-get install certbot python3-certbot-nginx
```

### Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Auto-renewal
```bash
sudo certbot renew --dry-run
```

## 📊 Service Management

### Backend Service Commands
```bash
# Start
sudo systemctl start ai-anomaly-detection

# Stop
sudo systemctl stop ai-anomaly-detection

# Restart
sudo systemctl restart ai-anomaly-detection

# Status
sudo systemctl status ai-anomaly-detection

# View logs
sudo journalctl -u ai-anomaly-detection -f

# View last 100 lines
sudo journalctl -u ai-anomaly-detection -n 100
```

### Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload (graceful restart)
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# Status
sudo systemctl status nginx

# View access logs
sudo tail -f /var/log/nginx/anomaly_detection_access.log

# View error logs
sudo tail -f /var/log/nginx/anomaly_detection_error.log
```

## 🔍 Health Checks

### Check Backend API
```bash
curl http://localhost/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Anomaly Detection Backend",
  "version": "1.0.0"
}
```

### Check Gunicorn Workers
```bash
ps aux | grep gunicorn
```

### Check Nginx Status
```bash
sudo systemctl status nginx
curl -I http://localhost
```

## 📝 Configuration Files

### Important Paths
- **Backend code**: `/opt/ai-anomaly-detection/backend/`
- **Frontend code**: `/opt/ai-anomaly-detection/frontend/`
- **Virtual env**: `/opt/ai-anomaly-detection/backend/.venv/`
- **Systemd service**: `/etc/systemd/system/ai-anomaly-detection.service`
- **Nginx config**: `/etc/nginx/sites-available/ai-anomaly-detection`
- **Backend logs**: `/opt/ai-anomaly-detection/backend/logs/`
- **Nginx logs**: `/var/log/nginx/anomaly_detection_*.log`

### Environment Variables (.env)
```bash
# Production settings
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
API_PORT=5000

# Database
DATABASE_URL=postgresql://user:pass@localhost/anomaly_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_ACCESS_LOG=/opt/ai-anomaly-detection/backend/logs/access.log
GUNICORN_ERROR_LOG=/opt/ai-anomaly-detection/backend/logs/error.log

# Logging
LOG_LEVEL=INFO
```

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check service logs
sudo journalctl -u ai-anomaly-detection -n 50

# Check Python errors
source /opt/ai-anomaly-detection/backend/.venv/bin/activate
cd /opt/ai-anomaly-detection/backend
python wsgi.py

# Check permissions
ls -la /opt/ai-anomaly-detection/backend
```

### Nginx 502 Bad Gateway
```bash
# Check if backend is running
sudo systemctl status ai-anomaly-detection

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check if port 5000 is listening
sudo netstat -tlnp | grep :5000
```

### WebSocket connection fails
```bash
# Check Nginx WebSocket configuration
sudo nginx -t

# Check browser console for errors
# Verify Socket.IO endpoint: http://your-domain/socket.io/

# Test with curl
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost/socket.io/?transport=websocket
```

### High CPU/Memory usage
```bash
# Check Gunicorn worker count
ps aux | grep gunicorn | wc -l

# Adjust workers in gunicorn.conf.py
# Formula: (2 * CPU cores) + 1

# Restart service
sudo systemctl restart ai-anomaly-detection
```

## 🔄 Updates and Maintenance

### Deploy New Version
```bash
cd /opt/ai-anomaly-detection/backend

# Pull latest code
git pull origin main

# Activate venv
source .venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart ai-anomaly-detection
```

### Database Migrations
```bash
cd /opt/ai-anomaly-detection/backend
source .venv/bin/activate

# Run migrations
python -c "from database import init_db; from app import app; init_db(app)"
```

### Backup
```bash
# Backup database
pg_dump anomaly_detection > backup_$(date +%Y%m%d).sql

# Backup ML models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Backup configuration
cp .env .env.backup
```

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY in .env
- [ ] Set up SSL/HTTPS with Let's Encrypt
- [ ] Configure firewall (UFW/iptables)
- [ ] Enable rate limiting in Nginx
- [ ] Set up fail2ban for SSH
- [ ] Regular security updates: `sudo apt-get update && sudo apt-get upgrade`
- [ ] Configure database user permissions
- [ ] Set up regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Use strong passwords for all services

## 🔥 Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## 📈 Monitoring

### Set Up Monitoring (Optional)
```bash
# Install Prometheus Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
```

### Log Rotation
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/ai-anomaly-detection

# Add configuration:
/opt/ai-anomaly-detection/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ai-anomaly-detection
    endscript
}
```

## 🎯 Performance Tuning

### Gunicorn Workers
```python
# In gunicorn.conf.py
workers = (2 * CPU_COUNT) + 1
worker_class = 'eventlet'  # For Socket.IO
worker_connections = 1000
```

### Nginx Optimization
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
```

## 📞 Support

For issues or questions:
- Check logs: `sudo journalctl -u ai-anomaly-detection -f`
- Review Nginx errors: `sudo tail -f /var/log/nginx/error.log`
- Test API: `curl http://localhost/api/health`

## 🎉 Success!

Your AI Anomaly Detection System should now be running at:
- **Frontend**: `http://your-domain.com`
- **API**: `http://your-domain.com/api`
- **Health Check**: `http://your-domain.com/api/health`
