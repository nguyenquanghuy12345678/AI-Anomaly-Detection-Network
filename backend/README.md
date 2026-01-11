# AI Anomaly Detection Network - Backend

Backend API server cho hệ thống phát hiện anomaly mạng với tích hợp Zabbix, PostgreSQL, Redis, và AI/ML.

## 🏗️ Kiến trúc

```
backend/
├── api/                    # REST API endpoints
│   ├── anomalies.py       # Anomaly detection endpoints
│   ├── alerts.py          # Alert management
│   ├── traffic.py         # Network traffic data
│   ├── connections.py     # Active connections
│   ├── model.py           # AI/ML model endpoints
│   └── system.py          # System status
├── models/                 # Database models
│   ├── anomaly.py
│   ├── alert.py
│   ├── network_traffic.py
│   ├── connection.py
│   └── model_metrics.py
├── services/              # Business logic services
│   ├── ml_service.py      # AI/ML anomaly detection
│   ├── zabbix_service.py  # Zabbix integration
│   ├── websocket_service.py  # Real-time updates
│   ├── cache_service.py   # Redis caching
│   └── monitoring_service.py  # Network monitoring
├── utils/                 # Utilities
│   └── data_generator.py  # Test data generation
├── app.py                 # Main application
├── config.py              # Configuration
├── database.py            # Database initialization
└── docker-compose.yml     # Docker orchestration
```

## 🚀 Cài đặt

### Yêu cầu
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### Bước 1: Clone và setup môi trường

```bash
cd backend
cp .env.example .env
# Chỉnh sửa .env với thông tin cấu hình của bạn
```

### Bước 2: Khởi động services với Docker

```bash
docker-compose up -d
```

Services sẽ được khởi động:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Zabbix Server: `localhost:10051`
- Zabbix Web: `http://localhost:8080`
- Backend API: `http://localhost:5000`

### Bước 3: Cài đặt dependencies (cho development)

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt packages
pip install -r requirements.txt
```

### Bước 4: Khởi tạo database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
```

### Bước 5: Generate demo data (optional)

```bash
python utils/data_generator.py
```

### Bước 6: Chạy application

```bash
python app.py
```

API sẽ chạy tại: `http://localhost:5000`

## 📡 API Endpoints

### Anomalies
- `GET /api/anomalies` - Lấy danh sách anomalies (phân trang)
- `GET /api/anomalies/recent` - Lấy anomalies gần đây
- `GET /api/anomalies/stats` - Thống kê anomalies
- `GET /api/anomalies/:id` - Chi tiết anomaly
- `POST /api/anomalies/:id/block` - Block anomaly

### Alerts
- `GET /api/alerts` - Lấy tất cả alerts
- `GET /api/alerts/unread` - Lấy alerts chưa đọc
- `PUT /api/alerts/:id/read` - Đánh dấu đã đọc
- `DELETE /api/alerts/:id` - Xóa alert

### Traffic
- `GET /api/traffic` - Lấy dữ liệu traffic
- `GET /api/traffic/stats` - Thống kê network
- `GET /api/traffic/recent` - Traffic gần đây

### AI Model
- `GET /api/model/status` - Trạng thái model
- `GET /api/model/metrics` - Performance metrics
- `POST /api/model/predict` - Dự đoán anomaly
- `POST /api/model/retrain` - Retrain model

### System
- `GET /api/system/status` - Trạng thái hệ thống
- `GET /api/system/health` - Health check
- `GET /api/system/metrics` - System metrics

### WebSocket Events
- `connected` - Kết nối thành công
- `anomaly` - Anomaly mới phát hiện
- `traffic` - Cập nhật traffic
- `alert` - Alert mới
- `status` - Cập nhật trạng thái hệ thống

## 🤖 AI/ML Model

Backend sử dụng **Isolation Forest** để phát hiện anomaly:

- **Algorithm**: Isolation Forest (scikit-learn)
- **Features**: Source/Dest ports, bytes, packets, protocol, time
- **Threshold**: 0.7 (có thể cấu hình)
- **Training**: Auto-retrain mỗi 24h hoặc manual trigger

### Sử dụng Model

```python
from services.ml_service import MLService

ml_service = MLService()

# Predict
data = {
    'sourcePort': 12345,
    'destinationPort': 80,
    'bytes': 5000,
    'packets': 100,
    'protocol': 'TCP'
}

result = ml_service.predict(data)
# {'prediction': 'anomaly', 'confidence': 0.85, 'severity': 'high'}
```

## 📊 Zabbix Integration

Backend tích hợp với Zabbix để:
- Thu thập network metrics
- Nhận alerts từ Zabbix
- Monitor system health
- Tạo triggers tự động

### Cấu hình Zabbix

1. Truy cập Zabbix Web: `http://localhost:8080`
2. Login: `Admin` / `zabbix`
3. Tạo host để monitor
4. Configure items và triggers

## 🗄️ Database Schema

### Tables
- `anomalies` - Anomaly records
- `alerts` - Alert notifications
- `network_traffic` - Traffic metrics (TimescaleDB)
- `connections` - Active connections
- `model_metrics` - AI model performance

## 🔧 Configuration

Chỉnh sửa `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Zabbix
ZABBIX_API_URL=http://localhost:8080/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix

# AI/ML
PREDICTION_THRESHOLD=0.7
MODEL_PATH=./models
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📈 Monitoring & Logging

Logs được lưu tại: `./logs/app.log`

```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Rebuild
docker-compose up -d --build
```

## 🔐 Security

- ✅ CORS configured
- ✅ Input validation với Pydantic
- ✅ SQL Injection protection với SQLAlchemy ORM
- ⚠️ Authentication chưa implement (TODO)
- ⚠️ HTTPS chưa configure (TODO)

## 🚧 TODO

- [ ] Implement JWT authentication
- [ ] Add rate limiting
- [ ] Setup HTTPS/SSL
- [ ] Add comprehensive tests
- [ ] Implement dataset training pipeline
- [ ] Add more ML models (LSTM, Autoencoder)
- [ ] Setup CI/CD pipeline
- [ ] Add API documentation (Swagger)

## 📝 License

MIT License

## 👥 Contributors

AI Anomaly Detection Team
