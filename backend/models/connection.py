"""
Connection database model
"""
from database import db
from datetime import datetime

class Connection(db.Model):
    """Active network connection record"""
    __tablename__ = 'connections'
    
    id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    source_ip = db.Column(db.String(45), nullable=False, index=True)
    source_port = db.Column(db.Integer, nullable=False)
    dest_ip = db.Column(db.String(45), nullable=False)
    dest_port = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    bytes_transferred = db.Column(db.BigInteger, default=0)
    packets = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer, default=0)  # seconds
    is_active = db.Column(db.Boolean, default=True, index=True)
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sourceIp': self.source_ip,
            'sourcePort': self.source_port,
            'destIp': self.dest_ip,
            'destPort': self.dest_port,
            'protocol': self.protocol,
            'state': self.state,
            'bytes': self.bytes_transferred,
            'packets': self.packets,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<Connection {self.source_ip}:{self.source_port} -> {self.dest_ip}:{self.dest_port}>'
