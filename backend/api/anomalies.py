"""
Anomalies API endpoints
"""
from flask import Blueprint, request, jsonify
from models.anomaly import Anomaly
from database import db
from datetime import datetime, timedelta
import uuid

anomalies_bp = Blueprint('anomalies', __name__)

@anomalies_bp.route('/', methods=['GET'])
def get_anomalies():
    """Get paginated list of anomalies"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    severity = request.args.get('severity', None)
    status = request.args.get('status', None)
    
    query = Anomaly.query
    
    if severity:
        query = query.filter_by(severity=severity)
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Anomaly.timestamp.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        'anomalies': [anomaly.to_dict() for anomaly in pagination.items],
        'total': pagination.total,
        'page': page,
        'pageSize': page_size,
        'totalPages': pagination.pages
    }), 200

@anomalies_bp.route('/recent', methods=['GET'])
def get_recent_anomalies():
    """Get recent anomalies"""
    limit = request.args.get('limit', 10, type=int)
    
    anomalies = Anomaly.query.order_by(Anomaly.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'anomalies': [anomaly.to_dict() for anomaly in anomalies]
    }), 200

@anomalies_bp.route('/stats', methods=['GET'])
def get_anomaly_stats():
    """Get anomaly statistics"""
    # Get date range
    time_range = request.args.get('timeRange', '24h')
    
    if time_range == '1h':
        since = datetime.utcnow() - timedelta(hours=1)
    elif time_range == '24h':
        since = datetime.utcnow() - timedelta(days=1)
    elif time_range == '7d':
        since = datetime.utcnow() - timedelta(days=7)
    elif time_range == '30d':
        since = datetime.utcnow() - timedelta(days=30)
    else:
        since = datetime.utcnow() - timedelta(days=1)
    
    # Count by severity
    critical_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.severity == 'critical'
    ).count()
    
    high_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.severity == 'high'
    ).count()
    
    medium_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.severity == 'medium'
    ).count()
    
    low_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.severity == 'low'
    ).count()
    
    # Count by type
    anomalies = Anomaly.query.filter(Anomaly.timestamp >= since).all()
    type_distribution = {}
    for anomaly in anomalies:
        type_distribution[anomaly.type] = type_distribution.get(anomaly.type, 0) + 1
    
    # Count by status
    active_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.status == 'active'
    ).count()
    
    blocked_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.status == 'blocked'
    ).count()
    
    resolved_count = Anomaly.query.filter(
        Anomaly.timestamp >= since,
        Anomaly.status == 'resolved'
    ).count()
    
    return jsonify({
        'totalAnomalies': len(anomalies),
        'bySeverity': {
            'critical': critical_count,
            'high': high_count,
            'medium': medium_count,
            'low': low_count
        },
        'byType': type_distribution,
        'byStatus': {
            'active': active_count,
            'blocked': blocked_count,
            'resolved': resolved_count
        },
        'timeRange': time_range
    }), 200

@anomalies_bp.route('/<anomaly_id>', methods=['GET'])
def get_anomaly(anomaly_id):
    """Get specific anomaly details"""
    anomaly = Anomaly.query.get(anomaly_id)
    
    if not anomaly:
        return jsonify({'error': 'Anomaly not found'}), 404
    
    return jsonify(anomaly.to_dict()), 200

@anomalies_bp.route('/<anomaly_id>/block', methods=['POST'])
def block_anomaly(anomaly_id):
    """Block a specific anomaly"""
    anomaly = Anomaly.query.get(anomaly_id)
    
    if not anomaly:
        return jsonify({'error': 'Anomaly not found'}), 404
    
    anomaly.status = 'blocked'
    anomaly.blocked_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Anomaly blocked successfully',
        'anomaly': anomaly.to_dict()
    }), 200

@anomalies_bp.route('/', methods=['POST'])
def create_anomaly():
    """Create a new anomaly (for testing/integration)"""
    data = request.get_json()
    
    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        source_ip=data.get('sourceIp'),
        destination_ip=data.get('destinationIp'),
        source_port=data.get('sourcePort'),
        destination_port=data.get('destinationPort'),
        type=data.get('type'),
        severity=data.get('severity'),
        confidence=data.get('confidence', 0.5),
        status=data.get('status', 'active'),
        description=data.get('description'),
        protocol=data.get('protocol'),
        bytes_transferred=data.get('bytes'),
        packets=data.get('packets')
    )
    
    db.session.add(anomaly)
    db.session.commit()
    
    return jsonify({
        'message': 'Anomaly created successfully',
        'anomaly': anomaly.to_dict()
    }), 201
