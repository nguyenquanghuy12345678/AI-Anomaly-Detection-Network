"""
Alerts API endpoints
"""
from flask import Blueprint, request, jsonify
from models.alert import Alert
from database import db
from datetime import datetime, timedelta
import uuid

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/', methods=['GET'])
def get_alerts():
    """Get all alerts with optional filters"""
    severity = request.args.get('severity', None)
    status = request.args.get('status', None)
    limit = request.args.get('limit', 50, type=int)
    
    query = Alert.query
    
    if severity:
        query = query.filter_by(severity=severity)
    if status:
        query = query.filter_by(status=status)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'total': len(alerts)
    }), 200

@alerts_bp.route('/unread', methods=['GET'])
def get_unread_alerts():
    """Get unread alerts only"""
    alerts = Alert.query.filter_by(status='unread').order_by(Alert.timestamp.desc()).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'total': len(alerts)
    }), 200

@alerts_bp.route('/<alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    """Mark alert as read"""
    alert = Alert.query.get(alert_id)
    
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.status = 'read'
    alert.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Alert marked as read',
        'alert': alert.to_dict()
    }), 200

@alerts_bp.route('/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    alert = Alert.query.get(alert_id)
    
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    db.session.delete(alert)
    db.session.commit()
    
    return jsonify({
        'message': 'Alert deleted successfully'
    }), 200

@alerts_bp.route('/', methods=['POST'])
def create_alert():
    """Create a new alert"""
    data = request.get_json()
    
    alert = Alert(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        severity=data.get('severity'),
        status=data.get('status', 'unread'),
        type=data.get('type'),
        title=data.get('title'),
        description=data.get('description'),
        source_ip=data.get('sourceIp'),
        affected_systems=data.get('affectedSystems', 1),
        requires_action=data.get('requiresAction', False),
        anomaly_id=data.get('anomalyId')
    )
    
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({
        'message': 'Alert created successfully',
        'alert': alert.to_dict()
    }), 201

@alerts_bp.route('/stats', methods=['GET'])
def get_alert_stats():
    """Get alert statistics"""
    time_range = request.args.get('timeRange', '24h')
    
    if time_range == '1h':
        since = datetime.utcnow() - timedelta(hours=1)
    elif time_range == '24h':
        since = datetime.utcnow() - timedelta(days=1)
    elif time_range == '7d':
        since = datetime.utcnow() - timedelta(days=7)
    else:
        since = datetime.utcnow() - timedelta(days=1)
    
    total = Alert.query.filter(Alert.timestamp >= since).count()
    unread = Alert.query.filter(
        Alert.timestamp >= since,
        Alert.status == 'unread'
    ).count()
    
    critical = Alert.query.filter(
        Alert.timestamp >= since,
        Alert.severity == 'critical'
    ).count()
    
    return jsonify({
        'total': total,
        'unread': unread,
        'critical': critical,
        'timeRange': time_range
    }), 200
