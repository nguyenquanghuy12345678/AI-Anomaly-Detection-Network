#!/bin/bash
###############################################################################
# LIGHTWEIGHT RUN - Start with minimal resources
# Chỉ chạy Backend API, không cần Docker/PostgreSQL/Redis
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found!"
    echo "Run: ./lightweight-setup.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

echo -e "${GREEN}Starting lightweight server...${NC}"
echo ""
echo -e "${BLUE}Backend API:${NC} http://localhost:5000"
echo -e "${BLUE}Health Check:${NC} http://localhost:5000/api/health"
echo ""
echo -e "Press ${GREEN}Ctrl+C${NC} to stop"
echo ""

# Run with Flask development server (lightest option)
export FLASK_ENV=development
python app.py
