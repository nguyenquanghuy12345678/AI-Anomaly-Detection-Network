// ========================================
// Main Application Entry Point
// ========================================

// ========================================
// WebSocket Connection
// ========================================

let wsConnected = false;
let wsReconnectAttempts = 0;
const wsMaxReconnectAttempts = 5;

function connectWebSocket() {
    try {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = API_CONFIG.baseURL.replace(/^https?:\/\//, '');
        const wsUrl = `${wsProtocol}//${wsHost}`;
        
        const socket = io(wsUrl, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: wsMaxReconnectAttempts,
            reconnectionDelay: 1000
        });

        socket.on('connect', () => {
            wsConnected = true;
            wsReconnectAttempts = 0;
            console.log('✅ WebSocket connected successfully');
            showNotification('Real-time monitoring active', 'success');
        });

        // Listen for server connection confirmation
        socket.on('connected', (data) => {
            console.log('✅ Server confirmed:', data.message);
        });

        socket.on('disconnect', () => {
            wsConnected = false;
            console.log('❌ WebSocket disconnected');
        });

        socket.on('connect_error', (error) => {
            wsReconnectAttempts++;
            console.error('❌ WebSocket connection error:', error);
            if (wsReconnectAttempts >= wsMaxReconnectAttempts) {
                showNotification('Real-time updates unavailable', 'warning');
            }
        });

        // Listen for anomaly detection events
        socket.on('anomaly_detected', (data) => {
            console.log('New anomaly detected:', data);
            showNotification(`New ${data.severity} anomaly detected from ${data.source_ip}`, 'warning');
            
            // Refresh current page data
            if (typeof dashboardManager !== 'undefined' && dashboardManager) {
                dashboardManager.loadAnomaliesTable();
                dashboardManager.updateMetrics();
            }
            if (typeof monitoringManager !== 'undefined' && monitoringManager) {
                monitoringManager.loadConnections();
            }
            if (typeof alertsManager !== 'undefined' && alertsManager) {
                alertsManager.loadAlerts();
            }
        });

        // Listen for traffic update events
        socket.on('traffic_update', (data) => {
            console.log('Traffic update:', data);
            
            // Update traffic displays
            if (typeof monitoringManager !== 'undefined' && monitoringManager) {
                monitoringManager.loadTrafficStats();
            }
            if (typeof dashboardManager !== 'undefined' && dashboardManager) {
                dashboardManager.updateMetrics();
            }
        });

        // Listen for alert events
        socket.on('alert_created', (data) => {
            console.log('New alert created:', data);
            showNotification(`New alert: ${data.message}`, data.severity === 'critical' ? 'error' : 'warning');
            
            // Refresh alerts page if active
            if (typeof alertsManager !== 'undefined' && alertsManager) {
                alertsManager.loadAlerts();
            }
        });

        // Listen for model update events
        socket.on('model_updated', (data) => {
            console.log('Model updated:', data);
            showNotification('AI model has been updated', 'info');
        });

        return socket;
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        showNotification('Real-time updates unavailable', 'warning');
        return null;
    }
}

// ========================================
// Utility Functions
// ========================================

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        if (typeof value === 'number') {
            animateValue(element, parseInt(element.textContent) || 0, value, 1000);
        } else {
            element.textContent = value;
        }
    }
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

function formatTime(timestamp, format = 'full') {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN', TIME_FORMATS[format]);
}

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function showModal() {
    const modal = document.getElementById('alertModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal() {
    const modal = document.getElementById('alertModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function blockThreat() {
    showNotification('Threat blocked successfully', 'success');
    closeModal();
    dashboardManager.loadAnomaliesTable();
}

// ========================================
// Notification System
// ========================================

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add styles if not already added
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 100px;
                right: 20px;
                min-width: 300px;
                max-width: 500px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                animation: slideIn 0.3s ease-out;
                margin-bottom: 1rem;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                flex: 1;
            }
            
            .notification-content i {
                font-size: 1.25rem;
            }
            
            .notification-close {
                background: none;
                border: none;
                cursor: pointer;
                padding: 0.25rem;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            
            .notification-close:hover {
                opacity: 1;
            }
            
            .notification-info {
                background: rgba(79, 172, 254, 0.1);
                border-left: 4px solid rgba(79, 172, 254, 1);
                color: rgba(79, 172, 254, 1);
            }
            
            .notification-success {
                background: rgba(67, 233, 123, 0.1);
                border-left: 4px solid rgba(67, 233, 123, 1);
                color: rgba(67, 233, 123, 1);
            }
            
            .notification-warning {
                background: rgba(254, 202, 87, 0.1);
                border-left: 4px solid rgba(254, 202, 87, 1);
                color: rgba(254, 202, 87, 1);
            }
            
            .notification-error {
                background: rgba(245, 87, 108, 0.1);
                border-left: 4px solid rgba(245, 87, 108, 1);
                color: rgba(245, 87, 108, 1);
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styles);
    }

    // Add to page
    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        info: 'info-circle',
        success: 'check-circle',
        warning: 'exclamation-triangle',
        error: 'times-circle'
    };
    return icons[type] || 'info-circle';
}

