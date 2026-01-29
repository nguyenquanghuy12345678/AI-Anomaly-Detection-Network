// ========================================
// API Service Module
// ========================================

class APIService {
    constructor() {
        this.baseURL = API_CONFIG.baseURL;
        this.endpoints = API_CONFIG.endpoints;
        this.requestQueue = [];
        this.isOnline = true;
        this.retryAttempts = 3;
        
        // Monitor connection status
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
    }

    // ========================================
    // Core HTTP Methods
    // ========================================

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            showLoading();
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            hideLoading();
            return data;
        } catch (error) {
            hideLoading();
            console.error('API Request Error:', error);
            this.handleError(error);
            throw error;
        }
    }

    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url);
    }

    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // ========================================
    // Anomaly API Methods
    // ========================================

    async getAnomalies(page = 1, pageSize = API_CONFIG.pagination.defaultPageSize) {
        return this.get(this.endpoints.anomalies, { page, pageSize });
    }

    async getRecentAnomalies(limit = 10) {
        return this.get(this.endpoints.recentAnomalies, { limit });
    }

    async getAnomalyStats() {
        return this.get(this.endpoints.anomalyStats);
    }

    async getAnomalyById(id) {
        return this.get(`${this.endpoints.anomalies}/${id}`);
    }

    async blockAnomaly(id) {
        return this.post(`${this.endpoints.anomalies}/${id}/block`);
    }

    // ========================================
    // Network Monitoring API Methods
    // ========================================

    async getNetworkTraffic(timeRange = '1h') {
        return this.get(this.endpoints.networkTraffic, { timeRange });
    }

    async getNetworkStats() {
        return this.get(this.endpoints.networkStats);
    }
    
    async getRecentTraffic(limit = 10) {
        return this.get(this.endpoints.trafficRecent, { limit });
    }
    
    // Connection API methods
    async getConnections() {
        return this.get(this.endpoints.connections);
    }
    
    async getConnectionStats() {
        return this.get(this.endpoints.connectionsStats);
    }
    
    // Real Network API methods
    async getRealInterfaces() {
        return this.get(this.endpoints.realInterfaces);
    }
    
    async getRealConnections() {
        return this.get(this.endpoints.realConnections);
    }
    
    async getRealStats() {
        return this.get(this.endpoints.realStats);
    }
    
    async startRealCapture(data = {}) {
        return this.post(this.endpoints.realCaptureStart, data);
    }
    
    async stopRealCapture() {
        return this.post(this.endpoints.realCaptureStop);
    }
    
    async getRealCaptureStats() {
        return this.get(this.endpoints.realCaptureStats);
    }

    // ========================================
    // AI Model API Methods
    // ========================================

    async getModelStatus() {
        return this.get(this.endpoints.modelStatus);
    }

    async getModelMetrics() {
        return this.get(this.endpoints.modelMetrics);
    }

    async predictAnomaly(data) {
        return this.post(this.endpoints.modelPredict, data);
    }
    
    async retrainModel() {
        return this.post(this.endpoints.modelRetrain);
    }

    // ========================================
    // System API Methods
    // ========================================

    async getSystemStatus() {
        return this.get(this.endpoints.systemStatus);
    }

    async getSystemHealth() {
        return this.get(this.endpoints.systemHealth);
    }
    
    async getSystemMetrics() {
        return this.get(this.endpoints.systemMetrics);
    }

    // ========================================
    // Alert API Methods
    // ========================================

    async getAlerts(unreadOnly = false) {
        const endpoint = unreadOnly ? this.endpoints.alertsUnread : this.endpoints.alerts;
        return this.get(endpoint);
    }
    
    async getAlertStats() {
        return this.get(this.endpoints.alertsStats);
    }

    async markAlertAsRead(id) {
        return this.put(`${this.endpoints.alerts}/${id}/read`);
    }

    async deleteAlert(id) {
        return this.delete(`${this.endpoints.alerts}/${id}`);
    }
    
    async createAlert(data) {
        return this.post(this.endpoints.alerts, data);
    }

    // ========================================
    // Error Handling
    // ========================================

    handleError(error) {
        if (error.message.includes('Failed to fetch')) {
            showNotification('Connection error. Please check your network.', 'error');
        } else if (error.message.includes('401')) {
            showNotification('Authentication required.', 'error');
        } else if (error.message.includes('403')) {
            showNotification('Access denied.', 'error');
        } else if (error.message.includes('404')) {
            showNotification('Resource not found.', 'error');
        } else if (error.message.includes('500')) {
            showNotification('Server error. Please try again later.', 'error');
        } else {
            showNotification('An error occurred. Please try again.', 'error');
        }
    }

    handleOnline() {
        this.isOnline = true;
        showNotification('Connection restored', 'success');
        this.processQueue();
    }

    handleOffline() {
        this.isOnline = false;
        showNotification('No internet connection', 'warning');
    }

    // ========================================
    // Request Queue Management
    // ========================================

    queueRequest(request) {
        this.requestQueue.push(request);
    }

    async processQueue() {
        while (this.requestQueue.length > 0 && this.isOnline) {
            const request = this.requestQueue.shift();
            try {
                await request();
            } catch (error) {
                console.error('Queue processing error:', error);
            }
        }
    }
}

