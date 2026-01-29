"""
Main Flask application entry point
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Disable strict slashes to avoid 308 redirects
app.url_map.strict_slashes = False

# Initialize CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize SocketIO with eventlet
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',  # Use eventlet for better WebSocket support
    logger=False,
    engineio_logger=False
)

# Import after app initialization to avoid circular imports
from api import register_blueprints
from database import init_db
from services.websocket_service import init_websocket_handlers
from services.monitoring_service import start_monitoring

# Initialize database
init_db(app)

# Register API blueprints
register_blueprints(app)

# Initialize WebSocket handlers
init_websocket_handlers(socketio)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'AI Anomaly Detection Backend',
        'version': '1.0.0'
    }, 200

@app.route('/')
def index():
    """Root endpoint"""
    return {
        'message': 'AI Anomaly Detection API',
        'version': '1.0.0',
        'endpoints': '/api/*'
    }, 200

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    
    print("⚠️  WARNING: Using Flask development server!")
    print("📌 For production, use: gunicorn --config gunicorn.conf.py wsgi:application")
    print("")
    
    # Start background monitoring service
    start_monitoring(socketio, app)
    
    # Run the application
    print(f"🚀 Starting AI Anomaly Detection Backend on port {port}...")
    print(f"📊 API available at: http://localhost:{port}/api")
    print(f"🏥 Health check: http://localhost:{port}/api/health")
    print(f"🔌 WebSocket: http://localhost:{port}/socket.io")
    print(f"⚠️  Note: Redis service not required - using in-memory cache")
    
    # Use eventlet or gevent for better WebSocket support
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=False, 
        use_reloader=False,
        log_output=True
    )
