#!/bin/bash
###############################################################################
# Production Deployment Script
# AI Anomaly Detection System - Backend Deployment
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-anomaly-detection"
INSTALL_DIR="/opt/ai-anomaly-detection"
BACKEND_DIR="${INSTALL_DIR}/backend"
FRONTEND_DIR="${INSTALL_DIR}/frontend"
VENV_DIR="${BACKEND_DIR}/.venv"
SERVICE_NAME="ai-anomaly-detection.service"
NGINX_CONFIG="/etc/nginx/sites-available/${PROJECT_NAME}"
NGINX_ENABLED="/etc/nginx/sites-enabled/${PROJECT_NAME}"

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Please run as root or with sudo"
        exit 1
    fi
}

check_dependencies() {
    print_info "Checking system dependencies..."
    
    local missing_deps=()
    
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v pip3 >/dev/null 2>&1 || missing_deps+=("python3-pip")
    command -v nginx >/dev/null 2>&1 || missing_deps+=("nginx")
    command -v systemctl >/dev/null 2>&1 || missing_deps+=("systemd")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Install them with: apt-get install ${missing_deps[*]}"
        exit 1
    fi
    
    print_success "All dependencies found"
}

create_directories() {
    print_info "Creating project directories..."
    
    mkdir -p "${INSTALL_DIR}"
    mkdir -p "${BACKEND_DIR}"
    mkdir -p "${FRONTEND_DIR}"
    mkdir -p "${BACKEND_DIR}/logs"
    mkdir -p "${BACKEND_DIR}/models"
    mkdir -p "${BACKEND_DIR}/data"
    mkdir -p "/var/cache/nginx/anomaly_detection"
    
    print_success "Directories created"
}

setup_python_env() {
    print_info "Setting up Python virtual environment..."
    
    cd "${BACKEND_DIR}"
    python3 -m venv "${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
    
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    print_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping Python dependencies"
    fi
}

setup_systemd_service() {
    print_info "Setting up systemd service..."
    
    if [ -f "${BACKEND_DIR}/${SERVICE_NAME}" ]; then
        cp "${BACKEND_DIR}/${SERVICE_NAME}" "/etc/systemd/system/${SERVICE_NAME}"
        systemctl daemon-reload
        print_success "Systemd service configured"
    else
        print_warning "Service file not found: ${BACKEND_DIR}/${SERVICE_NAME}"
    fi
}

setup_nginx() {
    print_info "Setting up Nginx configuration..."
    
    if [ -f "${INSTALL_DIR}/nginx/nginx.conf" ]; then
        cp "${INSTALL_DIR}/nginx/nginx.conf" "${NGINX_CONFIG}"
        
        # Enable site
        if [ ! -L "${NGINX_ENABLED}" ]; then
            ln -s "${NGINX_CONFIG}" "${NGINX_ENABLED}"
        fi
        
        # Test configuration
        nginx -t
        
        print_success "Nginx configured"
    else
        print_warning "Nginx config not found: ${INSTALL_DIR}/nginx/nginx.conf"
    fi
}

set_permissions() {
    print_info "Setting permissions..."
    
    # Create www-data user if it doesn't exist
    id -u www-data &>/dev/null || useradd -r -s /bin/false www-data
    
    chown -R www-data:www-data "${INSTALL_DIR}"
    chmod -R 755 "${INSTALL_DIR}"
    chmod -R 775 "${BACKEND_DIR}/logs"
    
    # Cache directory permissions
    chown -R www-data:www-data /var/cache/nginx/anomaly_detection
    chmod -R 755 /var/cache/nginx/anomaly_detection
    
    print_success "Permissions set"
}

start_services() {
    print_info "Starting services..."
    
    # Enable and start backend service
    systemctl enable ${SERVICE_NAME}
    systemctl restart ${SERVICE_NAME}
    
    # Restart Nginx
    systemctl restart nginx
    
    print_success "Services started"
}

check_services() {
    print_info "Checking service status..."
    
    # Check backend
    if systemctl is-active --quiet ${SERVICE_NAME}; then
        print_success "Backend service is running"
    else
        print_error "Backend service failed to start"
        systemctl status ${SERVICE_NAME}
        exit 1
    fi
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        print_error "Nginx failed to start"
        systemctl status nginx
        exit 1
    fi
    
    # Test API endpoint
    sleep 2
    if curl -f http://localhost/api/health >/dev/null 2>&1; then
        print_success "API health check passed"
    else
        print_warning "API health check failed - service may still be starting"
    fi
}

display_info() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Deployment Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}📊 Application URLs:${NC}"
    echo -e "   Frontend:  http://localhost"
    echo -e "   API:       http://localhost/api"
    echo -e "   Health:    http://localhost/api/health"
    echo ""
    echo -e "${BLUE}🔧 Service Management:${NC}"
    echo -e "   Start:     sudo systemctl start ${SERVICE_NAME}"
    echo -e "   Stop:      sudo systemctl stop ${SERVICE_NAME}"
    echo -e "   Restart:   sudo systemctl restart ${SERVICE_NAME}"
    echo -e "   Status:    sudo systemctl status ${SERVICE_NAME}"
    echo -e "   Logs:      sudo journalctl -u ${SERVICE_NAME} -f"
    echo ""
    echo -e "${BLUE}📝 Log Files:${NC}"
    echo -e "   Backend:   ${BACKEND_DIR}/logs/"
    echo -e "   Nginx:     /var/log/nginx/anomaly_detection_*.log"
    echo ""
    echo -e "${YELLOW}⚠️  Remember to:${NC}"
    echo -e "   1. Configure your domain in nginx.conf"
    echo -e "   2. Set up SSL certificates (Let's Encrypt)"
    echo -e "   3. Update .env file with production settings"
    echo -e "   4. Set up database backups"
    echo -e "   5. Configure firewall rules"
    echo ""
}

# Main deployment flow
main() {
    print_info "Starting deployment of ${PROJECT_NAME}..."
    echo ""
    
    check_root
    check_dependencies
    create_directories
    setup_python_env
    setup_systemd_service
    setup_nginx
    set_permissions
    start_services
    check_services
    display_info
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"
