// ========================================
// API Configuration
// ========================================

const API_CONFIG = {
    baseURL: 'http://localhost:5000/api',
    endpoints: {
        // Anomaly endpoints
        anomalies: '/anomalies',
        recentAnomalies: '/anomalies/recent',
        anomalyStats: '/anomalies/stats',
        
        // Network monitoring endpoints (Updated to match backend)
        networkTraffic: '/traffic',
        networkStats: '/traffic/stats',
        
        // AI Model endpoints
        modelStatus: '/model/status',
        modelMetrics: '/model/metrics',
        modelPredict: '/model/predict',
        
        // System endpoints
        systemStatus: '/system/status',
        systemHealth: '/system/health',
        
        // Alert endpoints
        alerts: '/alerts',
        alertsUnread: '/alerts/unread',
    },
    
    // WebSocket configuration (Socket.IO)
    websocket: {
        url: 'http://localhost:5000',
        reconnectInterval: 3000,
        maxReconnectAttempts: 5
    },
    
    // Polling intervals (in milliseconds)
    polling: {
        anomalies: 5000,      // 5 seconds
        traffic: 2000,        // 2 seconds
        stats: 10000,         // 10 seconds
        systemStatus: 30000,  // 30 seconds
        alerts: 10000         // 10 seconds
    },
    
    // Pagination
    pagination: {
        defaultPageSize: 10,
        maxPageSize: 100
    },
    
    // Chart update intervals
    charts: {
        realtime: 1000,       // 1 second
        historical: 5000      // 5 seconds
    }
};

// Chart color schemes
const CHART_COLORS = {
    primary: 'rgba(102, 126, 234, 1)',
    primaryLight: 'rgba(102, 126, 234, 0.5)',
    secondary: 'rgba(118, 75, 162, 1)',
    secondaryLight: 'rgba(118, 75, 162, 0.5)',
    success: 'rgba(67, 233, 123, 1)',
    successLight: 'rgba(67, 233, 123, 0.5)',
    danger: 'rgba(245, 87, 108, 1)',
    dangerLight: 'rgba(245, 87, 108, 0.5)',
    warning: 'rgba(254, 202, 87, 1)',
    warningLight: 'rgba(254, 202, 87, 0.5)',
    info: 'rgba(79, 172, 254, 1)',
    infoLight: 'rgba(79, 172, 254, 0.5)',
    
    // Gradient colors
    gradient: {
        purple: ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'],
        pink: ['rgba(240, 147, 251, 0.8)', 'rgba(245, 87, 108, 0.8)'],
        blue: ['rgba(79, 172, 254, 0.8)', 'rgba(0, 242, 254, 0.8)'],
        green: ['rgba(67, 233, 123, 0.8)', 'rgba(56, 249, 215, 0.8)']
    }
};

// Anomaly severity levels
const SEVERITY_LEVELS = {
    CRITICAL: { value: 4, label: 'Critical', color: CHART_COLORS.danger },
    HIGH: { value: 3, label: 'High', color: CHART_COLORS.warning },
    MEDIUM: { value: 2, label: 'Medium', color: CHART_COLORS.info },
    LOW: { value: 1, label: 'Low', color: CHART_COLORS.success }
};

// Anomaly types
const ANOMALY_TYPES = {
    DOS_ATTACK: 'DoS Attack',
    PORT_SCAN: 'Port Scan',
    BRUTE_FORCE: 'Brute Force',
    SQL_INJECTION: 'SQL Injection',
    XSS_ATTACK: 'XSS Attack',
    MALWARE: 'Malware',
    SUSPICIOUS_TRAFFIC: 'Suspicious Traffic',
    UNAUTHORIZED_ACCESS: 'Unauthorized Access',
    DATA_EXFILTRATION: 'Data Exfiltration',
    OTHER: 'Other'
};

// Chart default options
const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                usePointStyle: true,
                padding: 15,
                font: {
                    size: 12
                }
            }
        },
        tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.parsed.y.toLocaleString();
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.05)',
                drawBorder: false
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        },
        x: {
            grid: {
                display: false,
                drawBorder: false
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        }
    }
};

// Time format options
const TIME_FORMATS = {
    full: { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    },
    date: { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    },
    time: { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    },
    short: { 
        hour: '2-digit', 
        minute: '2-digit'
    }
};

// Export configuration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API_CONFIG,
        CHART_COLORS,
        SEVERITY_LEVELS,
        ANOMALY_TYPES,
        CHART_DEFAULTS,
        TIME_FORMATS
    };
}
