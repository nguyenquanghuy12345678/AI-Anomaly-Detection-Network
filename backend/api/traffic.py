"""
Traffic API endpoints
"""
from flask import Blueprint, request, jsonify
from models.network_traffic import NetworkTraffic
from database import db
from datetime import datetime, timedelta

traffic_bp = Blueprint('traffic', __name__)

@traffic_bp.route('/', methods=['GET'])
def get_traffic():
    """Get network traffic data"""
    time_range = request.args.get('timeRange', '1h')
    
    if time_range == '1h':
        since = datetime.utcnow() - timedelta(hours=1)
    elif time_range == '24h':
        since = datetime.utcnow() - timedelta(days=1)
    elif time_range == '7d':
        since = datetime.utcnow() - timedelta(days=7)
    elif time_range == '30d':
        since = datetime.utcnow() - timedelta(days=30)
    else:
        since = datetime.utcnow() - timedelta(hours=1)
    
    traffic_data = NetworkTraffic.query.filter(
        NetworkTraffic.timestamp >= since
    ).order_by(NetworkTraffic.timestamp.asc()).all()
    
    return jsonify({
        'traffic': [t.to_dict() for t in traffic_data],
        'timeRange': time_range
    }), 200

@traffic_bp.route('/stats', methods=['GET'])
def get_traffic_stats():
    """Get network statistics"""
    # Get latest traffic record
    latest = NetworkTraffic.query.order_by(NetworkTraffic.timestamp.desc()).first()
    
    if not latest:
        return jsonify({
            'totalTraffic': 0,
            'anomalyCount': 0,
            'blockedThreats': 0,
            'avgResponseTime': 0,
            'activeConnections': 0,
            'detectionRate': 0
        }), 200
    
    # Calculate averages over last hour
    since = datetime.utcnow() - timedelta(hours=1)
    recent_traffic = NetworkTraffic.query.filter(
        NetworkTraffic.timestamp >= since
    ).all()
    
    avg_traffic = sum(t.total_mbps for t in recent_traffic) / len(recent_traffic) if recent_traffic else 0
    total_anomalies = sum(t.anomaly_count for t in recent_traffic)
    total_blocked = sum(t.blocked_threats for t in recent_traffic)
    avg_response = sum(t.avg_response_time for t in recent_traffic if t.avg_response_time) / len(recent_traffic) if recent_traffic else 0
    
    # Detection rate = blocked / total anomalies * 100
    detection_rate = (total_blocked / total_anomalies * 100) if total_anomalies > 0 else 0
    
    return jsonify({
        'totalTraffic': round(avg_traffic, 2),
        'anomalyCount': total_anomalies,
        'blockedThreats': total_blocked,
        'avgResponseTime': round(avg_response, 2),
        'activeConnections': latest.active_connections,
        'detectionRate': round(detection_rate, 2)
    }), 200

@traffic_bp.route('/recent', methods=['GET'])
def get_recent_traffic():
    """Get most recent traffic data"""
    limit = request.args.get('limit', 10, type=int)
    
    traffic_data = NetworkTraffic.query.order_by(
        NetworkTraffic.timestamp.desc()
    ).limit(limit).all()
    
    return jsonify({
        'traffic': [t.to_dict() for t in reversed(traffic_data)]
    }), 200
