// ========================================
// Monitoring Page Manager
// ========================================

class MonitoringManager {
    constructor() {
        this.connections = [];
        this.trafficData = [];
        this.updateInterval = null;
        this.charts = {};
    }

    // ========================================
    // Initialize
    // ========================================

    async initialize() {
        if (document.getElementById('monitoring-page')) {
            await this.loadInitialData();
            this.setupCharts();
            this.setupEventListeners();
            this.startRealTimeUpdates();
        }
    }

    // ========================================
    // Load Initial Data
    // ========================================

    async loadInitialData() {
        await Promise.all([
            this.loadConnections(),
            this.loadTrafficStats(),
            this.updateProtocolDistribution()
        ]);
    }

    // ========================================
    // Load Connections
    // ========================================

    async loadConnections() {
        try {
            // Get real connections from API
            const response = await apiService.get(API_CONFIG.endpoints.connections);
            
            if (response && response.connections) {
                this.connections = response.connections;
            } else if (response && Array.isArray(response)) {
                this.connections = response;
            } else {
                // Fallback to mock data if API fails
                console.warn('Using mock data - API returned unexpected format');
                this.connections = this.generateMockConnections(20);
            }
            
            this.renderConnections();
            this.updateConnectionStats();
        } catch (error) {
            console.error('Error loading connections:', error);
            showNotification('Failed to load connections', 'error');
            // Use mock data as fallback
            this.connections = this.generateMockConnections(20);
            this.renderConnections();
            this.updateConnectionStats();
        }
    }

    generateMockConnections(count) {
        const connections = [];
        const protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'FTP'];
        const states = ['ESTABLISHED', 'LISTENING', 'TIME_WAIT', 'CLOSE_WAIT'];

        for (let i = 0; i < count; i++) {
            connections.push({
                id: `conn-${i}`,
                sourceIp: MockDataGenerator.generateIP(),
                sourcePort: Math.floor(Math.random() * 50000 + 10000),
                destIp: MockDataGenerator.generateIP(),
                destPort: Math.floor(Math.random() * 65535),
                protocol: protocols[Math.floor(Math.random() * protocols.length)],
                state: states[Math.floor(Math.random() * states.length)],
                bytes: Math.floor(Math.random() * 10000000),
                packets: Math.floor(Math.random() * 100000),
                duration: Math.floor(Math.random() * 3600),
                timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString()
            });
        }

