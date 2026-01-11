"""
Model Metrics database model
"""
from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class ModelMetrics(db.Model):
    """AI/ML model performance metrics"""
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    model_version = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    detection_rate = db.Column(db.Float)
    false_positive_rate = db.Column(db.Float)
    true_positives = db.Column(db.Integer, default=0)
    false_positives = db.Column(db.Integer, default=0)
    true_negatives = db.Column(db.Integer, default=0)
    false_negatives = db.Column(db.Integer, default=0)
    predictions_made = db.Column(db.Integer, default=0)
    last_trained = db.Column(db.DateTime)
    training_duration = db.Column(db.Integer)  # seconds
    dataset_size = db.Column(db.Integer)
    additional_metrics = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'version': self.model_version,
            'status': self.status,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1Score': self.f1_score,
            'detectionRate': self.detection_rate,
            'falsePositiveRate': self.false_positive_rate,
            'lastTrained': self.last_trained.isoformat() if self.last_trained else None,
            'predictionsMade': self.predictions_made,
            'additionalMetrics': self.additional_metrics
        }
    
    def __repr__(self):
        return f'<ModelMetrics {self.model_version} - Accuracy: {self.accuracy}>'
