"""
WebSocket service for real-time updates
"""
from flask_socketio import emit
import threading
import time

# Global socketio instance
socketio_instance = None

def init_websocket_handlers(socketio):
    """Initialize WebSocket event handlers"""
    global socketio_instance
    socketio_instance = socketio
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"🔌 Client connected")
        emit('connected', {'message': 'Connected to anomaly detection system'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"🔌 Client disconnected")
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping from client"""
        emit('pong', {'timestamp': time.time()})
    
    print("✅ WebSocket handlers initialized")

def emit_anomaly(anomaly_data):
    """Emit new anomaly to all connected clients"""
    if socketio_instance:
        socketio_instance.emit('anomaly', anomaly_data)

def emit_traffic_update(traffic_data):
    """Emit traffic update to all connected clients"""
    if socketio_instance:
        socketio_instance.emit('traffic', traffic_data)

def emit_alert(alert_data):
    """Emit new alert to all connected clients"""
    if socketio_instance:
        socketio_instance.emit('alert', alert_data)

def emit_status_update(status_data):
    """Emit system status update to all connected clients"""
    if socketio_instance:
        socketio_instance.emit('status', status_data)
