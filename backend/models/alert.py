"""
Alert database model
"""
from database import db
from datetime import datetime

class Alert(db.Model):
    """Alert notification record"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='unread', index=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    source_ip = db.Column(db.String(45))
    affected_systems = db.Column(db.Integer, default=1)
    requires_action = db.Column(db.Boolean, default=False)
    anomaly_id = db.Column(db.String(36), db.ForeignKey('anomalies.id'))
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    anomaly = db.relationship('Anomaly', backref='alerts', foreign_keys=[anomaly_id])
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'severity': self.severity,
            'status': self.status,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'sourceIp': self.source_ip,
            'affectedSystems': self.affected_systems,
            'requiresAction': self.requires_action,
            'anomalyId': self.anomaly_id
        }
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.title} ({self.severity})>'
