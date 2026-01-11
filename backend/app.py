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

# Initialize CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

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
    
    # Start background monitoring service
    start_monitoring(socketio)
    
    # Run the application
    print(f"🚀 Starting AI Anomaly Detection Backend on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True, use_reloader=False)
