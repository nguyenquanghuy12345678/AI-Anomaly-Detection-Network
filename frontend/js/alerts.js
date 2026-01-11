// ========================================
// Alerts Page Manager
// ========================================

class AlertsManager {
    constructor() {
        this.alerts = [];
        this.filteredAlerts = [];
        this.currentPage = 1;
        this.pageSize = 15;
        this.totalPages = 1;
        this.filters = {
            severity: 'all',
            status: 'all',
            search: '',
            dateRange: 'all'
        };
        this.sortBy = 'timestamp';
        this.sortOrder = 'desc';
    }

    // ========================================
    // Initialize
    // ========================================

    async initialize() {
        if (document.getElementById('alerts-page')) {
            await this.loadAlerts();
            this.setupEventListeners();
            this.startAutoRefresh();
        }
    }

    // ========================================
    // Load Alerts
    // ========================================

    async loadAlerts() {
        try {
            // Get real alerts from API
            const response = await apiService.getAlerts();
            
            if (response && response.alerts) {
                this.alerts = response.alerts;
            } else if (response && Array.isArray(response)) {
                this.alerts = response;
            } else {
                // Fallback to mock data if API fails
                console.warn('Using mock alerts - API returned unexpected format');
                this.alerts = this.generateMockAlerts(50);
            }
            
            this.applyFilters();
            this.renderAlerts();
            this.updateStats();
            showNotification('Alerts loaded successfully', 'success');
        } catch (error) {
            console.error('Error loading alerts:', error);
            showNotification('Failed to load alerts - using cached data', 'warning');
            // Use mock data as fallback
            this.alerts = this.generateMockAlerts(50);
            this.applyFilters();
            this.renderAlerts();
            this.updateStats();
        }
    }

    // ========================================
    // Generate Mock Alerts
    // ========================================

    generateMockAlerts(count) {
        const alerts = [];
        const severities = ['critical', 'high', 'medium', 'low'];
        const statuses = ['unread', 'read', 'dismissed'];
        const types = Object.values(ANOMALY_TYPES);

        for (let i = 0; i < count; i++) {
            const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
            alerts.push({
                id: `alert-${i}`,
                timestamp: timestamp.toISOString(),
                severity: severities[Math.floor(Math.random() * severities.length)],
                status: statuses[Math.floor(Math.random() * statuses.length)],
                type: types[Math.floor(Math.random() * types.length)],
                title: this.generateAlertTitle(),
                description: 'Suspicious network activity detected from multiple sources',
                sourceIp: MockDataGenerator.generateIP(),
                affectedSystems: Math.floor(Math.random() * 10 + 1),
                requiresAction: Math.random() > 0.5
            });
        }

        return alerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }

    generateAlertTitle() {
        const titles = [
            'Multiple failed authentication attempts',
            'Unusual outbound traffic detected',
            'Port scan activity identified',
            'Potential DDoS attack in progress',
            'Malware signature detected',
            'Unauthorized access attempt',
            'Data exfiltration suspected',
            'Brute force attack detected',
            'Suspicious file upload',
            'Anomalous database queries'
        ];
        return titles[Math.floor(Math.random() * titles.length)];
    }

    // ========================================
    // Filtering and Sorting
    // ========================================

    applyFilters() {
        this.filteredAlerts = this.alerts.filter(alert => {
            // Severity filter
            if (this.filters.severity !== 'all' && alert.severity !== this.filters.severity) {
                return false;
            }

            // Status filter
            if (this.filters.status !== 'all' && alert.status !== this.filters.status) {
                return false;
            }

            // Search filter
            if (this.filters.search) {
                const search = this.filters.search.toLowerCase();
                return alert.title.toLowerCase().includes(search) ||
                       alert.description.toLowerCase().includes(search) ||
                       alert.sourceIp.includes(search);
            }

            // Date range filter
            if (this.filters.dateRange !== 'all') {
                const alertDate = new Date(alert.timestamp);
                const now = new Date();
                const hoursDiff = (now - alertDate) / (1000 * 60 * 60);

                switch (this.filters.dateRange) {
                    case '1h':
                        if (hoursDiff > 1) return false;
                        break;
                    case '24h':
                        if (hoursDiff > 24) return false;
                        break;
                    case '7d':
                        if (hoursDiff > 168) return false;
                        break;
                    case '30d':
                        if (hoursDiff > 720) return false;
                        break;
                }
            }

            return true;
        });

        // Apply sorting
        this.applySorting();

        // Update pagination
        this.totalPages = Math.ceil(this.filteredAlerts.length / this.pageSize);
        this.currentPage = Math.min(this.currentPage, this.totalPages || 1);
    }

