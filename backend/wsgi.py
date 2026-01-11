"""
WSGI Entry Point
Production entry point for WSGI servers (Gunicorn/Waitress)
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, socketio

# Wrap Flask app with SocketIO middleware for WSGI servers
# This makes the app compatible with Gunicorn, Waitress, etc.
try:
    # For python-socketio >= 5.0
    application = socketio.WSGIApp(socketio, app)
except AttributeError:
    # Fallback: Use Flask app directly if WSGIApp not available
    # SocketIO will still work through Flask's built-in server
    application = app
    print("⚠️  Warning: Using Flask app directly. WebSocket may require socketio.run()")

if __name__ == "__main__":
    # For development only - use production server in production
    port = int(os.getenv('API_PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
