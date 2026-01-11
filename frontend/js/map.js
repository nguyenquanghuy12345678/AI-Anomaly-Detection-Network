/**
 * Geographic Map Manager for visualizing attack origins and network activity
 * Uses Leaflet.js for interactive map display
 */

class GeoMapManager {
    constructor() {
        this.map = null;
        this.markers = [];
        this.heatData = [];
        this.attackLines = [];
        this.updateInterval = null;
        
        // Map configuration
        this.config = {
            center: [20, 0], // Center of the world
            zoom: 2,
            maxZoom: 18,
            minZoom: 2
        };
        
        // Custom icons for different threat levels
        this.icons = {
            high: this.createCustomIcon('#ff4444'),
            medium: this.createCustomIcon('#ffaa00'),
            low: this.createCustomIcon('#44ff44'),
            server: this.createCustomIcon('#4444ff')
        };
    }

    /**
     * Initialize the map
     */
    init(containerId) {
        if (!window.L) {
            console.error('Leaflet library not loaded');
            return;
        }

        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Initialize map
        this.map = L.map(containerId).setView(this.config.center, this.config.zoom);

        // Add tile layer (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            maxZoom: this.config.maxZoom,
            minZoom: this.config.minZoom
        }).addTo(this.map);

        // Add dark mode tile layer option
        this.darkTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            maxZoom: this.config.maxZoom,
            minZoom: this.config.minZoom
        });

        // Load initial data
        this.loadMapData();

        // Start auto-refresh
        this.startAutoRefresh();

        console.log('Geographic map initialized');
    }

    /**
     * Create custom marker icon
     */
    createCustomIcon(color) {
        return L.divIcon({
            className: 'custom-marker',
            html: `<div style="
                width: 20px;
                height: 20px;
                background-color: ${color};
                border: 2px solid white;
                border-radius: 50%;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                animation: pulse 2s infinite;
            "></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
    }

    /**
     * Load map data (attacks, servers, etc.)
     */
    async loadMapData() {
        try {
            // In production, fetch from API
            // const data = await apiService.getGeoData();
            
            // For now, use mock data
            const data = this.generateMockGeoData();
            
            this.renderAttacks(data.attacks);
            this.renderServers(data.servers);
            this.renderAttackLines(data.attacks);
            
        } catch (error) {
            console.error('Error loading map data:', error);
        }
    }

    /**
     * Generate mock geographic data
     */
    generateMockGeoData() {
        const attacks = [];
        const servers = [
            { lat: 37.7749, lng: -122.4194, name: 'San Francisco Server', status: 'healthy' },
            { lat: 51.5074, lng: -0.1278, name: 'London Server', status: 'healthy' },
            { lat: 35.6762, lng: 139.6503, name: 'Tokyo Server', status: 'warning' },
            { lat: -33.8688, lng: 151.2093, name: 'Sydney Server', status: 'healthy' }
        ];

        // Generate random attack origins
        const attackLocations = [
            { lat: 55.7558, lng: 37.6173, country: 'Russia' },
            { lat: 39.9042, lng: 116.4074, country: 'China' },
            { lat: 28.6139, lng: 77.2090, country: 'India' },
            { lat: 52.5200, lng: 13.4050, country: 'Germany' },
            { lat: -23.5505, lng: -46.6333, country: 'Brazil' },
            { lat: 40.7128, lng: -74.0060, country: 'USA' },
            { lat: 1.3521, lng: 103.8198, country: 'Singapore' },
            { lat: 25.2048, lng: 55.2708, country: 'UAE' }
        ];

        attackLocations.forEach((location, index) => {
            const count = Math.floor(Math.random() * 50) + 10;
            const severity = Math.random();
            const level = severity > 0.7 ? 'high' : severity > 0.4 ? 'medium' : 'low';
            
            attacks.push({
                ...location,
                count,
                severity: level,
                types: this.getRandomAttackTypes(),
                target: servers[Math.floor(Math.random() * servers.length)]
            });
        });

        return { attacks, servers };
    }

    /**
     * Get random attack types
     */
    getRandomAttackTypes() {
        const types = ['DDoS', 'Port Scan', 'SQL Injection', 'Brute Force', 'Malware', 'Phishing'];
        const count = Math.floor(Math.random() * 3) + 1;
        return types.sort(() => Math.random() - 0.5).slice(0, count);
    }

    /**
     * Render attack markers on map
     */
    renderAttacks(attacks) {
        // Clear existing markers
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];

        attacks.forEach(attack => {
            const icon = this.icons[attack.severity];
            const marker = L.marker([attack.lat, attack.lng], { icon })
                .bindPopup(this.createAttackPopup(attack))
                .addTo(this.map);

            // Add circle to show attack intensity
            const circle = L.circle([attack.lat, attack.lng], {
                color: this.getSeverityColor(attack.severity),
                fillColor: this.getSeverityColor(attack.severity),
                fillOpacity: 0.2,
                radius: attack.count * 1000 // Scale radius by attack count
            }).addTo(this.map);

            this.markers.push(marker);
            this.markers.push(circle);
        });
    }

    /**
     * Render server markers
     */
    renderServers(servers) {
        servers.forEach(server => {
            const marker = L.marker([server.lat, server.lng], { 
                icon: this.icons.server 
            })
                .bindPopup(this.createServerPopup(server))
                .addTo(this.map);

            this.markers.push(marker);
        });
    }

    /**
     * Render attack lines from origin to target
     */
    renderAttackLines(attacks) {
        // Clear existing lines
        this.attackLines.forEach(line => this.map.removeLayer(line));
        this.attackLines = [];

        attacks.forEach(attack => {
            if (attack.target) {
                const line = L.polyline(
                    [[attack.lat, attack.lng], [attack.target.lat, attack.target.lng]], 
                    {
                        color: this.getSeverityColor(attack.severity),
                        weight: 2,
                        opacity: 0.5,
                        dashArray: '5, 10'
                    }
                ).addTo(this.map);

                this.attackLines.push(line);
            }
        });
    }

    /**
     * Create popup content for attacks
     */
    createAttackPopup(attack) {
        return `
            <div class="map-popup">
                <h3><i class="fas fa-exclamation-triangle"></i> Attack Origin</h3>
                <p><strong>Location:</strong> ${attack.country}</p>
                <p><strong>Severity:</strong> <span class="severity-${attack.severity}">${attack.severity.toUpperCase()}</span></p>
                <p><strong>Attack Count:</strong> ${attack.count}</p>
                <p><strong>Types:</strong> ${attack.types.join(', ')}</p>
                <p><strong>Target:</strong> ${attack.target ? attack.target.name : 'Unknown'}</p>
            </div>
        `;
    }

    /**
     * Create popup content for servers
     */
    createServerPopup(server) {
        return `
            <div class="map-popup">
                <h3><i class="fas fa-server"></i> ${server.name}</h3>
                <p><strong>Status:</strong> <span class="status-${server.status}">${server.status.toUpperCase()}</span></p>
                <p><strong>Coordinates:</strong> ${server.lat.toFixed(4)}, ${server.lng.toFixed(4)}</p>
            </div>
        `;
    }

    /**
     * Get color based on severity
     */
    getSeverityColor(severity) {
        const colors = {
            high: '#ff4444',
            medium: '#ffaa00',
            low: '#44ff44'
        };
        return colors[severity] || '#888888';
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh(interval = 30000) {
        this.stopAutoRefresh();
        this.updateInterval = setInterval(() => {
            this.loadMapData();
        }, interval);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Toggle dark mode
     */
    setDarkMode(enabled) {
        if (enabled) {
            this.map.eachLayer(layer => {
                if (layer instanceof L.TileLayer && !layer.options.className?.includes('dark')) {
                    this.map.removeLayer(layer);
                }
            });
            this.darkTileLayer.addTo(this.map);
        } else {
            this.map.removeLayer(this.darkTileLayer);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                maxZoom: this.config.maxZoom,
                minZoom: this.config.minZoom
            }).addTo(this.map);
        }
    }

    /**
     * Focus on specific location
     */
    focusLocation(lat, lng, zoom = 8) {
        this.map.setView([lat, lng], zoom);
    }

    /**
     * Clear all markers and lines
     */
    clear() {
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.attackLines.forEach(line => this.map.removeLayer(line));
        this.markers = [];
        this.attackLines = [];
    }

    /**
     * Destroy map instance
     */
    destroy() {
        this.stopAutoRefresh();
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GeoMapManager;
}
