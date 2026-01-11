"""
Configuration module for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://anomaly_user:anomaly_pass@localhost:5432/anomaly_detection')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Zabbix
    ZABBIX_SERVER = os.getenv('ZABBIX_SERVER', 'http://localhost:8080')
    ZABBIX_USER = os.getenv('ZABBIX_USER', 'Admin')
    ZABBIX_PASSWORD = os.getenv('ZABBIX_PASSWORD', 'zabbix')
    ZABBIX_API_URL = os.getenv('ZABBIX_API_URL', 'http://localhost:8080/api_jsonrpc.php')
    
    # AI/ML
    MODEL_PATH = os.getenv('MODEL_PATH', './models')
    MODEL_VERSION = os.getenv('MODEL_VERSION', '1.0.0')
    PREDICTION_THRESHOLD = float(os.getenv('PREDICTION_THRESHOLD', 0.7))
    RETRAIN_INTERVAL = int(os.getenv('RETRAIN_INTERVAL', 86400))
    
    # Network Monitoring
    INTERFACE = os.getenv('INTERFACE', 'eth0')
    PACKET_CAPTURE_ENABLED = os.getenv('PACKET_CAPTURE_ENABLED', 'true').lower() == 'true'
    TRAFFIC_WINDOW = int(os.getenv('TRAFFIC_WINDOW', 300))
    
    # GeoIP
    GEOIP_DB_PATH = os.getenv('GEOIP_DB_PATH', './data/GeoLite2-City.mmdb')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    # WebSocket
    WEBSOCKET_PING_TIMEOUT = int(os.getenv('WEBSOCKET_PING_TIMEOUT', 60))
    WEBSOCKET_PING_INTERVAL = int(os.getenv('WEBSOCKET_PING_INTERVAL', 25))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
