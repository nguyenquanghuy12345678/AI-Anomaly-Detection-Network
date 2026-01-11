"""
AI/ML Service for anomaly detection
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from config import Config

class MLService:
    """Machine Learning service for anomaly detection"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = Config.MODEL_PATH
        self.model_version = Config.MODEL_VERSION
        self.threshold = Config.PREDICTION_THRESHOLD
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Load or initialize model
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk"""
        model_file = os.path.join(self.model_path, f'anomaly_detector_{self.model_version}.pkl')
        scaler_file = os.path.join(self.model_path, f'scaler_{self.model_version}.pkl')
        features_file = os.path.join(self.model_path, f'features_{self.model_version}.json')
        
        try:
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                
                # Load feature names if available
                if os.path.exists(features_file):
                    import json
                    with open(features_file, 'r') as f:
                        features_data = json.load(f)
                        self.feature_names = features_data.get('features', [])
                
                print(f"✅ Model loaded from {model_file}")
                print(f"   Features: {len(self.feature_names) if self.feature_names else 'legacy mode'}")
            else:
                print("⚠️  No existing model found, initializing new model...")
                self.initialize_model()
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.initialize_model()
    
    def initialize_model(self):
        """Initialize a new Isolation Forest model"""
        self.model = IsolationForest(
            contamination=0.1,
            max_samples=256,
            random_state=42,
            n_estimators=100
        )
        print("✅ New Isolation Forest model initialized")
    
    def save_model(self):
        """Save model to disk"""
        model_file = os.path.join(self.model_path, f'anomaly_detector_{self.model_version}.pkl')
        scaler_file = os.path.join(self.model_path, f'scaler_{self.model_version}.pkl')
        
        try:
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            print(f"✅ Model saved to {model_file}")
        except Exception as e:
            print(f"❌ Error saving model: {e}")
    
    def extract_features(self, data):
        """Extract features from network data"""
        features = []
        
        # Convert data to feature vector
        features.append(data.get('sourcePort', 0))
        features.append(data.get('destinationPort', 0))
        features.append(data.get('bytes', 0))
        features.append(data.get('packets', 0))
        features.append(data.get('duration', 0))
        
        # Protocol encoding (TCP=1, UDP=2, HTTP=3, HTTPS=4, Other=0)
        protocol_map = {'TCP': 1, 'UDP': 2, 'HTTP': 3, 'HTTPS': 4, 'SSH': 5, 'FTP': 6}
        protocol = data.get('protocol', 'OTHER').upper()
        features.append(protocol_map.get(protocol, 0))
        
        # Hour of day (for temporal patterns)
        hour = datetime.utcnow().hour
        features.append(hour)
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, data):
        """Make prediction on new data"""
        try:
            # Extract features
            features = self.extract_features(data)
            
            # Check if model is fitted
            if not hasattr(self.model, 'offset_'):
                # If not fitted, return default prediction
                return {
                    'prediction': 'normal',
                    'confidence': 0.5,
                    'anomaly_score': 0.0,
                    'severity': 'low'
                }
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction (-1 for anomaly, 1 for normal)
            prediction = self.model.predict(features_scaled)[0]
            
            # Get anomaly score
            anomaly_score = self.model.score_samples(features_scaled)[0]
            
            # Calculate confidence (0-1)
            confidence = abs(anomaly_score)
            
            # Determine severity based on score
            if confidence > 0.8:
                severity = 'critical'
            elif confidence > 0.6:
                severity = 'high'
            elif confidence > 0.4:
                severity = 'medium'
            else:
                severity = 'low'
            
            result = {
                'prediction': 'anomaly' if prediction == -1 else 'normal',
                'confidence': float(confidence),
                'anomaly_score': float(anomaly_score),
                'severity': severity if prediction == -1 else 'low'
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return {
                'prediction': 'error',
                'confidence': 0.0,
                'anomaly_score': 0.0,
                'severity': 'low',
                'error': str(e)
            }
    
    def train(self, X_train):
        """Train the model with data"""
        try:
            # Scale the data
            X_scaled = self.scaler.fit_transform(X_train)
            
            # Fit the model
            self.model.fit(X_scaled)
            
            # Save the model
            self.save_model()
            
            print("✅ Model training completed")
            return {'status': 'success'}
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def retrain(self):
        """Retrain model with latest data"""
        from models.anomaly import Anomaly
        from database import db
        
        try:
            # Get recent anomalies for retraining
            anomalies = Anomaly.query.limit(10000).all()
            
            if len(anomalies) < 100:
                return {'status': 'insufficient_data', 'message': 'Not enough data for retraining'}
            
            # Convert to feature matrix
            X_train = []
            for anomaly in anomalies:
                features = self.extract_features({
                    'sourcePort': anomaly.source_port,
                    'destinationPort': anomaly.destination_port,
                    'bytes': anomaly.bytes_transferred or 0,
                    'packets': anomaly.packets or 0,
                    'protocol': anomaly.protocol,
                    'duration': 0
                })
                X_train.append(features[0])
            
            X_train = np.array(X_train)
            
            # Train the model
            result = self.train(X_train)
            
            # Update model metrics
            from models.model_metrics import ModelMetrics
            metrics = ModelMetrics(
                timestamp=datetime.utcnow(),
                model_version=self.model_version,
                status='active',
                last_trained=datetime.utcnow(),
                dataset_size=len(anomalies)
            )
            db.session.add(metrics)
            db.session.commit()
            
            return result
            
        except Exception as e:
            print(f"❌ Retraining error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_feature_importance(self):
        """Get feature importance (for future analysis)"""
        # Isolation Forest doesn't provide feature importance directly
        # This is a placeholder for future implementation
        return {
            'sourcePort': 0.15,
            'destinationPort': 0.15,
            'bytes': 0.25,
            'packets': 0.20,
            'duration': 0.15,
            'protocol': 0.10
        }
