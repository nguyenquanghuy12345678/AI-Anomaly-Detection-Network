// ========================================
// Dashboard Management
// ========================================

class DashboardManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = API_CONFIG.pagination.defaultPageSize;
        this.anomalies = [];
        this.totalPages = 1;
        this.filters = {
            search: '',
            severity: 'all',
            status: 'all'
        };
    }

    // ========================================
    // Initialize Dashboard
    // ========================================

    async initialize() {
        try {
            await this.loadInitialData();
            this.setupEventListeners();
            this.startRealTimeUpdates();
            chartManager.initializeAllCharts();
            this.startChartUpdates();
        } catch (error) {
            console.error('Dashboard initialization error:', error);
            showNotification('Failed to initialize dashboard', 'error');
        }
    }

    // ========================================
    // Load Initial Data
    // ========================================

    async loadInitialData() {
        await Promise.all([
            this.updateMetrics(),
            this.updateSystemStatus(),
            this.loadAnomaliesTable(),
            loadTrafficData(),
            loadAnomalyData(),
            loadThreatDistribution(),
            loadConfidenceData()
        ]);
    }

    // ========================================
    // Update Metrics
    // ========================================

    async updateMetrics() {
        try {
            // In production, replace with actual API call
            // const stats = await apiService.getNetworkStats();
            
            // Using mock data for now
            const stats = {
                totalTraffic: Math.floor(Math.random() * 1000 + 500),
                anomalyCount: Math.floor(Math.random() * 50 + 10),
                blockedThreats: Math.floor(Math.random() * 30 + 5),
                avgResponseTime: Math.floor(Math.random() * 100 + 50)
            };

            updateElement('totalTraffic', stats.totalTraffic);
            updateElement('anomalyCount', stats.anomalyCount);
            updateElement('blockedThreats', stats.blockedThreats);
            updateElement('avgResponseTime', stats.avgResponseTime + 'ms');

            // Update sidebar quick stats
            updateElement('totalAnomalies', stats.anomalyCount);
            updateElement('activeConnections', Math.floor(Math.random() * 100 + 50));
            updateElement('detectionRate', '98.5%');
        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    }

    // ========================================
    // Update System Status
    // ========================================

    async updateSystemStatus() {
        try {
            // In production, replace with actual API call
            // const status = await apiService.getSystemStatus();
            
            // Using mock data for now
            const status = {
                aiModel: 'Active',
                networkMonitor: 'Running',
                database: 'Connected'
            };

            updateElement('aiModelStatus', status.aiModel);
            updateElement('networkMonitorStatus', status.networkMonitor);
            updateElement('databaseStatus', status.database);
        } catch (error) {
            console.error('Error updating system status:', error);
        }
    }

    // ========================================
    // Load Anomalies Table
    // ========================================

    async loadAnomaliesTable() {
        try {
            // In production, replace with actual API call
            // const response = await apiService.getAnomalies(this.currentPage, this.pageSize);
            
            // Using mock data for now
            this.anomalies = MockDataGenerator.generateAnomalies(this.pageSize);
            this.totalPages = 5;

            this.renderAnomaliesTable();
            this.updatePagination();
        } catch (error) {
            console.error('Error loading anomalies:', error);
            showNotification('Failed to load anomalies', 'error');
        }
    }

    // ========================================
    // Render Anomalies Table
    // ========================================

    renderAnomaliesTable() {
        const tbody = document.getElementById('anomaliesTableBody');
        if (!tbody) return;

        if (this.anomalies.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="no-data">No anomalies found</td></tr>';
            return;
        }

        tbody.innerHTML = this.anomalies.map(anomaly => `
            <tr data-id="${anomaly.id}">
                <td class="timestamp">${formatTime(anomaly.timestamp, 'full')}</td>
                <td class="ip-address">${anomaly.sourceIp}</td>
                <td class="ip-address">${anomaly.destinationIp}</td>
                <td>${anomaly.type}</td>
                <td><span class="badge ${anomaly.severity}">${anomaly.severity}</span></td>
                <td>
                    <div class="confidence-bar">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${anomaly.confidence}%"></div>
                        </div>
                        <span class="confidence-value">${anomaly.confidence}%</span>
                    </div>
                </td>
                <td><span class="badge ${anomaly.status}">${anomaly.status}</span></td>
                <td>
                    <button class="action-btn" onclick="viewAnomalyDetails('${anomaly.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn danger" onclick="blockAnomaly('${anomaly.id}')" title="Block">
                        <i class="fas fa-ban"></i>
                    </button>
                    <button class="action-btn success" onclick="resolveAnomaly('${anomaly.id}')" title="Resolve">
                        <i class="fas fa-check"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    // ========================================
    // Update Pagination
    // ========================================

    updatePagination() {
        const pageInfo = document.getElementById('pageInfo');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');

        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${this.totalPages}`;
        }

        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage === this.totalPages;
        }
    }

    // ========================================
    // Setup Event Listeners
    // ========================================

    setupEventListeners() {
        // Pagination
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.goToPage(this.currentPage - 1));
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.goToPage(this.currentPage + 1));
        }

        // Search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.filters.search = e.target.value;
                    this.loadAnomaliesTable();
                }, 500);
            });
        }

        // Navigation links - handled by router
        // Remove old navigation handler as router now manages this

        // Notification icon
        const notificationIcon = document.querySelector('.notification-icon');
        if (notificationIcon) {
            notificationIcon.addEventListener('click', () => {
                showNotification('No new notifications', 'info');
            });
        }
    }

    // ========================================
    // Pagination Methods
    // ========================================

    goToPage(page) {
        if (page < 1 || page > this.totalPages) return;
        this.currentPage = page;
        this.loadAnomaliesTable();
    }

    // ========================================
    // Real-time Updates
    // ========================================

    startRealTimeUpdates() {
        // Connect WebSocket
        wsService.connect();

        // Listen for new anomalies
        wsService.on('anomaly', (data) => {
            this.handleNewAnomaly(data);
        });

        // Listen for traffic updates
        wsService.on('traffic', (data) => {
            this.handleTrafficUpdate(data);
        });

        // Fallback to polling if WebSocket fails
        setInterval(() => {
            if (!wsService.isConnected) {
                this.updateMetrics();
            }
        }, API_CONFIG.polling.stats);
    }

    handleNewAnomaly(anomaly) {
        // Add to table
        this.anomalies.unshift(anomaly);
        if (this.anomalies.length > this.pageSize) {
            this.anomalies.pop();
        }
        this.renderAnomaliesTable();

        // Update notification badge
        const badge = document.getElementById('notificationCount');
        if (badge) {
            const count = parseInt(badge.textContent) + 1;
            badge.textContent = count;
        }

        // Show notification
        showNotification(`New ${anomaly.severity} anomaly detected!`, 'warning');
        
        // Update metrics
        this.updateMetrics();
    }

    handleTrafficUpdate(data) {
        chartManager.updateTrafficChart([data]);
    }

    // ========================================
    // Chart Updates
    // ========================================

    startChartUpdates() {
        // Update traffic chart
        chartManager.startAutoUpdate('traffic', () => {
            const data = [{
                timestamp: new Date().toISOString(),
                incoming: Math.floor(Math.random() * 100 + 50),
                outgoing: Math.floor(Math.random() * 80 + 30)
            }];
            chartManager.updateTrafficChart(data);
        }, API_CONFIG.charts.realtime);

        // Update other charts periodically
        setInterval(() => {
            loadAnomalyData();
            loadThreatDistribution();
        }, API_CONFIG.charts.historical);
    }
}