// ========================================
// WebSocket Service (Socket.IO)
// ========================================

class WebSocketService {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = API_CONFIG.websocket.maxReconnectAttempts;
        this.reconnectInterval = API_CONFIG.websocket.reconnectInterval;
        this.listeners = {};
        this.isConnected = false;
    }

    connect() {
        try {
            // Socket.IO connection
            this.socket = io(API_CONFIG.websocket.url, {
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectInterval
            });
            
            this.socket.on('connect', () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                console.log('✅ Socket.IO connected');
                showNotification('Real-time monitoring active', 'success');
                this.emit('connected');
            });

            // Listen for anomaly events
            this.socket.on('anomaly', (data) => {
                console.log('📊 New anomaly received:', data);
                this.emit('anomaly', data);
            });
            
            // Listen for traffic updates
            this.socket.on('traffic_update', (data) => {
                console.log('📈 Traffic update received');
                this.emit('traffic', data);
            });
            
            // Listen for alert events
            this.socket.on('alert', (data) => {
                console.log('⚠️ New alert received:', data);
                this.emit('alert', data);
            });

            this.socket.on('disconnect', (reason) => {
                this.isConnected = false;
                console.log('❌ Socket.IO disconnected:', reason);
                if (reason === 'io server disconnect') {
                    // Server disconnected, reconnect manually
                    this.socket.connect();
                }
                this.emit('disconnected', reason);
            });
            
            this.socket.on('connect_error', (error) => {
                console.error('❌ Socket.IO connection error:', error);
                this.emit('error', error);
            });
            
            this.socket.on('reconnect', (attemptNumber) => {
                console.log(`🔄 Reconnected after ${attemptNumber} attempts`);
                showNotification('Reconnected to server', 'success');
            });
            
            this.socket.on('reconnect_attempt', (attemptNumber) => {
                console.log(`🔄 Reconnecting... Attempt ${attemptNumber}`);
            });
            
            this.socket.on('reconnect_failed', () => {
                console.error('❌ Failed to reconnect');
                showNotification('Unable to establish real-time connection', 'error');
            });
            
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.emit('error', error);
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.listeners[event]) return;
        this.listeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event listener for ${event}:`, error);
            }
        });
    }

    send(event, data) {
        if (this.isConnected && this.socket) {
            this.socket.emit(event, data);
        } else {
            console.warn('Socket.IO not connected');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
            console.log('🔌 Socket.IO disconnected manually');
        }
    }
}

// ========================================
// Mock Data Generator (for development/testing)
// ========================================

class MockDataGenerator {
    static generateAnomaly() {
        const types = Object.keys(ANOMALY_TYPES);
        const severities = Object.keys(SEVERITY_LEVELS);
        
        return {
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
            sourceIp: this.generateIP(),
            destinationIp: this.generateIP(),
            type: ANOMALY_TYPES[types[Math.floor(Math.random() * types.length)]],
            severity: severities[Math.floor(Math.random() * severities.length)].toLowerCase(),
            confidence: Math.floor(Math.random() * 30 + 70),
            status: ['active', 'blocked', 'pending'][Math.floor(Math.random() * 3)],
            description: 'Anomalous network behavior detected'
        };
    }

    static generateIP() {
        return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
    }

    static generateTrafficData(points = 20) {
        const data = [];
        const now = Date.now();
        for (let i = points - 1; i >= 0; i--) {
            data.push({
                timestamp: new Date(now - i * 1000).toISOString(),
                value: Math.floor(Math.random() * 100 + 50)
            });
        }
        return data;
    }

    static generateAnomalies(count = 10) {
        return Array.from({ length: count }, () => this.generateAnomaly());
    }
}

// ========================================
// Initialize Services
// ========================================

const apiService = new APIService();
const wsService = new WebSocketService();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.apiService = apiService;
    window.wsService = wsService;
    window.MockDataGenerator = MockDataGenerator;
}
