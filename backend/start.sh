#!/bin/bash
###############################################################################
# Quick Start Script for Development
# Start backend with Gunicorn for testing
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting AI Anomaly Detection Backend...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found"
fi

# Start with Gunicorn
echo -e "${GREEN}✅ Starting Gunicorn server...${NC}"
echo ""
gunicorn \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --worker-class eventlet \
    --reload \
    wsgi:application