// ========================================
// Anomaly Action Functions
// ========================================

async function viewAnomalyDetails(id) {
    try {
        // In production, fetch actual anomaly details
        // const anomaly = await apiService.getAnomalyById(id);
        
        const anomaly = dashboardManager.anomalies.find(a => a.id === id);
        if (!anomaly) return;

        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="alert info">
                <i class="fas fa-info-circle"></i>
                <div>
                    <strong>Anomaly ID:</strong> ${anomaly.id}
                </div>
            </div>
            <div style="display: grid; gap: 1rem;">
                <div>
                    <strong>Timestamp:</strong><br>
                    ${formatTime(anomaly.timestamp, 'full')}
                </div>
                <div>
                    <strong>Source IP:</strong><br>
                    <span class="ip-address">${anomaly.sourceIp}</span>
                </div>
                <div>
                    <strong>Destination IP:</strong><br>
                    <span class="ip-address">${anomaly.destinationIp}</span>
                </div>
                <div>
                    <strong>Type:</strong><br>
                    ${anomaly.type}
                </div>
                <div>
                    <strong>Severity:</strong><br>
                    <span class="badge ${anomaly.severity}">${anomaly.severity}</span>
                </div>
                <div>
                    <strong>Confidence:</strong><br>
                    ${anomaly.confidence}%
                </div>
                <div>
                    <strong>Status:</strong><br>
                    <span class="badge ${anomaly.status}">${anomaly.status}</span>
                </div>
                <div>
                    <strong>Description:</strong><br>
                    ${anomaly.description}
                </div>
            </div>
        `;

        showModal();
    } catch (error) {
        console.error('Error viewing anomaly details:', error);
        showNotification('Failed to load anomaly details', 'error');
    }
}

async function blockAnomaly(id) {
    if (!confirm('Are you sure you want to block this threat?')) return;

    try {
        // In production, call actual API
        // await apiService.blockAnomaly(id);
        
        showNotification('Threat blocked successfully', 'success');
        dashboardManager.loadAnomaliesTable();
    } catch (error) {
        console.error('Error blocking anomaly:', error);
        showNotification('Failed to block threat', 'error');
    }
}

async function resolveAnomaly(id) {
    if (!confirm('Mark this anomaly as resolved?')) return;

    try {
        showNotification('Anomaly resolved', 'success');
        dashboardManager.loadAnomaliesTable();
    } catch (error) {
        console.error('Error resolving anomaly:', error);
        showNotification('Failed to resolve anomaly', 'error');
    }
}

function exportAnomalies() {
    try {
        const csv = convertToCSV(dashboardManager.anomalies);
        downloadFile(csv, 'anomalies.csv', 'text/csv');
        showNotification('Anomalies exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting anomalies:', error);
        showNotification('Failed to export anomalies', 'error');
    }
}

// ========================================
// Initialize Dashboard Manager
// ========================================

const dashboardManager = new DashboardManager();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.dashboardManager = dashboardManager;
    window.viewAnomalyDetails = viewAnomalyDetails;
    window.blockAnomaly = blockAnomaly;
    window.resolveAnomaly = resolveAnomaly;
    window.exportAnomalies = exportAnomalies;
}
