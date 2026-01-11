// ========================================
// Chart Manager
// ========================================

class ChartManager {
    constructor() {
        this.charts = {};
        this.updateIntervals = {};
    }

    // ========================================
    // Create Traffic Chart
    // ========================================

    createTrafficChart() {
        const ctx = document.getElementById('trafficChart');
        if (!ctx) return;

        const config = {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Incoming Traffic',
                        data: [],
                        borderColor: CHART_COLORS.primary,
                        backgroundColor: CHART_COLORS.primaryLight,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        borderWidth: 2
                    },
                    {
                        label: 'Outgoing Traffic',
                        data: [],
                        borderColor: CHART_COLORS.info,
                        backgroundColor: CHART_COLORS.infoLight,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                ...CHART_DEFAULTS,
                animation: {
                    duration: 750
                },
                scales: {
                    ...CHART_DEFAULTS.scales,
                    y: {
                        ...CHART_DEFAULTS.scales.y,
                        title: {
                            display: true,
                            text: 'Traffic (MB/s)'
                        }
                    },
                    x: {
                        ...CHART_DEFAULTS.scales.x,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        };

        this.charts.traffic = new Chart(ctx, config);
        return this.charts.traffic;
    }

    // ========================================
    // Create Anomaly Chart
    // ========================================

    createAnomalyChart() {
        const ctx = document.getElementById('anomalyChart');
        if (!ctx) return;

        const config = {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Critical',
                        data: [],
                        backgroundColor: CHART_COLORS.danger,
                        borderRadius: 4
                    },
                    {
                        label: 'High',
                        data: [],
                        backgroundColor: CHART_COLORS.warning,
                        borderRadius: 4
                    },
                    {
                        label: 'Medium',
                        data: [],
                        backgroundColor: CHART_COLORS.info,
                        borderRadius: 4
                    },
                    {
                        label: 'Low',
                        data: [],
                        backgroundColor: CHART_COLORS.success,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    ...CHART_DEFAULTS.scales,
                    y: {
                        ...CHART_DEFAULTS.scales.y,
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Number of Anomalies'
                        }
                    },
                    x: {
                        ...CHART_DEFAULTS.scales.x,
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Time Period'
                        }
                    }
                }
            }
        };

        this.charts.anomaly = new Chart(ctx, config);
        return this.charts.anomaly;
    }

    // ========================================
    // Create Threat Distribution Chart
    // ========================================

    createThreatDistributionChart() {
        const ctx = document.getElementById('threatDistributionChart');
        if (!ctx) return;

        const config = {
            type: 'doughnut',
            data: {
                labels: Object.values(ANOMALY_TYPES),
                datasets: [{
                    data: [],
                    backgroundColor: [
                        CHART_COLORS.danger,
                        CHART_COLORS.warning,
                        CHART_COLORS.info,
                        CHART_COLORS.success,
                        CHART_COLORS.primary,
                        CHART_COLORS.secondary,
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                cutout: '65%',
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    legend: {
                        ...CHART_DEFAULTS.plugins.legend,
                        position: 'right'
                    },
                    tooltip: {
                        ...CHART_DEFAULTS.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };

        this.charts.threatDistribution = new Chart(ctx, config);
        return this.charts.threatDistribution;
    }

    // ========================================
    // Create Confidence Chart
    // ========================================

    createConfidenceChart() {
        const ctx = document.getElementById('confidenceChart');
        if (!ctx) return;

        const config = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'AI Model Confidence',
                    data: [],
                    borderColor: CHART_COLORS.success,
                    backgroundColor: CHART_COLORS.successLight,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: CHART_COLORS.success,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderWidth: 3
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    ...CHART_DEFAULTS.scales,
                    y: {
                        ...CHART_DEFAULTS.scales.y,
                        min: 0,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Confidence (%)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        ...CHART_DEFAULTS.scales.x,
                        title: {
                            display: true,
                            text: 'Detection Events'
                        }
                    }
                },
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    tooltip: {
                        ...CHART_DEFAULTS.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `Confidence: ${context.parsed.y}%`;
                            }
                        }
                    }
                }
            }
        };

        this.charts.confidence = new Chart(ctx, config);
        return this.charts.confidence;
    }

    // ========================================
    // Update Chart Data
    // ========================================

    updateTrafficChart(data) {
        if (!this.charts.traffic) return;

        const chart = this.charts.traffic;
        const maxDataPoints = 20;

        // Add new data
        data.forEach(point => {
            chart.data.labels.push(formatTime(point.timestamp, 'short'));
            chart.data.datasets[0].data.push(point.incoming);
            chart.data.datasets[1].data.push(point.outgoing);
        });

        // Remove old data if exceeds max points
        while (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }

        chart.update('none');
    }

    updateAnomalyChart(data) {
        if (!this.charts.anomaly) return;

        const chart = this.charts.anomaly;
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.critical;
        chart.data.datasets[1].data = data.high;
        chart.data.datasets[2].data = data.medium;
        chart.data.datasets[3].data = data.low;

        chart.update();
    }

    updateThreatDistributionChart(data) {
        if (!this.charts.threatDistribution) return;

        const chart = this.charts.threatDistribution;
        chart.data.datasets[0].data = data;
        chart.update();
    }

    updateConfidenceChart(data) {
        if (!this.charts.confidence) return;

        const chart = this.charts.confidence;
        const maxDataPoints = 30;

        chart.data.labels.push(data.label || formatTime(new Date(), 'short'));
        chart.data.datasets[0].data.push(data.value);

        // Remove old data if exceeds max points
        while (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update('none');
    }

    // ========================================
    // Chart Management
    // ========================================

    initializeAllCharts() {
        this.createTrafficChart();
        this.createAnomalyChart();
        this.createThreatDistributionChart();
        this.createConfidenceChart();
    }

    destroyChart(chartName) {
        if (this.charts[chartName]) {
            this.charts[chartName].destroy();
            delete this.charts[chartName];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartName => {
            this.destroyChart(chartName);
        });
    }

    getChart(chartName) {
        return this.charts[chartName];
    }

    // ========================================
    // Auto Update Management
    // ========================================

    startAutoUpdate(chartName, updateFunction, interval) {
        this.stopAutoUpdate(chartName);
        this.updateIntervals[chartName] = setInterval(updateFunction, interval);
    }

    stopAutoUpdate(chartName) {
        if (this.updateIntervals[chartName]) {
            clearInterval(this.updateIntervals[chartName]);
            delete this.updateIntervals[chartName];
        }
    }

    stopAllAutoUpdates() {
        Object.keys(this.updateIntervals).forEach(chartName => {
            this.stopAutoUpdate(chartName);
        });
    }
}

// ========================================
// Chart Refresh Functions
// ========================================

function refreshTrafficChart() {
    showNotification('Refreshing traffic data...', 'info');
    loadTrafficData();
}

function refreshAnomalyChart() {
    showNotification('Refreshing anomaly data...', 'info');
    loadAnomalyData();
}

// ========================================
// Initialize Chart Manager
// ========================================

const chartManager = new ChartManager();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.chartManager = chartManager;
    window.refreshTrafficChart = refreshTrafficChart;
    window.refreshAnomalyChart = refreshAnomalyChart;
}
