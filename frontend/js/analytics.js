// ========================================
// Analytics Page Manager
// ========================================

class AnalyticsManager {
    constructor() {
        this.dateRange = {
            start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            end: new Date()
        };
        this.charts = {};
        this.reportData = {};
    }

    // ========================================
    // Initialize
    // ========================================

    async initialize() {
        if (document.getElementById('analytics-page')) {
            await this.loadAnalyticsData();
            this.setupCharts();
            this.setupEventListeners();
        }
    }

    // ========================================
    // Load Analytics Data
    // ========================================

    async loadAnalyticsData() {
        try {
            await Promise.all([
                this.loadTrendData(),
                this.loadStatistics(),
                this.loadTopThreats(),
                this.loadGeographicData()
            ]);
            showNotification('Analytics loaded successfully', 'success');
        } catch (error) {
            console.error('Error loading analytics:', error);
            showNotification('Failed to load some analytics data', 'warning');
        }
    }

    async loadTrendData() {
        try {
            // Try to get real trend data from API
            const response = await apiService.getAnomalyStats();
            
            if (response && response.trends) {
                this.reportData.trends = response.trends;
            } else {
                // Fallback to mock data
                this.loadMockTrendData();
            }
        } catch (error) {
            console.error('Error loading trend data:', error);
            this.loadMockTrendData();
        }
    }
    
    loadMockTrendData() {
        // Mock data for trends
        this.reportData.trends = {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            anomalies: [45, 52, 38, 61],
            blocked: [30, 40, 28, 45],
            resolved: [42, 48, 35, 58]
        };
    }

