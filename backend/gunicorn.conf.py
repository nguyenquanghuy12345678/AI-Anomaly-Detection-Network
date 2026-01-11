"""
Gunicorn Configuration File
Production-ready WSGI server settings for AI Anomaly Detection Backend
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('API_PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'eventlet'  # Required for Socket.IO support
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')  # - means stdout
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')    # - means stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'ai-anomaly-detection'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
# ssl_version = 'TLSv1_2'
# cert_reqs = 0
# ca_certs = None
# ciphers = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Starting Gunicorn server...")

def on_reload(server):
    """Called when the server is reloaded."""
    print("🔄 Reloading Gunicorn server...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Gunicorn server is ready! Workers: {workers}")
    print(f"📊 Listening on {bind}")
    print(f"🔧 Worker class: {worker_class}")

def on_exit(server):
    """Called just before the master process exits."""
    print("👋 Shutting down Gunicorn server...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"⚠️  Worker {worker.pid} received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker is aborted."""
    print(f"❌ Worker {worker.pid} aborted")