        return connections;
    }

    // ========================================
    // Render Connections
    // ========================================

    renderConnections() {
        const tbody = document.getElementById('connections-tbody');
        if (!tbody) return;

        if (this.connections.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="no-data">No active connections</td></tr>';
            return;
        }

        tbody.innerHTML = this.connections.map(conn => `
            <tr>
                <td class="ip-address">${conn.sourceIp}:${conn.sourcePort}</td>
                <td class="ip-address">${conn.destIp}:${conn.destPort}</td>
                <td><span class="badge ${conn.protocol.toLowerCase()}">${conn.protocol}</span></td>
                <td><span class="badge ${conn.state.toLowerCase().replace('_', '-')}">${conn.state}</span></td>
                <td>${this.formatBytes(conn.bytes)}</td>
                <td>${conn.packets.toLocaleString()}</td>
                <td>${this.formatDuration(conn.duration)}</td>
                <td class="timestamp">${formatTime(conn.timestamp, 'time')}</td>
                <td>
                    <button class="btn-icon" onclick="monitoringManager.viewConnectionDetails('${conn.id}')" title="Details">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn-icon danger" onclick="monitoringManager.terminateConnection('${conn.id}')" title="Terminate">
                        <i class="fas fa-ban"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    // ========================================
    // Update Stats
    // ========================================

    updateConnectionStats() {
        const stats = {
            active: this.connections.filter(c => c.state === 'ESTABLISHED').length,
            listening: this.connections.filter(c => c.state === 'LISTENING').length,
            totalBytes: this.connections.reduce((sum, c) => sum + c.bytes, 0),
            totalPackets: this.connections.reduce((sum, c) => sum + c.packets, 0)
        };

        updateElement('active-connections-stat', stats.active);
        updateElement('listening-ports', stats.listening);
        updateElement('total-bytes', this.formatBytes(stats.totalBytes));
        updateElement('total-packets', stats.totalPackets.toLocaleString());
    }

    async loadTrafficStats() {
        try {
            // Get real traffic stats from API
            const response = await apiService.get(API_CONFIG.endpoints.trafficStats);
            
            if (response && response.stats) {
                const stats = response.stats;
                updateElement('bandwidth-usage', stats.bandwidth || 'N/A');
                updateElement('network-latency', stats.latency || 'N/A');
                updateElement('packet-loss', stats.packetLoss || 'N/A');
                updateElement('system-uptime', stats.uptime || 'N/A');
            } else {
                // Fallback to mock stats
                this.loadMockTrafficStats();
            }
        } catch (error) {
            console.error('Error loading traffic stats:', error);
            this.loadMockTrafficStats();
        }
    }
    
    loadMockTrafficStats() {
        const stats = {
            bandwidth: (Math.random() * 100 + 50).toFixed(2) + ' Mbps',
            latency: Math.floor(Math.random() * 50 + 10) + ' ms',
            packetLoss: (Math.random() * 2).toFixed(2) + '%',
            uptime: '99.9%'
        };

        updateElement('bandwidth-usage', stats.bandwidth);
        updateElement('network-latency', stats.latency);
        updateElement('packet-loss', stats.packetLoss);
        updateElement('system-uptime', stats.uptime);
    }

    // ========================================
    // Setup Charts
    // ========================================

    setupCharts() {
        this.setupBandwidthChart();
        this.setupProtocolChart();
        this.setupLatencyChart();
    }

    setupBandwidthChart() {
        const ctx = document.getElementById('bandwidth-chart');
        if (!ctx) return;

        this.charts.bandwidth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Bandwidth (Mbps)',
                    data: [],
                    borderColor: CHART_COLORS.primary,
                    backgroundColor: CHART_COLORS.primaryLight,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Mbps'
                        }
                    }
                }
            }
        });

        // Initialize with data
        for (let i = 0; i < 20; i++) {
            this.updateBandwidthChart();
        }
    }

    setupProtocolChart() {
        const ctx = document.getElementById('protocol-chart');
        if (!ctx) return;

        this.charts.protocol = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'Other'],
                datasets: [{
                    data: [30, 25, 20, 15, 7, 3],
                    backgroundColor: [
                        CHART_COLORS.primary,
                        CHART_COLORS.info,
                        CHART_COLORS.success,
                        CHART_COLORS.warning,
                        CHART_COLORS.danger,
                        CHART_COLORS.secondary
                    ]
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    setupLatencyChart() {
        const ctx = document.getElementById('latency-chart');
        if (!ctx) return;

        this.charts.latency = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Latency (ms)',
                    data: [],
                    backgroundColor: CHART_COLORS.info,
                    borderRadius: 4
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Milliseconds'
                        }
                    }
                }
            }
        });

        // Initialize with data
        for (let i = 0; i < 10; i++) {
            this.updateLatencyChart();
        }
    }

    // ========================================
    // Update Charts
    // ========================================

    updateBandwidthChart() {
        if (!this.charts.bandwidth) return;

        const chart = this.charts.bandwidth;
        const maxPoints = 20;

        chart.data.labels.push(formatTime(new Date(), 'short'));
        chart.data.datasets[0].data.push((Math.random() * 100 + 50).toFixed(2));

        if (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update('none');
    }

    updateLatencyChart() {
        if (!this.charts.latency) return;

        const chart = this.charts.latency;
        const maxPoints = 10;

        chart.data.labels.push(formatTime(new Date(), 'short'));
        chart.data.datasets[0].data.push(Math.floor(Math.random() * 50 + 10));

        if (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update('none');
    }

    updateProtocolDistribution() {
        if (!this.charts.protocol) return;

        const protocols = {};
        this.connections.forEach(conn => {
            protocols[conn.protocol] = (protocols[conn.protocol] || 0) + 1;
        });

        // Update chart with real data if available
    }

    // ========================================
    // Real-time Updates
    // ========================================

    startRealTimeUpdates() {
        this.updateInterval = setInterval(() => {
            this.loadConnections();
            this.updateBandwidthChart();
            this.updateLatencyChart();
            this.loadTrafficStats();
        }, 2000);
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    // ========================================
    // Event Listeners
    // ========================================

    setupEventListeners() {
        // Add event listeners for filters, etc.
    }

    // ========================================
    // Connection Actions
    // ========================================

    viewConnectionDetails(id) {
        const conn = this.connections.find(c => c.id === id);
        if (!conn) return;

        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <h4>Connection Details</h4>
            <div style="display: grid; gap: 1rem; margin-top: 1rem;">
                <div>
                    <strong>Source:</strong><br>
                    <span class="ip-address">${conn.sourceIp}:${conn.sourcePort}</span>
                </div>
                <div>
                    <strong>Destination:</strong><br>
                    <span class="ip-address">${conn.destIp}:${conn.destPort}</span>
                </div>
                <div>
                    <strong>Protocol:</strong><br>
                    ${conn.protocol}
                </div>
                <div>
                    <strong>State:</strong><br>
                    <span class="badge ${conn.state.toLowerCase()}">${conn.state}</span>
                </div>
                <div>
                    <strong>Data Transferred:</strong><br>
                    ${this.formatBytes(conn.bytes)} (${conn.packets.toLocaleString()} packets)
                </div>
                <div>
                    <strong>Duration:</strong><br>
                    ${this.formatDuration(conn.duration)}
                </div>
                <div>
                    <strong>Started:</strong><br>
                    ${formatTime(conn.timestamp, 'full')}
                </div>
            </div>
        `;
        showModal();
    }

    async terminateConnection(id) {
        if (!confirm('Are you sure you want to terminate this connection?')) return;

        const index = this.connections.findIndex(c => c.id === id);
        if (index !== -1) {
            this.connections.splice(index, 1);
            this.renderConnections();
            this.updateConnectionStats();
            showNotification('Connection terminated', 'success');
        }
    }

    // ========================================
    // Utility Methods
    // ========================================

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    // ========================================
    // Cleanup
    // ========================================

    destroy() {
        this.stopRealTimeUpdates();
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// ========================================
// Initialize Monitoring Manager
// ========================================

const monitoringManager = new MonitoringManager();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.monitoringManager = monitoringManager;
}
