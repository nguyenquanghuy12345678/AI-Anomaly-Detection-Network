"""
Model API endpoints
"""
from flask import Blueprint, request, jsonify
from models.model_metrics import ModelMetrics
from services.ml_service import MLService
from database import db
from datetime import datetime

model_bp = Blueprint('model', __name__)

# Initialize ML service
ml_service = MLService()

@model_bp.route('/status', methods=['GET'])
def get_model_status():
    """Get AI model status"""
    # Get latest model metrics
    latest_metrics = ModelMetrics.query.order_by(ModelMetrics.timestamp.desc()).first()
    
    if not latest_metrics:
        return jsonify({
            'status': 'offline',
            'accuracy': 0,
            'lastTrained': None,
            'version': '1.0.0',
            'detectionRate': 0,
            'falsePositiveRate': 0
        }), 200
    
    return jsonify({
        'status': latest_metrics.status,
        'accuracy': round(latest_metrics.accuracy * 100, 2) if latest_metrics.accuracy else 0,
        'lastTrained': latest_metrics.last_trained.isoformat() if latest_metrics.last_trained else None,
        'version': latest_metrics.model_version,
        'detectionRate': round(latest_metrics.detection_rate * 100, 2) if latest_metrics.detection_rate else 0,
        'falsePositiveRate': round(latest_metrics.false_positive_rate * 100, 2) if latest_metrics.false_positive_rate else 0
    }), 200

@model_bp.route('/metrics', methods=['GET'])
def get_model_metrics():
    """Get model performance metrics"""
    latest_metrics = ModelMetrics.query.order_by(ModelMetrics.timestamp.desc()).first()
    
    if not latest_metrics:
        return jsonify({
            'accuracy': 0,
            'precision': 0,
            'recall': 0,
            'f1Score': 0,
            'detectionRate': 0,
            'falsePositiveRate': 0,
            'predictionsMade': 0
        }), 200
    
    return jsonify(latest_metrics.to_dict()), 200

@model_bp.route('/predict', methods=['POST'])
def predict():
    """Make predictions on new data"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Use ML service to make prediction
        prediction = ml_service.predict(data)
        
        return jsonify({
            'prediction': prediction['prediction'],
            'confidence': prediction['confidence'],
            'anomalyScore': prediction['anomaly_score'],
            'severity': prediction['severity'],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500

@model_bp.route('/retrain', methods=['POST'])
def retrain_model():
    """Trigger model retraining"""
    try:
        result = ml_service.retrain()
        
        return jsonify({
            'message': 'Model retraining initiated',
            'status': result['status'],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Retraining failed',
            'message': str(e)
        }), 500
