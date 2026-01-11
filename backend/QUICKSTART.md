# Quick Start Guide

## Khởi động nhanh Backend

### Option 1: Docker (Khuyến nghị)

```bash
# 1. Clone repo và di chuyển vào thư mục backend
cd backend

# 2. Copy và chỉnh sửa file environment
cp .env.example .env
# Chỉnh sửa .env nếu cần

# 3. Khởi động tất cả services
docker-compose up -d

# 4. Kiểm tra logs
docker-compose logs -f backend

# 5. Truy cập
# API: http://localhost:5000
# Zabbix: http://localhost:8080 (Admin/zabbix)
```

### Option 2: Local Development

```bash
# 1. Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Copy environment file
cp .env.example .env

# 4. Chạy setup script
python setup.py

# 5. Khởi động services cần thiết (PostgreSQL, Redis)
docker-compose up -d postgres redis

# 6. Chạy application
python app.py
```

## Kiểm tra Backend

```bash
# Health check
curl http://localhost:5000/api/health

# Get anomalies
curl http://localhost:5000/api/anomalies

# Get system status
curl http://localhost:5000/api/system/status
```

## Cấu trúc Project

```
backend/
├── api/              # REST API endpoints
├── models/           # Database models (SQLAlchemy)
├── services/         # Business logic
│   ├── ml_service.py        # AI/ML anomaly detection
│   ├── zabbix_service.py    # Zabbix integration
│   ├── websocket_service.py # Real-time WebSocket
│   ├── cache_service.py     # Redis caching
│   └── monitoring_service.py # Network monitoring
├── utils/            # Utilities
├── app.py           # Main application
├── config.py        # Configuration
├── database.py      # Database setup
└── docker-compose.yml
```

## Các Tính Năng Đã Implement

### ✅ REST API (20+ endpoints)
- Anomaly management (CRUD)
- Alert system
- Network traffic monitoring
- AI model status & prediction
- System health checks

### ✅ WebSocket Real-time
- Live anomaly notifications
- Traffic updates
- Alert broadcasts
- Status changes

### ✅ Database (PostgreSQL)
- 5 tables với relationships
- Indexes cho performance
- TimescaleDB support (optional)

### ✅ AI/ML Module
- Isolation Forest model
- Feature engineering
- Real-time prediction
- Model training pipeline

### ✅ Zabbix Integration
- API connection
- Metrics collection
- Alert synchronization
- Host monitoring

### ✅ Caching (Redis)
- Session management
- Real-time data caching
- Pub/sub for WebSocket

### ✅ Monitoring Service
- Auto-generate mock data
- Background processing
- Real-time metrics collection

### ✅ Docker Support
- Multi-container setup
- PostgreSQL + Redis + Zabbix
- Auto-initialization
- Volume persistence

## Troubleshooting

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U anomaly_user -d anomaly_detection
```

### Redis connection error
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

### Zabbix not accessible
```bash
# Check Zabbix services
docker-compose ps | grep zabbix

# Wait for initialization (first time takes 2-3 minutes)
docker-compose logs -f zabbix_server
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# PostgreSQL: 5432 -> 5433
# Redis: 6379 -> 6380
# Backend: 5000 -> 5001
# Zabbix: 8080 -> 8081
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## Development Tips

### Add new API endpoint
1. Create function in `api/your_module.py`
2. Register blueprint in `api/__init__.py`
3. Test with curl or Postman

### Add new model
1. Create model in `models/your_model.py`
2. Import in `models/__init__.py`
3. Run migration: `db.create_all()`

### Add new service
1. Create service in `services/your_service.py`
2. Import in relevant API endpoint
3. Use service in routes

## Production Deployment

### Security Checklist
- [ ] Change all default passwords
- [ ] Setup HTTPS/SSL
- [ ] Enable authentication (JWT)
- [ ] Configure firewall rules
- [ ] Setup rate limiting
- [ ] Enable CORS whitelist
- [ ] Secure environment variables
- [ ] Setup monitoring/logging

### Performance Optimization
- [ ] Enable Redis caching
- [ ] Setup connection pooling
- [ ] Configure nginx load balancing
- [ ] Optimize database queries
- [ ] Enable compression
- [ ] Setup CDN for static files

## Tài liệu bổ sung

- [API Documentation](docs/api.md) - Coming soon
- [Database Schema](docs/database.md) - Coming soon
- [ML Model Guide](docs/ml-model.md) - Coming soon
- [Zabbix Setup](docs/zabbix.md) - Coming soon
