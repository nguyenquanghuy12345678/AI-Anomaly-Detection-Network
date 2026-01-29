"""
API blueprints registration
"""
from api.anomalies import anomalies_bp
from api.alerts import alerts_bp
from api.traffic import traffic_bp
from api.model import model_bp
from api.system import system_bp
from api.connections import connections_bp
from api.real_network import real_network_bp

def register_blueprints(app):
    """Register all API blueprints"""
    app.register_blueprint(anomalies_bp, url_prefix='/api/anomalies')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(traffic_bp, url_prefix='/api/traffic')
    app.register_blueprint(model_bp, url_prefix='/api/model')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(connections_bp, url_prefix='/api/connections')
    app.register_blueprint(real_network_bp, url_prefix='/api/real-network')
    
    print("✅ API blueprints registered successfully (including Real Network)")

__all__ = ['register_blueprints']
