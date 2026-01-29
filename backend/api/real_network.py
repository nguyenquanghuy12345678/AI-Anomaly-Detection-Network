"""
Real Network Data API endpoints
"""
from flask import Blueprint, jsonify, request
from services.real_network_service import real_network_service
import psutil

real_network_bp = Blueprint('real_network', __name__)

@real_network_bp.route('/interfaces', methods=['GET'])
def get_interfaces():
    """Lấy danh sách network interfaces"""
    interfaces = real_network_service.get_network_interfaces()
    return jsonify({
        'interfaces': interfaces,
        'count': len(interfaces)
    }), 200

@real_network_bp.route('/connections', methods=['GET'])
def get_real_connections():
    """Lấy connections THẬT từ hệ thống"""
    connections = real_network_service.get_real_connections()
    return jsonify({
        'connections': connections,
        'total': len(connections),
        'timestamp': psutil.boot_time()
    }), 200

@real_network_bp.route('/stats', methods=['GET'])
def get_network_stats():
    """Lấy thống kê mạng THẬT"""
    stats = real_network_service.get_real_network_stats()
    return jsonify(stats), 200

@real_network_bp.route('/capture/start', methods=['POST'])
def start_capture():
    """Bắt đầu capture packets (requires admin)"""
    data = request.get_json() or {}
    interface = data.get('interface', None)
    filter_str = data.get('filter', '')
    
    success = real_network_service.start_capture(interface, filter_str)
    
    if success:
        return jsonify({
            'message': 'Packet capture started',
            'interface': interface or 'default',
            'filter': filter_str,
            'note': 'Requires administrator/root privileges'
        }), 200
    else:
        return jsonify({
            'error': 'Failed to start capture',
            'note': 'Make sure you run with administrator/root privileges'
        }), 500

@real_network_bp.route('/capture/stop', methods=['POST'])
def stop_capture():
    """Dừng packet capture"""
    real_network_service.stop_capture()
    return jsonify({
        'message': 'Packet capture stopped'
    }), 200

@real_network_bp.route('/capture/stats', methods=['GET'])
def get_capture_stats():
    """Lấy thống kê từ packet capture"""
    stats = real_network_service.get_capture_stats()
    return jsonify(stats), 200

@real_network_bp.route('/capture/reset', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    real_network_service.reset_stats()
    return jsonify({
        'message': 'Statistics reset successfully'
    }), 200

@real_network_bp.route('/system/info', methods=['GET'])
def get_system_info():
    """Lấy thông tin hệ thống"""
    try:
        return jsonify({
            'hostname': psutil.os.uname().nodename if hasattr(psutil.os, 'uname') else 'Unknown',
            'platform': psutil.os.name,
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'boot_time': psutil.boot_time()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
