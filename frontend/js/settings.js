// ========================================
// Settings Page Manager
// ========================================

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.isDirty = false;
    }

    // ========================================
    // Initialize
    // ========================================

    async initialize() {
        if (document.getElementById('settings-page')) {
            this.loadSettingsUI();
            this.setupEventListeners();
        }
    }

    // ========================================
    // Load/Save Settings
    // ========================================

    loadSettings() {
        const defaultSettings = {
            general: {
                theme: 'light',
                language: 'en',
                timezone: 'UTC',
                dateFormat: 'MM/DD/YYYY',
                autoRefresh: true,
                refreshInterval: 5
            },
            notifications: {
                enabled: true,
                desktop: true,
                email: false,
                sound: true,
                criticalOnly: false
            },
            alerts: {
                criticalThreshold: 90,
                highThreshold: 70,
                mediumThreshold: 50,
                autoBlock: false,
                alertRetention: 30
            },
            display: {
                itemsPerPage: 10,
                showSidebar: true,
                compactMode: false,
                animations: true
            },
            security: {
                sessionTimeout: 30,
                requireAuth: false,
                twoFactor: false,
                ipWhitelist: []
            }
        };

        try {
            const saved = localStorage.getItem('app_settings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (error) {
            console.error('Error loading settings:', error);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('app_settings', JSON.stringify(this.settings));
            this.isDirty = false;
            showNotification('Settings saved successfully', 'success');
            this.applySettings();
        } catch (error) {
            console.error('Error saving settings:', error);
            showNotification('Failed to save settings', 'error');
        }
    }

    // ========================================
    // Load Settings UI
    // ========================================

    loadSettingsUI() {
        // General Settings
        document.getElementById('theme-select').value = this.settings.general.theme;
        document.getElementById('language-select').value = this.settings.general.language;
        document.getElementById('timezone-select').value = this.settings.general.timezone;
        document.getElementById('auto-refresh').checked = this.settings.general.autoRefresh;
        document.getElementById('refresh-interval').value = this.settings.general.refreshInterval;

        // Notification Settings
        document.getElementById('notifications-enabled').checked = this.settings.notifications.enabled;
        document.getElementById('desktop-notifications').checked = this.settings.notifications.desktop;
        document.getElementById('email-notifications').checked = this.settings.notifications.email;
        document.getElementById('sound-alerts').checked = this.settings.notifications.sound;
        document.getElementById('critical-only').checked = this.settings.notifications.criticalOnly;

        // Alert Settings
        document.getElementById('critical-threshold').value = this.settings.alerts.criticalThreshold;
        document.getElementById('high-threshold').value = this.settings.alerts.highThreshold;
        document.getElementById('medium-threshold').value = this.settings.alerts.mediumThreshold;
        document.getElementById('auto-block').checked = this.settings.alerts.autoBlock;
        document.getElementById('alert-retention').value = this.settings.alerts.alertRetention;

        // Display Settings
        document.getElementById('items-per-page').value = this.settings.display.itemsPerPage;
        document.getElementById('show-sidebar').checked = this.settings.display.showSidebar;
        document.getElementById('compact-mode').checked = this.settings.display.compactMode;
        document.getElementById('animations-enabled').checked = this.settings.display.animations;

        // Security Settings
        document.getElementById('session-timeout').value = this.settings.security.sessionTimeout;
        document.getElementById('require-auth').checked = this.settings.security.requireAuth;
        document.getElementById('two-factor').checked = this.settings.security.twoFactor;

        // Update threshold displays
        this.updateThresholdDisplays();
    }

    // ========================================
    // Setup Event Listeners
    // ========================================

    setupEventListeners() {
        // Save button
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            this.collectSettings();
            this.saveSettings();
        });

        // Reset button
        document.getElementById('reset-settings-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to reset all settings to default?')) {
                this.resetSettings();
            }
        });

        // Export button
        document.getElementById('export-settings-btn').addEventListener('click', () => {
            this.exportSettings();
        });

        // Import button
        document.getElementById('import-settings-btn').addEventListener('click', () => {
            document.getElementById('import-file-input').click();
        });

        document.getElementById('import-file-input').addEventListener('change', (e) => {
            this.importSettings(e.target.files[0]);
        });

        // Theme change preview
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.previewTheme(e.target.value);
        });

        // Threshold sliders
        ['critical-threshold', 'high-threshold', 'medium-threshold'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateThresholdDisplays();
                this.isDirty = true;
            });
        });

        // Mark as dirty on any change
        document.querySelectorAll('#settings-page input, #settings-page select').forEach(input => {
            input.addEventListener('change', () => {
                this.isDirty = true;
            });
        });
    }

    // ========================================
    // Collect Settings from UI
    // ========================================

    collectSettings() {
        // General
        this.settings.general.theme = document.getElementById('theme-select').value;
        this.settings.general.language = document.getElementById('language-select').value;
        this.settings.general.timezone = document.getElementById('timezone-select').value;
        this.settings.general.autoRefresh = document.getElementById('auto-refresh').checked;
        this.settings.general.refreshInterval = parseInt(document.getElementById('refresh-interval').value);

        // Notifications
        this.settings.notifications.enabled = document.getElementById('notifications-enabled').checked;
        this.settings.notifications.desktop = document.getElementById('desktop-notifications').checked;
        this.settings.notifications.email = document.getElementById('email-notifications').checked;
        this.settings.notifications.sound = document.getElementById('sound-alerts').checked;
        this.settings.notifications.criticalOnly = document.getElementById('critical-only').checked;

        // Alerts
        this.settings.alerts.criticalThreshold = parseInt(document.getElementById('critical-threshold').value);
        this.settings.alerts.highThreshold = parseInt(document.getElementById('high-threshold').value);
        this.settings.alerts.mediumThreshold = parseInt(document.getElementById('medium-threshold').value);
        this.settings.alerts.autoBlock = document.getElementById('auto-block').checked;
        this.settings.alerts.alertRetention = parseInt(document.getElementById('alert-retention').value);

        // Display
        this.settings.display.itemsPerPage = parseInt(document.getElementById('items-per-page').value);
        this.settings.display.showSidebar = document.getElementById('show-sidebar').checked;
        this.settings.display.compactMode = document.getElementById('compact-mode').checked;
        this.settings.display.animations = document.getElementById('animations-enabled').checked;

        // Security
        this.settings.security.sessionTimeout = parseInt(document.getElementById('session-timeout').value);
        this.settings.security.requireAuth = document.getElementById('require-auth').checked;
        this.settings.security.twoFactor = document.getElementById('two-factor').checked;
    }

    // ========================================
    // Apply Settings
    // ========================================

    applySettings() {
        // Apply theme
        this.applyTheme(this.settings.general.theme);

        // Apply display settings
        document.body.classList.toggle('compact-mode', this.settings.display.compactMode);
        document.body.classList.toggle('no-animations', !this.settings.display.animations);

        // Update sidebar visibility
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.display = this.settings.display.showSidebar ? 'flex' : 'none';
        }

        // Apply pagination size
        if (window.dashboardManager) {
            dashboardManager.pageSize = this.settings.display.itemsPerPage;
        }
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }
    }

    previewTheme(theme) {
        this.applyTheme(theme);
    }

    // ========================================
    // Threshold Displays
    // ========================================

    updateThresholdDisplays() {
        const critical = document.getElementById('critical-threshold').value;
        const high = document.getElementById('high-threshold').value;
        const medium = document.getElementById('medium-threshold').value;

        document.getElementById('critical-value').textContent = critical + '%';
        document.getElementById('high-value').textContent = high + '%';
        document.getElementById('medium-value').textContent = medium + '%';
    }

    // ========================================
    // Reset Settings
    // ========================================

    resetSettings() {
        localStorage.removeItem('app_settings');
        this.settings = this.loadSettings();
        this.loadSettingsUI();
        this.applySettings();
        showNotification('Settings reset to default', 'info');
    }

    // ========================================
    // Export/Import Settings
    // ========================================

    exportSettings() {
        const dataStr = JSON.stringify(this.settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `anomaly-detection-settings-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        showNotification('Settings exported successfully', 'success');
    }

    async importSettings(file) {
        if (!file) return;

        try {
            const text = await file.text();
            const importedSettings = JSON.parse(text);
            
            // Validate settings structure
            if (this.validateSettings(importedSettings)) {
                this.settings = { ...this.settings, ...importedSettings };
                this.loadSettingsUI();
                this.saveSettings();
                showNotification('Settings imported successfully', 'success');
            } else {
                showNotification('Invalid settings file', 'error');
            }
        } catch (error) {
            console.error('Error importing settings:', error);
            showNotification('Failed to import settings', 'error');
        }
    }

    validateSettings(settings) {
        // Basic validation - check if key sections exist
        return settings.general && settings.notifications && settings.alerts;
    }

    // ========================================
    // Clear Cache
    // ========================================

    clearCache() {
        if (confirm('This will clear all cached data. Continue?')) {
            localStorage.clear();
            sessionStorage.clear();
            showNotification('Cache cleared successfully', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    }
}

// ========================================
// Initialize Settings Manager
// ========================================

const settingsManager = new SettingsManager();

// Apply settings on load
settingsManager.applySettings();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.settingsManager = settingsManager;
}
