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

    // ========================================
    // System API Methods
    // ========================================

    async getSystemStatus() {
        return this.get(this.endpoints.systemStatus);
    }

    async getSystemHealth() {
        return this.get(this.endpoints.systemHealth);
    }

    // ========================================
    // Alert API Methods
    // ========================================

    async getAlerts(unreadOnly = false) {
        const endpoint = unreadOnly ? this.endpoints.alertsUnread : this.endpoints.alerts;
        return this.get(endpoint);
    }

    async markAlertAsRead(id) {
        return this.put(`${this.endpoints.alerts}/${id}/read`);
    }

    async deleteAlert(id) {
        return this.delete(`${this.endpoints.alerts}/${id}`);
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
// WebSocket Service
// ========================================

class WebSocketService {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = API_CONFIG.websocket.maxReconnectAttempts;
        this.reconnectInterval = API_CONFIG.websocket.reconnectInterval;
        this.listeners = {};
        this.isConnected = false;
    }

    connect() {
        try {
            this.ws = new WebSocket(API_CONFIG.websocket.url);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                console.log('WebSocket connected');
                showNotification('Real-time monitoring active', 'success');
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('WebSocket message parse error:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };

            this.ws.onclose = () => {
                this.isConnected = false;
                console.log('WebSocket disconnected');
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            setTimeout(() => this.connect(), this.reconnectInterval);
        } else {
            showNotification('Unable to establish real-time connection', 'error');
        }
    }

    handleMessage(data) {
        const { type, payload } = data;
        this.emit(type, payload);
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
        this.listeners[event].forEach(callback => callback(data));
    }

    send(type, payload) {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify({ type, payload }));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
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