// ========================================
// Data Loading Functions
// ========================================

async function loadTrafficData() {
    try {
        // In production, replace with actual API call
        // const data = await apiService.getNetworkTraffic();
        
        // Using mock data for now
        const data = MockDataGenerator.generateTrafficData(20).map(point => ({
            ...point,
            incoming: Math.floor(Math.random() * 100 + 50),
            outgoing: Math.floor(Math.random() * 80 + 30)
        }));

        const chart = chartManager.getChart('traffic');
        if (chart) {
            chart.data.labels = data.map(d => formatTime(d.timestamp, 'short'));
            chart.data.datasets[0].data = data.map(d => d.incoming);
            chart.data.datasets[1].data = data.map(d => d.outgoing);
            chart.update();
        }
    } catch (error) {
        console.error('Error loading traffic data:', error);
    }
}

async function loadAnomalyData() {
    try {
        // In production, replace with actual API call
        // const data = await apiService.getAnomalyStats();
        
        // Using mock data for now
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const data = {
            labels,
            critical: labels.map(() => Math.floor(Math.random() * 10)),
            high: labels.map(() => Math.floor(Math.random() * 15 + 5)),
            medium: labels.map(() => Math.floor(Math.random() * 20 + 10)),
            low: labels.map(() => Math.floor(Math.random() * 25 + 15))
        };

        chartManager.updateAnomalyChart(data);
    } catch (error) {
        console.error('Error loading anomaly data:', error);
    }
}

async function loadThreatDistribution() {
    try {
        // In production, replace with actual API call
        
        // Using mock data for now
        const data = Object.keys(ANOMALY_TYPES).map(() => 
            Math.floor(Math.random() * 50 + 10)
        );

        chartManager.updateThreatDistributionChart(data);
    } catch (error) {
        console.error('Error loading threat distribution:', error);
    }
}

async function loadConfidenceData() {
    try {
        // In production, replace with actual API call
        
        // Generate initial confidence data
        for (let i = 0; i < 15; i++) {
            const data = {
                label: `Event ${i + 1}`,
                value: Math.floor(Math.random() * 20 + 75)
            };
            chartManager.updateConfidenceChart(data);
        }

        // Continue updating in real-time
        setInterval(() => {
            const data = {
                value: Math.floor(Math.random() * 20 + 75)
            };
            chartManager.updateConfidenceChart(data);
        }, 5000);
    } catch (error) {
        console.error('Error loading confidence data:', error);
    }
}

// ========================================
// CSV Export Function
// ========================================

function convertToCSV(data) {
    if (data.length === 0) return '';

    const headers = ['Timestamp', 'Source IP', 'Destination IP', 'Type', 'Severity', 'Confidence', 'Status'];
    const rows = data.map(item => [
        formatTime(item.timestamp, 'full'),
        item.sourceIp,
        item.destinationIp,
        item.type,
        item.severity,
        item.confidence + '%',
        item.status
    ]);

    const csv = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    return csv;
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ========================================
// Keyboard Shortcuts
// ========================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.focus();
    }

    // Escape: Close modal
    if (e.key === 'Escape') {
        closeModal();
    }

    // Ctrl/Cmd + R: Refresh data
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        showNotification('Refreshing dashboard...', 'info');
        dashboardManager.loadInitialData();
    }
});

// ========================================
// Window Events
// ========================================

window.addEventListener('load', () => {
    console.log('AI Network Anomaly Detection System - Initializing...');
    dashboardManager.initialize();
    showNotification('Dashboard loaded successfully', 'success');
});

window.addEventListener('beforeunload', () => {
    // Clean up
    chartManager.stopAllAutoUpdates();
    wsService.disconnect();
});

// Handle visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause updates when tab is not visible
        chartManager.stopAllAutoUpdates();
    } else {
        // Resume updates when tab becomes visible
        dashboardManager.startChartUpdates();
        dashboardManager.loadInitialData();
    }
});

// ========================================
// Error Handling
// ========================================

window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('An error occurred. Please try again.', 'error');
});

// ========================================
// Export Functions
// ========================================

if (typeof window !== 'undefined') {
    window.showNotification = showNotification;
    window.showLoading = showLoading;
    window.hideLoading = hideLoading;
    window.showModal = showModal;
    window.closeModal = closeModal;
    window.blockThreat = blockThreat;
    window.formatTime = formatTime;
    window.updateElement = updateElement;
    window.loadTrafficData = loadTrafficData;
    window.loadAnomalyData = loadAnomalyData;
    window.loadThreatDistribution = loadThreatDistribution;
    window.loadConfidenceData = loadConfidenceData;
    window.convertToCSV = convertToCSV;
    window.downloadFile = downloadFile;
}

