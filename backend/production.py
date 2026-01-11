"""
Production Server Launcher
Cross-platform script to start backend with appropriate WSGI server
"""
import os
import sys
import platform

def main():
    """Start production server"""
    print("🚀 Starting AI Anomaly Detection Backend (Production Mode)")
    print(f"📊 Platform: {platform.system()}")
    print("")
    
    # Import app and socketio
    from app import app, socketio
    from services.monitoring_service import start_monitoring
    
    # Start monitoring service
    start_monitoring(socketio, app)
    
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    if platform.system() == 'Windows':
        # Use Waitress on Windows with Socket.IO compatibility
        print("🪟 Using Waitress server (Windows)")
        print(f"📌 Listening on http://{host}:{port}")
        print("⚠️  Note: For full WebSocket support, Socket.IO will use long-polling")
        print("")
        
        from waitress import serve
        
        # Waitress doesn't support WebSocket upgrade, so we use Socket.IO's built-in server
        # which handles both WebSocket and polling transports
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            log_output=True
        )
    else:
        # Use Gunicorn on Unix/Linux (requires separate command)
        print("🐧 Unix/Linux detected")
        print(f"📌 Recommended: gunicorn --config gunicorn.conf.py wsgi:application")
        print("📌 Fallback: Using Socket.IO built-in server")
        print("")
        
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            use_reloader=False
        )

if __name__ == '__main__':
    main()
