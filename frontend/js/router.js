// ========================================
// SPA Router for Multi-Page Navigation
// ========================================

class Router {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
        this.beforeHooks = [];
        this.afterHooks = [];
        
        // Initialize router
        this.init();
    }

    // ========================================
    // Initialize Router
    // ========================================

    init() {
        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());

        // Register default routes
        this.registerDefaultRoutes();
    }

    // ========================================
    // Route Registration
    // ========================================

    registerDefaultRoutes() {
        this.register('', {
            name: 'dashboard',
            load: () => this.loadDashboard(),
            title: 'Dashboard'
        });

        this.register('dashboard', {
            name: 'dashboard',
            load: () => this.loadDashboard(),
            title: 'Dashboard'
        });

        this.register('monitoring', {
            name: 'monitoring',
            load: () => this.loadMonitoring(),
            title: 'Monitoring'
        });

        this.register('alerts', {
            name: 'alerts',
            load: () => this.loadAlerts(),
            title: 'Alerts'
        });

        this.register('analytics', {
            name: 'analytics',
            load: () => this.loadAnalytics(),
            title: 'Analytics'
        });

        this.register('map', {
            name: 'map',
            load: () => this.loadMap(),
            title: 'Geographic Map'
        });

        this.register('settings', {
            name: 'settings',
            load: () => this.loadSettings(),
            title: 'Settings'
        });
    }

    register(path, config) {
        this.routes.set(path, config);
    }

    // ========================================
    // Route Handling
    // ========================================

    handleRoute() {
        const hash = window.location.hash.slice(1) || '';
        const route = this.routes.get(hash);

        if (!route) {
            console.warn(`Route not found: ${hash}`);
            this.navigate('dashboard');
            return;
        }

        // Run before hooks
        for (const hook of this.beforeHooks) {
            if (hook(hash, this.currentRoute) === false) {
                return; // Cancel navigation
            }
        }

        // Show loading state
        if (typeof showLoading === 'function') {
            showLoading();
        }

        // Update document title
        document.title = `${route.title} - AI Network Anomaly Detection`;

        // Update active nav link
        this.updateActiveNav(hash);

        // Load route content with error handling
        try {
            route.load();
        } catch (error) {
            console.error('Error loading route:', error);
            if (typeof showNotification === 'function') {
                showNotification('Error loading page. Please try again.', 'error');
            }
        } finally {
            // Hide loading state
            if (typeof hideLoading === 'function') {
                setTimeout(hideLoading, 300);
            }
        }

        // Store current route
        this.currentRoute = hash;

        // Run after hooks
        for (const hook of this.afterHooks) {
            hook(hash);
        }
    }

    updateActiveNav(hash) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === `#${hash}` || (hash === '' && href === '#dashboard')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // ========================================
    // Navigation Methods
    // ========================================

    navigate(path) {
        window.location.hash = path;
    }

    back() {
        window.history.back();
    }

    // ========================================
    // Hooks
    // ========================================

    beforeEach(callback) {
        this.beforeHooks.push(callback);
    }

    afterEach(callback) {
        this.afterHooks.push(callback);
    }

    // ========================================
    // Page Loading Functions
    // ========================================

    async loadDashboard() {
        const mainContent = document.querySelector('.main-content');
        if (!mainContent) return;

        // Show dashboard content, hide others
        const dashboard = document.querySelector('.dashboard');
        const sidebar = document.querySelector('.sidebar');
        
        if (dashboard) dashboard.style.display = 'flex';
        if (sidebar) sidebar.style.display = 'flex';
        
        // Hide other page containers
        this.hideOtherPages(['monitoring-page', 'alerts-page', 'analytics-page', 'settings-page']);

        // Reinitialize dashboard if needed
        if (window.dashboardManager) {
            await dashboardManager.updateMetrics();
        }
    }

    async loadMonitoring() {
        await this.loadPageContent('monitoring');
    }

    async loadAlerts() {
        await this.loadPageContent('alerts');
    }

    async loadAnalytics() {
        await this.loadPageContent('analytics');
    }

    async loadMap() {
        await this.loadPageContent('map');
    }

    async loadSettings() {
        await this.loadPageContent('settings');
    }

    async loadPageContent(pageName) {
        const mainContent = document.querySelector('.main-content');
        if (!mainContent) return;

        // Hide dashboard and sidebar
        const dashboard = document.querySelector('.dashboard');
        const sidebar = document.querySelector('.sidebar');
        if (dashboard) dashboard.style.display = 'none';
        if (sidebar) sidebar.style.display = 'none';

        // Check if page container exists
        let pageContainer = document.getElementById(`${pageName}-page`);
        
        if (!pageContainer) {
            // Create page container if it doesn't exist
            pageContainer = document.createElement('div');
            pageContainer.id = `${pageName}-page`;
            pageContainer.className = 'page-container';
            mainContent.appendChild(pageContainer);

            // Load page content
            await this.fetchPageContent(pageName, pageContainer);
        } else {
            pageContainer.style.display = 'block';
        }

        // Hide other pages
        const otherPages = ['monitoring-page', 'alerts-page', 'analytics-page', 'map-page', 'settings-page']
            .filter(p => p !== `${pageName}-page`);
        this.hideOtherPages(otherPages);

        // Initialize page-specific functionality
        this.initializePage(pageName);
    }

    async fetchPageContent(pageName, container) {
        try {
            showLoading();
            
            // Try to fetch from pages directory
            const response = await fetch(`pages/${pageName}.html`);
            
            if (response.ok) {
                const html = await response.text();
                container.innerHTML = html;
            } else {
                // If file doesn't exist, load default template
                container.innerHTML = this.getDefaultTemplate(pageName);
            }
            
            hideLoading();
        } catch (error) {
            console.error(`Error loading ${pageName} page:`, error);
            container.innerHTML = this.getDefaultTemplate(pageName);
            hideLoading();
        }
    }

    hideOtherPages(pageIds) {
        pageIds.forEach(id => {
            const page = document.getElementById(id);
            if (page) page.style.display = 'none';
        });
    }

    initializePage(pageName) {
        // Initialize page-specific managers
        switch(pageName) {
            case 'monitoring':
                if (window.monitoringManager) {
                    monitoringManager.initialize();
                }
                break;
            case 'alerts':
                if (window.alertsManager) {
                    alertsManager.initialize();
                }
                break;
            case 'analytics':
                if (window.analyticsManager) {
                    analyticsManager.initialize();
                }
                break;
            case 'map':
                if (window.geoMapManager) {
                    geoMapManager.init('geoMap');
                }
                break;
            case 'settings':
                if (window.settingsManager) {
                    settingsManager.initialize();
                }
                break;
        }
    }

    getDefaultTemplate(pageName) {
        const templates = {
            monitoring: `
                <div class="page-header">
                    <h2><i class="fas fa-eye"></i> Network Monitoring</h2>
                    <p>Real-time network traffic and connection monitoring</p>
                </div>
                <div class="page-content">
                    <div class="alert info">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <strong>Coming Soon!</strong><br>
                            Real-time network monitoring features are under development.
                        </div>
                    </div>
                </div>
            `,
            alerts: `
                <div class="page-header">
                    <h2><i class="fas fa-bell"></i> Alerts & Notifications</h2>
                    <p>Manage security alerts and notifications</p>
                </div>
                <div class="page-content">
                    <div class="alert info">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <strong>Coming Soon!</strong><br>
                            Alert management features are under development.
                        </div>
                    </div>
                </div>
            `,
            analytics: `
                <div class="page-header">
                    <h2><i class="fas fa-chart-line"></i> Analytics & Reports</h2>
                    <p>Advanced analytics and historical reports</p>
                </div>
                <div class="page-content">
                    <div class="alert info">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <strong>Coming Soon!</strong><br>
                            Analytics and reporting features are under development.
                        </div>
                    </div>
                </div>
            `,
            settings: `
                <div class="page-header">
                    <h2><i class="fas fa-cog"></i> Settings</h2>
                    <p>Configure system preferences and options</p>
                </div>
                <div class="page-content">
                    <div class="alert info">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <strong>Coming Soon!</strong><br>
                            Settings page is under development.
                        </div>
                    </div>
                </div>
            `
        };

        return templates[pageName] || `
            <div class="page-header">
                <h2>${pageName.charAt(0).toUpperCase() + pageName.slice(1)}</h2>
            </div>
            <div class="page-content">
                <p>Page content loading...</p>
            </div>
        `;
    }
}

// ========================================
// Initialize Router
// ========================================

const router = new Router();

// Add navigation hooks
router.beforeEach((to, from) => {
    console.log(`Navigating from ${from || 'none'} to ${to}`);
    return true; // Allow navigation
});

router.afterEach((to) => {
    console.log(`Navigated to ${to}`);
    // Scroll to top on route change
    window.scrollTo(0, 0);
});

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.router = router;
}
