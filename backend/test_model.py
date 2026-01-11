"""
Test the trained anomaly detection model
"""
import os
import joblib
import numpy as np
import pandas as pd
import json

def load_model(version='1.0.0'):
    """Load trained model and scaler"""
    model_dir = './models'
    
    model_file = os.path.join(model_dir, f'anomaly_detector_{version}.pkl')
    scaler_file = os.path.join(model_dir, f'scaler_{version}.pkl')
    features_file = os.path.join(model_dir, f'features_{version}.json')
    
    print(f"📂 Loading model version {version}...")
    model = joblib.load(model_file)
    scaler = joblib.load(scaler_file)
    
    with open(features_file, 'r') as f:
        features_data = json.load(f)
        feature_names = features_data['features']
    
    print(f"✅ Model loaded successfully")
    print(f"   Features: {len(feature_names)}")
    
    return model, scaler, feature_names

def create_test_samples():
    """Create test samples for prediction"""
    
    # Normal traffic sample
    normal_sample = {
        'source_port': 45123,
        'dest_port': 443,
        'protocol': 4,  # HTTPS
        'packet_size': 512,
        'packets': 50,
        'bytes': 25600,
        'duration': 2.5,
        'flag_count': 2,
        'syn_flag': 1,
        'ack_flag': 1,
        'rst_flag': 0,
        'connection_rate': 3.0,
        'hour': 14,
        'day_of_week': 2
    }
    
    # DoS attack sample
    dos_sample = {
        'source_port': 12345,
        'dest_port': 80,
        'protocol': 1,  # TCP
        'packet_size': 64,
        'packets': 5000,
        'bytes': 320000,
        'duration': 0.1,
        'flag_count': 10,
        'syn_flag': 1,
        'ack_flag': 0,
        'rst_flag': 1,
        'connection_rate': 150.0,
        'hour': 3,
        'day_of_week': 5
    }
    
    # Port scan sample
    port_scan_sample = {
        'source_port': 54321,
        'dest_port': 8080,
        'protocol': 1,  # TCP
        'packet_size': 64,
        'packets': 2,
        'bytes': 128,
        'duration': 0.01,
        'flag_count': 1,
        'syn_flag': 1,
        'ack_flag': 0,
        'rst_flag': 1,
        'connection_rate': 30.0,
        'hour': 22,
        'day_of_week': 6
    }
    
    # Data exfiltration sample
    exfiltration_sample = {
        'source_port': 49876,
        'dest_port': 443,
        'protocol': 4,  # HTTPS
        'packet_size': 1400,
        'packets': 3000,
        'bytes': 4200000,
        'duration': 120.0,
        'flag_count': 3,
        'syn_flag': 1,
        'ack_flag': 1,
        'rst_flag': 0,
        'connection_rate': 5.0,
        'hour': 2,
        'day_of_week': 0
    }
    
    return {
        'Normal Traffic': normal_sample,
        'DoS Attack': dos_sample,
        'Port Scan': port_scan_sample,
        'Data Exfiltration': exfiltration_sample
    }

def predict_sample(model, scaler, feature_names, sample_data):
    """Predict if sample is anomaly"""
    # Convert to DataFrame
    df = pd.DataFrame([sample_data])
    
    # Ensure column order matches training
    df = df[feature_names]
    
    # Scale features
    X_scaled = scaler.transform(df)
    
    # Predict
    prediction = model.predict(X_scaled)[0]
    anomaly_score = model.score_samples(X_scaled)[0]
    
    # Convert prediction: 1 (normal) -> False, -1 (anomaly) -> True
    is_anomaly = prediction == -1
    
    # Convert anomaly score to confidence (0-100%)
    # Scores closer to -0.5 are more anomalous
    confidence = min(100, max(0, (1 - abs(anomaly_score + 0.25)) * 100))
    
    return is_anomaly, confidence, anomaly_score

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Testing AI/ML Anomaly Detection Model")
    print("=" * 60)
    
    # Load model
    model, scaler, feature_names = load_model()
    
    # Create test samples
    test_samples = create_test_samples()
    
    print("\n🔍 Running predictions on test samples:\n")
    print("-" * 60)
    
    # Test each sample
    for sample_name, sample_data in test_samples.items():
        is_anomaly, confidence, score = predict_sample(
            model, scaler, feature_names, sample_data
        )
        
        # Display results
        status = "🚨 ANOMALY" if is_anomaly else "✅ NORMAL"
        print(f"\n{sample_name}:")
        print(f"   Status: {status}")
        print(f"   Confidence: {confidence:.2f}%")
        print(f"   Anomaly Score: {score:.4f}")
        
        # Show key features
        print(f"   Key Features:")
        print(f"      - Protocol: {sample_data['protocol']}")
        print(f"      - Packets: {sample_data['packets']}")
        print(f"      - Bytes: {sample_data['bytes']}")
        print(f"      - Duration: {sample_data['duration']}s")
        print(f"      - Connection Rate: {sample_data['connection_rate']}/s")
    
    print("\n" + "-" * 60)
    print("\n✅ Model testing complete!")
    print("\n💡 Model is ready to use in the application")
    print("   The ML service will automatically load this model")

if __name__ == '__main__':
    main()