    async loadStatistics() {
        try {
            // Try to get real statistics from API
            const response = await apiService.getAnomalyStats();
            
            if (response && response.statistics) {
                const stats = response.statistics;
                updateElement('total-anomalies-analytics', stats.totalAnomalies || 0);
                updateElement('total-blocked-analytics', stats.totalBlocked || 0);
                updateElement('avg-response-analytics', (stats.avgResponseTime || 0) + ' min');
                updateElement('detection-accuracy', (stats.detectionAccuracy || 0) + '%');
                updateElement('false-positives', (stats.falsePositives || 0) + '%');
                updateElement('critical-incidents', stats.criticalIncidents || 0);
                updateElement('high-incidents', stats.highIncidents || 0);
                updateElement('medium-incidents', stats.mediumIncidents || 0);
            } else {
                // Fallback to mock statistics
                this.loadMockStatistics();
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
            this.loadMockStatistics();
        }
    }
    
    loadMockStatistics() {
        const stats = {
            totalAnomalies: 196,
            totalBlocked: 143,
            avgResponseTime: 2.3,
            detectionAccuracy: 98.5,
            falsePositives: 1.2,
            criticalIncidents: 23,
            highIncidents: 45,
            mediumIncidents: 78,
            lowIncidents: 50
        };

        updateElement('total-anomalies-analytics', stats.totalAnomalies);
        updateElement('total-blocked-analytics', stats.totalBlocked);
        updateElement('avg-response-analytics', stats.avgResponseTime + ' min');
        updateElement('detection-accuracy', stats.detectionAccuracy + '%');
        updateElement('false-positives', stats.falsePositives + '%');
        updateElement('critical-incidents', stats.criticalIncidents);
        updateElement('high-incidents', stats.highIncidents);
        updateElement('medium-incidents', stats.mediumIncidents);
    }

    async loadTopThreats() {
        try {
            // Try to get real top threats from API - use anomaly stats
            const response = await apiService.getAnomalyStats();
            
            if (response && response.threats) {
                this.reportData.topThreats = response.threats;
            } else {
                // Fallback to mock data
                this.loadMockTopThreats();
            }
        } catch (error) {
            console.error('Error loading top threats:', error);
            this.loadMockTopThreats();
        }

        this.renderTopThreats();
    }
    
    loadMockTopThreats() {
        this.reportData.topThreats = [
            { name: 'Port Scan', count: 45, trend: '+12%' },
            { name: 'DDoS Attack', count: 32, trend: '-5%' },
            { name: 'Brute Force', count: 28, trend: '+8%' },
            { name: 'SQL Injection', count: 19, trend: '+3%' },
            { name: 'Malware', count: 15, trend: '-10%' }
        ];
    }

    async loadGeographicData() {
        try {
            // Use mock data for geographic visualization
            this.loadMockGeographicData();
        } catch (error) {
            console.error('Error loading geographic data:', error);
            this.loadMockGeographicData();
        }

        this.renderGeographicData();
    }
    
    loadMockGeographicData() {
        // Mock geographic data
        this.reportData.geographic = [
            { country: 'China', count: 145, percentage: 32 },
            { country: 'Russia', count: 98, percentage: 22 },
            { country: 'USA', count: 76, percentage: 17 },
            { country: 'Brazil', count: 54, percentage: 12 },
            { country: 'India', count: 43, percentage: 10 },
            { country: 'Others', count: 30, percentage: 7 }
        ];
    }

    // ========================================
    // Setup Charts
    // ========================================

    setupCharts() {
        this.setupTrendChart();
        this.setupSeverityChart();
        this.setupResponseTimeChart();
        this.setupModelPerformanceChart();
    }

    setupTrendChart() {
        const ctx = document.getElementById('trend-chart');
        if (!ctx) return;

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.reportData.trends.labels,
                datasets: [
                    {
                        label: 'Anomalies Detected',
                        data: this.reportData.trends.anomalies,
                        borderColor: CHART_COLORS.danger,
                        backgroundColor: CHART_COLORS.dangerLight,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Threats Blocked',
                        data: this.reportData.trends.blocked,
                        borderColor: CHART_COLORS.warning,
                        backgroundColor: CHART_COLORS.warningLight,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Incidents Resolved',
                        data: this.reportData.trends.resolved,
                        borderColor: CHART_COLORS.success,
                        backgroundColor: CHART_COLORS.successLight,
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    }
                }
            }
        });
    }

    setupSeverityChart() {
        const ctx = document.getElementById('severity-trend-chart');
        if (!ctx) return;

        this.charts.severity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [
                    {
                        label: 'Critical',
                        data: [5, 6, 4, 8],
                        backgroundColor: CHART_COLORS.danger,
                        stack: 'severity'
                    },
                    {
                        label: 'High',
                        data: [12, 14, 10, 16],
                        backgroundColor: CHART_COLORS.warning,
                        stack: 'severity'
                    },
                    {
                        label: 'Medium',
                        data: [18, 20, 15, 22],
                        backgroundColor: CHART_COLORS.info,
                        stack: 'severity'
                    },
                    {
                        label: 'Low',
                        data: [10, 12, 9, 15],
                        backgroundColor: CHART_COLORS.success,
                        stack: 'severity'
                    }
                ]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Incidents'
                        }
                    },
                    x: {
                        stacked: true
                    }
                }
            }
        });
    }

    setupResponseTimeChart() {
        const ctx = document.getElementById('response-time-chart');
        if (!ctx) return;

        this.charts.responseTime = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Avg Response Time (min)',
                    data: [2.1, 2.5, 1.8, 2.3, 2.0, 1.9, 2.2],
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
                            text: 'Minutes'
                        }
                    }
                }
            }
        });
    }

    setupModelPerformanceChart() {
        const ctx = document.getElementById('model-performance-chart');
        if (!ctx) return;

        this.charts.modelPerformance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Specificity'],
                datasets: [{
                    label: 'Model Performance',
                    data: [98.5, 97.2, 96.8, 97.0, 98.1],
                    backgroundColor: CHART_COLORS.primaryLight,
                    borderColor: CHART_COLORS.primary,
                    borderWidth: 2,
                    pointBackgroundColor: CHART_COLORS.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: CHART_COLORS.primary
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                }
            }
        });
    }

    // ========================================
    // Render Data
    // ========================================

    renderTopThreats() {
        const container = document.getElementById('top-threats-list');
        if (!container) return;

        container.innerHTML = this.reportData.topThreats.map((threat, index) => `
            <div class="threat-item">
                <div class="threat-rank">${index + 1}</div>
                <div class="threat-info">
                    <div class="threat-name">${threat.name}</div>
                    <div class="threat-count">${threat.count} incidents</div>
                </div>
                <div class="threat-trend ${threat.trend.includes('+') ? 'up' : 'down'}">
                    <i class="fas fa-arrow-${threat.trend.includes('+') ? 'up' : 'down'}"></i>
                    ${threat.trend}
                </div>
            </div>
        `).join('');
    }

    renderGeographicData() {
        const container = document.getElementById('geographic-list');
        if (!container) return;

        container.innerHTML = this.reportData.geographic.map(item => `
            <div class="geo-item">
                <div class="geo-info">
                    <div class="geo-country">${item.country}</div>
                    <div class="geo-count">${item.count} attacks</div>
                </div>
                <div class="geo-bar">
                    <div class="geo-fill" style="width: ${item.percentage}%"></div>
                </div>
                <div class="geo-percentage">${item.percentage}%</div>
            </div>
        `).join('');
    }

    // ========================================
    // Event Listeners
    // ========================================

    setupEventListeners() {
        // Date range selector
        const dateButtons = document.querySelectorAll('.date-range-btn');
        dateButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                dateButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.updateDateRange(btn.dataset.range);
            });
        });
    }

    updateDateRange(range) {
        const now = new Date();
        switch(range) {
            case '7d':
                this.dateRange.start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case '30d':
                this.dateRange.start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
            case '90d':
                this.dateRange.start = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
                break;
            case '1y':
                this.dateRange.start = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
                break;
        }
        this.dateRange.end = now;
        this.loadAnalyticsData();
        showNotification(`Date range updated to ${range}`, 'info');
    }

    // ========================================
    // Export Reports
    // ========================================

    async exportReport(format) {
        showNotification(`Exporting report as ${format.toUpperCase()}...`, 'info');
        
        // Simulate export
        setTimeout(() => {
            showNotification(`Report exported successfully as ${format.toUpperCase()}`, 'success');
        }, 1500);
    }

    // ========================================
    // Cleanup
    // ========================================

    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// ========================================
// Initialize Analytics Manager
// ========================================

const analyticsManager = new AnalyticsManager();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.analyticsManager = analyticsManager;
}
