"""
Anomaly database model
"""
from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Anomaly(db.Model):
    """Anomaly detection record"""
    __tablename__ = 'anomalies'
    
    id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    source_ip = db.Column(db.String(45), nullable=False, index=True)
    destination_ip = db.Column(db.String(45), nullable=False)
    source_port = db.Column(db.Integer)
    destination_port = db.Column(db.Integer)
    type = db.Column(db.String(50), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)
    confidence = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    description = db.Column(db.Text)
    protocol = db.Column(db.String(10))
    bytes_transferred = db.Column(db.BigInteger)
    packets = db.Column(db.Integer)
    additional_data = db.Column(JSON)
    blocked_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sourceIp': self.source_ip,
            'destinationIp': self.destination_ip,
            'sourcePort': self.source_port,
            'destinationPort': self.destination_port,
            'type': self.type,
            'severity': self.severity,
            'confidence': self.confidence,
            'status': self.status,
            'description': self.description,
            'protocol': self.protocol,
            'bytes': self.bytes_transferred,
            'packets': self.packets,
            'additionalData': self.additional_data
        }
    
    def __repr__(self):
        return f'<Anomaly {self.id} - {self.type} ({self.severity})>'