// ========================================
// Theme Toggle Functionality
// ========================================

function initThemeToggle() {
    const themeToggleBtn = document.getElementById('themeToggle');
    if (!themeToggleBtn) return;

    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // Add click handler
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        
        showNotification(`Switched to ${newTheme} theme`, 'info');
    });
}

function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }

    // Update icon
    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
        const icon = themeToggleBtn.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    // Update map theme if map is loaded
    if (window.geoMapManager && window.geoMapManager.map) {
        window.geoMapManager.setDarkMode(theme === 'dark');
    }
}

// Initialize theme toggle when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initKeyboardShortcuts();
    initNotifications();
    initScrollEffects();
});

// ========================================
// Scroll Effects
// ========================================

function initScrollEffects() {
    let lastScroll = 0;
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Add shadow to header on scroll
        if (currentScroll > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
}

// ========================================
// Keyboard Shortcuts
// ========================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Only trigger if no input is focused
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            return;
        }

        // Ctrl/Cmd + key shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'd':
                    e.preventDefault();
                    window.location.hash = 'dashboard';
                    showNotification('Navigated to Dashboard', 'info');
                    break;
                case 'm':
                    e.preventDefault();
                    window.location.hash = 'monitoring';
                    showNotification('Navigated to Monitoring', 'info');
                    break;
                case 'k':
                    e.preventDefault();
                    window.location.hash = 'map';
                    showNotification('Navigated to Map', 'info');
                    break;
                case ',':
                    e.preventDefault();
                    window.location.hash = 'settings';
                    showNotification('Navigated to Settings', 'info');
                    break;
            }
        }

        // Alt + key shortcuts
        if (e.altKey) {
            switch(e.key) {
                case 't':
                    e.preventDefault();
                    const themeBtn = document.getElementById('themeToggle');
                    if (themeBtn) themeBtn.click();
                    break;
                case 'n':
                    e.preventDefault();
                    const notifBtn = document.getElementById('notificationsBtn');
                    if (notifBtn) notifBtn.click();
                    break;
            }
        }

        // Escape key to close modals
        if (e.key === 'Escape') {
            closeModal();
            const notifications = document.querySelectorAll('.notification');
            notifications.forEach(n => n.remove());
        }

        // ? to show keyboard shortcuts help
        if (e.key === '?' && !e.shiftKey) {
            showKeyboardShortcutsHelp();
        }
    });
}

function showKeyboardShortcutsHelp() {
    const helpContent = `
        <div style="text-align: left;">
            <h3 style="margin-bottom: 15px;">⌨️ Keyboard Shortcuts</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Ctrl + D</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Go to Dashboard</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Ctrl + M</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Go to Monitoring</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Ctrl + K</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Go to Map</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Ctrl + ,</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Go to Settings</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Alt + T</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Toggle Theme</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Alt + N</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Open Notifications</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Esc</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">Close Modals</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>?</strong></td>
                    <td style="padding: 8px;">Show this help</td>
                </tr>
            </table>
        </div>
    `;
    
    const modalBody = document.getElementById('modalBody');
    const modal = document.getElementById('anomalyModal');
    
    if (modalBody && modal) {
        modalBody.innerHTML = helpContent;
        modal.querySelector('.modal-header h3').textContent = 'Keyboard Shortcuts';
        modal.querySelector('.modal-footer').style.display = 'none';
        modal.classList.add('active');
    }
}

// ========================================
// Notifications System
// ========================================

function initNotifications() {
    const notifBtn = document.getElementById('notificationsBtn');
    if (notifBtn) {
        notifBtn.addEventListener('click', showNotificationsPanel);
    }
}

function showNotificationsPanel() {
    showNotification('Notifications panel - Coming soon!', 'info');
}

// ========================================
// Console Welcome Message
// ========================================

console.log('%c🛡️ AI Network Anomaly Detection System', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cVersion 1.0.0', 'color: #764ba2; font-size: 14px;');
console.log('%cInitializing security monitoring...', 'color: #43e97b; font-size: 12px;');
console.log('%c💡 Press ? to see keyboard shortcuts', 'color: #feca57; font-size: 12px;');
// ========================================
// Application Initialization
// ========================================

// Initialize WebSocket connection on app load
let appWebSocket = null;

document.addEventListener('DOMContentLoaded', () => {
    // Connect WebSocket for real-time updates
    appWebSocket = connectWebSocket();
    console.log('%c🔌 WebSocket connection initiated', 'color: #38ada9; font-size: 12px;');
});