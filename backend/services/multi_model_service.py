"""
Multi-Model ML Service
Service quản lý và sử dụng tất cả các ML models
"""
import os
import joblib
import json
import numpy as np
import pandas as pd
from datetime import datetime
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

class MultiModelService:
    """Service to manage multiple ML models"""
    
    def __init__(self, model_dir='./models', version='1.0.0'):
        self.model_dir = model_dir
        self.version = version
        
        # Models
        self.anomaly_detector = None
        self.anomaly_scaler = None
        
        self.attack_classifier = None
        self.attack_scaler = None
        self.attack_encoder = None
        
        self.severity_predictor = None
        self.severity_scaler = None
        self.severity_encoder = None
        
        self.traffic_forecaster = None
        self.traffic_scaler = None
        
        # Load all models
        self.load_all_models()
    
    def load_all_models(self):
        """Load all available models"""
        print("\n🔄 Loading ML models...")
        
        # 1. Anomaly Detector
        try:
            self.anomaly_detector = joblib.load(
                os.path.join(self.model_dir, f'anomaly_detector_{self.version}.pkl'))
            self.anomaly_scaler = joblib.load(
                os.path.join(self.model_dir, f'scaler_{self.version}.pkl'))
            print("   ✅ Anomaly Detector loaded")
        except:
            print("   ⚠️  Anomaly Detector not found")
        
        # 2. Attack Classifier
        try:
            self.attack_classifier = joblib.load(
                os.path.join(self.model_dir, f'attack_classifier_{self.version}.pkl'))
            self.attack_scaler = joblib.load(
                os.path.join(self.model_dir, f'attack_scaler_{self.version}.pkl'))
            self.attack_encoder = joblib.load(
                os.path.join(self.model_dir, f'attack_encoder_{self.version}.pkl'))
            print("   ✅ Attack Classifier loaded")
        except:
            print("   ⚠️  Attack Classifier not found")
        
        # 3. Severity Predictor
        try:
            self.severity_predictor = joblib.load(
                os.path.join(self.model_dir, f'severity_predictor_{self.version}.pkl'))
            self.severity_scaler = joblib.load(
                os.path.join(self.model_dir, f'severity_scaler_{self.version}.pkl'))
            self.severity_encoder = joblib.load(
                os.path.join(self.model_dir, f'severity_encoder_{self.version}.pkl'))
            print("   ✅ Severity Predictor loaded")
        except:
            print("   ⚠️  Severity Predictor not found")
        
        # 4. Traffic Forecaster
        try:
            self.traffic_forecaster = joblib.load(
                os.path.join(self.model_dir, f'traffic_forecaster_{self.version}.pkl'))
            self.traffic_scaler = joblib.load(
                os.path.join(self.model_dir, f'traffic_scaler_{self.version}.pkl'))
            print("   ✅ Traffic Forecaster loaded")
        except:
            print("   ⚠️  Traffic Forecaster not found")
    
    def detect_anomaly(self, traffic_data):
        """Detect if traffic is anomalous"""
        if not self.anomaly_detector:
            return {'error': 'Anomaly detector not loaded'}
        
        try:
            # Prepare features
            features = [
                traffic_data.get('source_port', 0),
                traffic_data.get('dest_port', 0),
                traffic_data.get('protocol', 1),
                traffic_data.get('packet_size', 500),
                traffic_data.get('packets', 50),
                traffic_data.get('bytes', 25000),
                traffic_data.get('duration', 1.0),
                traffic_data.get('flag_count', 2),
                traffic_data.get('syn_flag', 1),
                traffic_data.get('ack_flag', 1),
                traffic_data.get('rst_flag', 0),
                traffic_data.get('connection_rate', 5.0),
                datetime.now().hour,
                datetime.now().weekday()
            ]
            
            X = np.array(features).reshape(1, -1)
            X_scaled = self.anomaly_scaler.transform(X)
            
            prediction = self.anomaly_detector.predict(X_scaled)[0]
            score = self.anomaly_detector.score_samples(X_scaled)[0]
            
            is_anomaly = prediction == -1
            confidence = min(100, max(0, abs(score) * 100))
            
            return {
                'is_anomaly': bool(is_anomaly),
                'confidence': float(confidence),
                'anomaly_score': float(score)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def classify_attack(self, traffic_data):
        """Classify attack type"""
        if not self.attack_classifier:
            return {'error': 'Attack classifier not loaded'}
        
        try:
            features = [
                traffic_data.get('source_port', 0),
                traffic_data.get('dest_port', 0),
                traffic_data.get('protocol', 1),
                traffic_data.get('packet_size', 500),
                traffic_data.get('packets', 50),
                traffic_data.get('bytes', 25000),
                traffic_data.get('duration', 1.0),
                traffic_data.get('flag_count', 2),
                traffic_data.get('syn_flag', 1),
                traffic_data.get('ack_flag', 1),
                traffic_data.get('rst_flag', 0),
                traffic_data.get('connection_rate', 5.0),
                datetime.now().hour,
                datetime.now().weekday()
            ]
            
            X = np.array(features).reshape(1, -1)
            X_scaled = self.attack_scaler.transform(X)
            
            prediction = self.attack_classifier.predict(X_scaled)[0]
            probabilities = self.attack_classifier.predict_proba(X_scaled)[0]
            
            attack_type = self.attack_encoder.inverse_transform([prediction])[0]
            confidence = float(max(probabilities) * 100)
            
            # Get all probabilities
            all_types = {}
            for i, prob in enumerate(probabilities):
                type_name = self.attack_encoder.inverse_transform([i])[0]
                all_types[type_name] = float(prob * 100)
            
            return {
                'attack_type': attack_type,
                'confidence': confidence,
                'probabilities': all_types
            }
        except Exception as e:
            return {'error': str(e)}
    
    def predict_severity(self, alert_data):
        """Predict alert severity level"""
        if not self.severity_predictor:
            return {'error': 'Severity predictor not loaded'}
        
        try:
            features = [
                alert_data.get('connection_rate', 10),
                alert_data.get('failed_attempts', 5),
                alert_data.get('data_volume_mb', 10),
                alert_data.get('unique_sources', 5),
                alert_data.get('unique_destinations', 5),
                alert_data.get('unusual_ports', 2),
                alert_data.get('time_window_minutes', 10),
                alert_data.get('is_encrypted', 0),
                alert_data.get('matches_known_signature', 0),
                alert_data.get('geographic_anomaly', 0),
                alert_data.get('affected_systems', 1),
                alert_data.get('business_hours', 1)
            ]
            
            X = np.array(features).reshape(1, -1)
            X_scaled = self.severity_scaler.transform(X)
            
            prediction = self.severity_predictor.predict(X_scaled)[0]
            probabilities = self.severity_predictor.predict_proba(X_scaled)[0]
            
            severity = self.severity_encoder.inverse_transform([prediction])[0]
            confidence = float(max(probabilities) * 100)
            
            return {
                'severity': severity,
                'confidence': confidence
            }
        except Exception as e:
            return {'error': str(e)}
    
    def forecast_traffic(self, current_data):
        """Forecast next interval's traffic"""
        if not self.traffic_forecaster:
            return {'error': 'Traffic forecaster not loaded'}
        
        try:
            now = datetime.now()
            features = [
                now.hour,
                now.weekday(),
                now.day,
                int(now.weekday() >= 5),
                int(8 <= now.hour <= 18),
                current_data.get('traffic_mbps', 100),
                current_data.get('connections_count', 500),
                current_data.get('packets_per_sec', 5000),
                current_data.get('avg_packet_size', 600),
                current_data.get('tcp_ratio', 0.7),
                current_data.get('udp_ratio', 0.2),
                current_data.get('http_ratio', 0.4),
                current_data.get('traffic_lag_1', 100),
                current_data.get('traffic_lag_2', 100),
                current_data.get('traffic_lag_3', 100)
            ]
            
            X = np.array(features).reshape(1, -1)
            X_scaled = self.traffic_scaler.transform(X)
            
            prediction = self.traffic_forecaster.predict(X_scaled)[0]
            
            return {
                'predicted_traffic_mbps': float(prediction),
                'current_traffic_mbps': current_data.get('traffic_mbps', 100),
                'change_percent': float((prediction - current_data.get('traffic_mbps', 100)) / current_data.get('traffic_mbps', 100) * 100)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_complete(self, traffic_data):
        """Complete analysis using all models"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        # 1. Detect anomaly
        anomaly_result = self.detect_anomaly(traffic_data)
        results['analysis']['anomaly_detection'] = anomaly_result
        
        # 2. If anomaly, classify attack type
        if anomaly_result.get('is_anomaly'):
            attack_result = self.classify_attack(traffic_data)
            results['analysis']['attack_classification'] = attack_result
            
            # 3. Predict severity
            severity_data = {
                'connection_rate': traffic_data.get('connection_rate', 10),
                'failed_attempts': traffic_data.get('failed_attempts', 5),
                'data_volume_mb': traffic_data.get('bytes', 25000) / 1024 / 1024,
                'unique_sources': traffic_data.get('unique_sources', 1),
                'unique_destinations': traffic_data.get('unique_destinations', 1),
                'unusual_ports': traffic_data.get('unusual_ports', 0),
                'time_window_minutes': traffic_data.get('duration', 1.0) / 60,
                'is_encrypted': traffic_data.get('is_encrypted', 0),
                'matches_known_signature': 1 if attack_result.get('confidence', 0) > 80 else 0,
                'geographic_anomaly': traffic_data.get('geographic_anomaly', 0),
                'affected_systems': traffic_data.get('affected_systems', 1),
                'business_hours': int(8 <= datetime.now().hour <= 18)
            }
            
            severity_result = self.predict_severity(severity_data)
            results['analysis']['severity_prediction'] = severity_result
        
        # 4. Forecast traffic
        forecast_data = {
            'traffic_mbps': traffic_data.get('bytes', 25000) / 1024 / 1024 / traffic_data.get('duration', 1.0) * 8,
            'connections_count': 500,
            'packets_per_sec': traffic_data.get('packets', 50) / traffic_data.get('duration', 1.0),
            'avg_packet_size': traffic_data.get('packet_size', 500),
            'tcp_ratio': 0.7,
            'udp_ratio': 0.2,
            'http_ratio': 0.4,
            'traffic_lag_1': 100,
            'traffic_lag_2': 100,
            'traffic_lag_3': 100
        }
        
        forecast_result = self.forecast_traffic(forecast_data)
        results['analysis']['traffic_forecast'] = forecast_result
        
        return results
    
    def get_models_status(self):
        """Get status of all models"""
        return {
            'anomaly_detector': self.anomaly_detector is not None,
            'attack_classifier': self.attack_classifier is not None,
            'severity_predictor': self.severity_predictor is not None,
            'traffic_forecaster': self.traffic_forecaster is not None,
            'version': self.version
        }

# Test function
def test_service():
    """Test multi-model service"""
    print("=" * 70)
    print("🧪 Testing Multi-Model ML Service")
    print("=" * 70)
    
    service = MultiModelService()
    
    print("\n📊 Models Status:")
    status = service.get_models_status()
    for model, loaded in status.items():
        if model != 'version':
            icon = "✅" if loaded else "❌"
            print(f"   {icon} {model.replace('_', ' ').title()}")
    
    # Test with DoS attack sample
    print("\n🔍 Testing with DoS Attack Sample...")
    dos_traffic = {
        'source_port': 12345,
        'dest_port': 80,
        'protocol': 1,
        'packet_size': 64,
        'packets': 5000,
        'bytes': 320000,
        'duration': 0.1,
        'flag_count': 10,
        'syn_flag': 1,
        'ack_flag': 0,
        'rst_flag': 1,
        'connection_rate': 150.0
    }
    
    results = service.analyze_complete(dos_traffic)
    
    print("\n📋 Analysis Results:")
    if 'anomaly_detection' in results['analysis']:
        ad = results['analysis']['anomaly_detection']
        print(f"\n   1. Anomaly Detection:")
        print(f"      Is Anomaly: {ad.get('is_anomaly')}")
        print(f"      Confidence: {ad.get('confidence', 0):.2f}%")
    
    if 'attack_classification' in results['analysis']:
        ac = results['analysis']['attack_classification']
        print(f"\n   2. Attack Classification:")
        print(f"      Type: {ac.get('attack_type', 'unknown')}")
        print(f"      Confidence: {ac.get('confidence', 0):.2f}%")
    
    if 'severity_prediction' in results['analysis']:
        sp = results['analysis']['severity_prediction']
        print(f"\n   3. Severity Prediction:")
        print(f"      Severity: {sp.get('severity', 'unknown').upper()}")
        print(f"      Confidence: {sp.get('confidence', 0):.2f}%")
    
    if 'traffic_forecast' in results['analysis']:
        tf = results['analysis']['traffic_forecast']
        print(f"\n   4. Traffic Forecast:")
        print(f"      Predicted: {tf.get('predicted_traffic_mbps', 0):.2f} Mbps")
        print(f"      Change: {tf.get('change_percent', 0):.2f}%")
    
    print("\n" + "=" * 70)
    print("✅ Multi-Model Service Test Complete!")
    print("=" * 70)

if __name__ == '__main__':
    test_service()
