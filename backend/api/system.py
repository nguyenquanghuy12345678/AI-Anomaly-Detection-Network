"""
System API endpoints
"""
from flask import Blueprint, jsonify
from database import db
from datetime import datetime
import psutil
import os

system_bp = Blueprint('system', __name__)

@system_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get system status"""
    # Check database connection
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except:
        db_status = 'offline'
    
    # Check Redis connection
    try:
        from services.cache_service import cache
        cache.ping()
        redis_status = 'healthy'
    except:
        redis_status = 'offline'
    
    # AI Model status
    from models.model_metrics import ModelMetrics
    latest_metrics = ModelMetrics.query.order_by(ModelMetrics.timestamp.desc()).first()
    model_status = latest_metrics.status if latest_metrics else 'offline'
    
    return jsonify({
        'database': db_status,
        'redis': redis_status,
        'aiModel': model_status,
        'networkMonitor': 'active',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@system_bp.route('/health', methods=['GET'])
def health_check():
    """System health check"""
    try:
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            'status': 'healthy',
            'uptime': datetime.utcnow().isoformat(),
            'cpu': {
                'usage': cpu_percent,
                'cores': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@system_bp.route('/metrics', methods=['GET'])
def get_system_metrics():
    """Get detailed system metrics"""
    try:
        # Network I/O
        net_io = psutil.net_io_counters()
        
        return jsonify({
            'network': {
                'bytesSent': net_io.bytes_sent,
                'bytesRecv': net_io.bytes_recv,
                'packetsSent': net_io.packets_sent,
                'packetsRecv': net_io.packets_recv
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
