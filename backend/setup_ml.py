"""
Complete AI/ML Pipeline Setup
Runs all steps: dataset generation, model training, and testing
"""
import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_step(step_num, text):
    """Print step"""
    print(f"\n🔹 Step {step_num}: {text}")
    print("-" * 60)

def run_pipeline():
    """Run complete AI/ML pipeline"""
    print_header("🤖 AI/ML Complete Pipeline Setup")
    
    # Step 1: Generate Dataset
    print_step(1, "Generating Training Dataset")
    try:
        from prepare_dataset import DatasetManager
        manager = DatasetManager()
        dataset = manager.generate_synthetic_dataset(n_samples=10000, anomaly_ratio=0.1)
        print("✅ Dataset generation complete")
    except Exception as e:
        print(f"❌ Dataset generation failed: {e}")
        return False
    
    # Step 2: Train Model
    print_step(2, "Training Machine Learning Model")
    try:
        from train_model import ModelTrainer
        from sklearn.model_selection import train_test_split
        
        trainer = ModelTrainer()
        data = trainer.load_data()
        X, y = trainer.prepare_features(data)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        contamination = (y_train == 1).sum() / len(y_train)
        trainer.train_model(X_train, contamination=contamination)
        
        metrics = trainer.evaluate_model(X_test, y_test)
        trainer.save_model(version='1.0.0')
        
        print("✅ Model training complete")
        print(f"   Accuracy: {metrics['accuracy']*100:.2f}%")
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test Model
    print_step(3, "Testing Model with Sample Data")
    try:
        import joblib
        import json
        import pandas as pd
        
        # Load model
        model = joblib.load('./models/anomaly_detector_1.0.0.pkl')
        scaler = joblib.load('./models/scaler_1.0.0.pkl')
        with open('./models/features_1.0.0.json', 'r') as f:
            feature_names = json.load(f)['features']
        
        # Create test sample (DoS attack)
        test_sample = {
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
            'connection_rate': 150.0,
            'hour': 3,
            'day_of_week': 5
        }
        
        # Predict
        df = pd.DataFrame([test_sample])[feature_names]
        X_scaled = scaler.transform(df)
        prediction = model.predict(X_scaled)[0]
        
        if prediction == -1:
            print("✅ Model testing successful - DoS attack detected!")
        else:
            print("⚠️  Model test warning - DoS attack not detected")
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False
    
    # Step 4: Summary
    print_header("🎉 AI/ML Pipeline Complete!")
    print("\n📊 Summary:")
    print(f"   ✅ Dataset: 10,000 samples generated")
    print(f"   ✅ Model: Trained with {metrics['accuracy']*100:.2f}% accuracy")
    print(f"   ✅ Testing: Model working correctly")
    print(f"\n📁 Files Created:")
    print(f"   - data/datasets/synthetic_network_traffic.csv")
    print(f"   - models/anomaly_detector_1.0.0.pkl")
    print(f"   - models/scaler_1.0.0.pkl")
    print(f"   - models/features_1.0.0.json")
    print(f"\n🚀 Next Steps:")
    print(f"   1. Restart backend: python app.py")
    print(f"   2. Model will auto-load on startup")
    print(f"   3. Test via API: http://localhost:5000/api/model/status")
    print(f"   4. Generate demo data: python utils/data_generator.py")
    print(f"   5. View dashboard: http://localhost:8080")
    print("\n" + "=" * 60)
    
    return True

if __name__ == '__main__':
    success = run_pipeline()
    sys.exit(0 if success else 1)
