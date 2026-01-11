#!/bin/bash
###############################################################################
# Production Start Script for Unix/Linux
# Uses Gunicorn WSGI server
###############################################################################

set -e

echo "========================================"
echo "AI Anomaly Detection - Production Mode"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python3 -m venv .venv"
    echo "Then install dependencies: .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn..."
    pip install gunicorn eventlet
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start production server
echo ""
echo "Starting production server with Gunicorn..."
echo ""

gunicorn \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:${API_PORT:-5000} \
    --workers ${GUNICORN_WORKERS:-4} \
    --worker-class eventlet \
    --access-logfile ${GUNICORN_ACCESS_LOG:--} \
    --error-logfile ${GUNICORN_ERROR_LOG:--} \
    --log-level ${LOG_LEVEL:-info} \
    wsgi:application
