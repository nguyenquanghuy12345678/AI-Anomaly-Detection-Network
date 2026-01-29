#!/bin/bash
###############################################################################
# LIGHTWEIGHT SETUP - Minimal Resource Usage
# Phù hợp cho: VPS nhỏ, máy ảo, development
# Yêu cầu: Ubuntu 20.04+, 512MB RAM, 1GB disk
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Lightweight Setup - Minimal Resources${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Installing Python3...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Navigate to backend
cd "$(dirname "$0")/backend"

# Create virtual environment
echo -e "${BLUE}[1/6] Creating virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# Install minimal dependencies
echo -e "${BLUE}[2/6] Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create minimal .env file
echo -e "${BLUE}[3/6] Creating configuration...${NC}"
cat > .env << 'EOF'
# Minimal Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
API_PORT=5000

# Use SQLite instead of PostgreSQL (lightweight)
DATABASE_URL=sqlite:///instance/anomaly.db

# Use in-memory cache instead of Redis (lightweight)
REDIS_URL=memory://

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Disable heavy features
ENABLE_ZABBIX=false
ENABLE_ML_TRAINING=false
EOF

# Create instance directory
mkdir -p instance

# Initialize database (SQLite)
echo -e "${BLUE}[4/6] Initializing SQLite database...${NC}"
python3 << 'PYEOF'
from database import init_db
from app import app
with app.app_context():
    init_db(app)
    print("✅ Database initialized")
PYEOF

# Check if models exist
if [ ! -f "models/anomaly_detector_1.0.0.pkl" ]; then
    echo -e "${YELLOW}⚠️  ML models not found (optional for lightweight setup)${NC}"
fi

echo -e "${BLUE}[5/6] Setup complete!${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Lightweight Setup Complete!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Resource Usage:${NC}"
echo -e "  • RAM: ~300MB"
echo -e "  • Disk: ~500MB"
echo -e "  • Database: SQLite (no PostgreSQL needed)"
echo -e "  • Cache: In-memory (no Redis needed)"
echo ""
echo -e "${BLUE}To start the application:${NC}"
echo -e "  ${GREEN}./lightweight-run.sh${NC}"
echo ""
echo -e "${BLUE}Or manually:${NC}"
echo -e "  cd backend"
echo -e "  source .venv/bin/activate"
echo -e "  python app.py"
echo ""
