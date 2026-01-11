"""
Network Traffic database model
"""
from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class NetworkTraffic(db.Model):
    """Network traffic metrics record"""
    __tablename__ = 'network_traffic'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    incoming_mbps = db.Column(db.Float, nullable=False)
    outgoing_mbps = db.Column(db.Float, nullable=False)
    total_mbps = db.Column(db.Float, nullable=False)
    tcp_traffic = db.Column(db.Float, default=0)
    udp_traffic = db.Column(db.Float, default=0)
    http_traffic = db.Column(db.Float, default=0)
    https_traffic = db.Column(db.Float, default=0)
    ssh_traffic = db.Column(db.Float, default=0)
    ftp_traffic = db.Column(db.Float, default=0)
    other_traffic = db.Column(db.Float, default=0)
    active_connections = db.Column(db.Integer, default=0)
    anomaly_count = db.Column(db.Integer, default=0)
    blocked_threats = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float)
    protocols = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'incoming': self.incoming_mbps,
            'outgoing': self.outgoing_mbps,
            'total': self.total_mbps,
            'protocols': {
                'tcp': self.tcp_traffic,
                'udp': self.udp_traffic,
                'http': self.http_traffic,
                'https': self.https_traffic,
                'ssh': self.ssh_traffic,
                'ftp': self.ftp_traffic,
                'other': self.other_traffic
            } if not self.protocols else self.protocols,
            'activeConnections': self.active_connections,
            'anomalyCount': self.anomaly_count,
            'blockedThreats': self.blocked_threats,
            'avgResponseTime': self.avg_response_time
        }
    
    def __repr__(self):
        return f'<NetworkTraffic {self.timestamp} - {self.total_mbps} Mbps>'