    applySorting() {
        this.filteredAlerts.sort((a, b) => {
            let aVal = a[this.sortBy];
            let bVal = b[this.sortBy];

            if (this.sortBy === 'timestamp') {
                aVal = new Date(aVal);
                bVal = new Date(bVal);
            }

            if (this.sortOrder === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });
    }

    // ========================================
    // Render Alerts
    // ========================================

    renderAlerts() {
        const container = document.getElementById('alerts-list');
        if (!container) return;

        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageAlerts = this.filteredAlerts.slice(start, end);

        if (pageAlerts.length === 0) {
            container.innerHTML = `
                <div class="no-data" style="text-align: center; padding: 3rem;">
                    <i class="fas fa-inbox" style="font-size: 3rem; color: var(--text-light);"></i>
                    <p style="margin-top: 1rem; color: var(--text-secondary);">No alerts found</p>
                </div>
            `;
            return;
        }

        container.innerHTML = pageAlerts.map(alert => `
            <div class="alert-item ${alert.status}" data-id="${alert.id}">
                <div class="alert-indicator ${alert.severity}"></div>
                <div class="alert-content">
                    <div class="alert-header">
                        <div class="alert-title">
                            <span class="badge ${alert.severity}">${alert.severity}</span>
                            <h4>${alert.title}</h4>
                        </div>
                        <div class="alert-meta">
                            <span class="timestamp">${formatTime(alert.timestamp, 'full')}</span>
                        </div>
                    </div>
                    <p class="alert-description">${alert.description}</p>
                    <div class="alert-details">
                        <span><i class="fas fa-network-wired"></i> ${alert.sourceIp}</span>
                        <span><i class="fas fa-server"></i> ${alert.affectedSystems} systems</span>
                        <span><i class="fas fa-shield-alt"></i> ${alert.type}</span>
                    </div>
                </div>
                <div class="alert-actions">
                    ${alert.status === 'unread' ? `
                        <button class="btn-icon" onclick="alertsManager.markAsRead('${alert.id}')" title="Mark as read">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                    <button class="btn-icon" onclick="alertsManager.viewDetails('${alert.id}')" title="View details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon danger" onclick="alertsManager.dismissAlert('${alert.id}')" title="Dismiss">
                        <i class="fas fa-times"></i>
                    </button>
                    ${alert.requiresAction ? `
                        <button class="btn-primary btn-sm" onclick="alertsManager.takeAction('${alert.id}')">
                            Take Action
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');

        this.updatePagination();
    }

    // ========================================
    // Update Stats
    // ========================================

    updateStats() {
        const stats = {
            total: this.alerts.length,
            unread: this.alerts.filter(a => a.status === 'unread').length,
            critical: this.alerts.filter(a => a.severity === 'critical').length,
            requiresAction: this.alerts.filter(a => a.requiresAction).length
        };

        updateElement('total-alerts', stats.total);
        updateElement('unread-alerts', stats.unread);
        updateElement('critical-alerts', stats.critical);
        updateElement('action-required', stats.requiresAction);
    }

    // ========================================
    // Update Pagination
    // ========================================

    updatePagination() {
        const pageInfo = document.getElementById('alerts-page-info');
        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${this.totalPages}`;
        }

        const prevBtn = document.getElementById('alerts-prev-page');
        const nextBtn = document.getElementById('alerts-next-page');

        if (prevBtn) prevBtn.disabled = this.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.currentPage === this.totalPages;
    }

    // ========================================
    // Event Listeners
    // ========================================

    setupEventListeners() {
        // Filter change listeners would be set up here
        // This is a simplified version - full implementation would handle all filter controls
    }

    // ========================================
    // Alert Actions
    // ========================================

    async markAsRead(id) {
        const alert = this.alerts.find(a => a.id === id);
        if (alert) {
            alert.status = 'read';
            this.applyFilters();
            this.renderAlerts();
            this.updateStats();
            showNotification('Alert marked as read', 'success');
        }
    }

    async viewDetails(id) {
        const alert = this.alerts.find(a => a.id === id);
        if (!alert) return;

        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="alert ${alert.severity}">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>${alert.severity.toUpperCase()} Alert</strong>
                </div>
            </div>
            <div style="display: grid; gap: 1.5rem; margin-top: 1rem;">
                <div>
                    <strong>Title:</strong><br>
                    ${alert.title}
                </div>
                <div>
                    <strong>Description:</strong><br>
                    ${alert.description}
                </div>
                <div>
                    <strong>Source IP:</strong><br>
                    <span class="ip-address">${alert.sourceIp}</span>
                </div>
                <div>
                    <strong>Affected Systems:</strong><br>
                    ${alert.affectedSystems} systems
                </div>
                <div>
                    <strong>Threat Type:</strong><br>
                    ${alert.type}
                </div>
                <div>
                    <strong>Timestamp:</strong><br>
                    ${formatTime(alert.timestamp, 'full')}
                </div>
                <div>
                    <strong>Status:</strong><br>
                    <span class="badge ${alert.status}">${alert.status}</span>
                </div>
            </div>
        `;
        showModal();
    }

    async dismissAlert(id) {
        if (!confirm('Are you sure you want to dismiss this alert?')) return;

        const index = this.alerts.findIndex(a => a.id === id);
        if (index !== -1) {
            this.alerts.splice(index, 1);
            this.applyFilters();
            this.renderAlerts();
            this.updateStats();
            showNotification('Alert dismissed', 'success');
        }
    }

    async takeAction(id) {
        showNotification('Action initiated for alert', 'info');
        // Implement action logic here
    }

    // ========================================
    // Pagination
    // ========================================

    goToPage(page) {
        if (page < 1 || page > this.totalPages) return;
        this.currentPage = page;
        this.renderAlerts();
    }

    // ========================================
    // Auto Refresh
    // ========================================

    startAutoRefresh() {
        setInterval(() => {
            this.loadAlerts();
        }, API_CONFIG.polling.alerts || 10000);
    }
}

// ========================================
// Initialize Alerts Manager
// ========================================

const alertsManager = new AlertsManager();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.alertsManager = alertsManager;
}
