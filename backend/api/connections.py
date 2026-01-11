"""
Connections API endpoints
"""
from flask import Blueprint, request, jsonify
from models.connection import Connection
from database import db

connections_bp = Blueprint('connections', __name__)

@connections_bp.route('/', methods=['GET'])
def get_connections():
    """Get active connections"""
    limit = request.args.get('limit', 100, type=int)
    active_only = request.args.get('activeOnly', 'true').lower() == 'true'
    
    query = Connection.query
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    connections = query.order_by(Connection.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'connections': [conn.to_dict() for conn in connections],
        'total': len(connections)
    }), 200

@connections_bp.route('/stats', methods=['GET'])
def get_connection_stats():
    """Get connection statistics"""
    active_count = Connection.query.filter_by(is_active=True).count()
    
    # Group by protocol
    connections = Connection.query.filter_by(is_active=True).all()
    protocol_distribution = {}
    for conn in connections:
        protocol_distribution[conn.protocol] = protocol_distribution.get(conn.protocol, 0) + 1
    
    # Group by state
    state_distribution = {}
    for conn in connections:
        state_distribution[conn.state] = state_distribution.get(conn.state, 0) + 1
    
    return jsonify({
        'activeConnections': active_count,
        'byProtocol': protocol_distribution,
        'byState': state_distribution
    }), 200
