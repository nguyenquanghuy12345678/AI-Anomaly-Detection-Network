"""
Complete ML Pipeline - Train All Models
Huấn luyện tất cả các models cùng lúc
"""
import sys
import os

def print_header(text):
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)

def print_step(num, text):
    print(f"\n{'─' * 70}")
    print(f"  STEP {num}: {text}")
    print(f"{'─' * 70}")

def run_all_training():
    """Train all ML models in sequence"""
    
    print_header("🤖 COMPLETE ML TRAINING PIPELINE")
    print("\nThis will train all models:")
    print("  1. ✅ Anomaly Detector (Isolation Forest)")
    print("  2. 🎯 Attack Classifier (Random Forest)")
    print("  3. ⚠️  Severity Predictor (Gradient Boosting)")
    print("  4. 📈 Traffic Forecaster (Gradient Boosting)")
    
    results = {}
    
    # Model 1: Anomaly Detector
    print_step(1, "Training Anomaly Detection Model")
    try:
        from prepare_dataset import DatasetManager
        from train_model import ModelTrainer
        from sklearn.model_selection import train_test_split
        
        manager = DatasetManager()
        dataset = manager.generate_synthetic_dataset(n_samples=10000, anomaly_ratio=0.1)
        
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
        
        results['anomaly_detector'] = {
            'status': 'success',
            'accuracy': metrics['accuracy']
        }
        print(f"✅ Anomaly Detector: {metrics['accuracy']*100:.2f}% accuracy")
        
    except Exception as e:
        print(f"❌ Anomaly Detector failed: {e}")
        results['anomaly_detector'] = {'status': 'failed', 'error': str(e)}
    
    # Model 2: Attack Classifier
    print_step(2, "Training Attack Classification Model")
    try:
        from train_attack_classifier import AttackClassifier
        
        classifier = AttackClassifier()
        data = classifier.generate_attack_dataset(n_samples=5000)
        metrics = classifier.train_model(data)
        classifier.save_model(version='1.0.0')
        
        results['attack_classifier'] = {
            'status': 'success',
            'accuracy': metrics['accuracy']
        }
        print(f"✅ Attack Classifier: {metrics['accuracy']*100:.2f}% accuracy")
        
    except Exception as e:
        print(f"❌ Attack Classifier failed: {e}")
        results['attack_classifier'] = {'status': 'failed', 'error': str(e)}
    
    # Model 3: Severity Predictor
    print_step(3, "Training Severity Prediction Model")
    try:
        from train_severity_predictor import SeverityPredictor
        
        predictor = SeverityPredictor()
        data = predictor.generate_severity_dataset(n_samples=3000)
        metrics = predictor.train_model(data)
        predictor.save_model(version='1.0.0')
        
        results['severity_predictor'] = {
            'status': 'success',
            'accuracy': metrics['accuracy']
        }
        print(f"✅ Severity Predictor: {metrics['accuracy']*100:.2f}% accuracy")
        
    except Exception as e:
        print(f"❌ Severity Predictor failed: {e}")
        results['severity_predictor'] = {'status': 'failed', 'error': str(e)}
    
    # Model 4: Traffic Forecaster
    print_step(4, "Training Traffic Forecasting Model")
    try:
        from train_traffic_forecaster import TrafficForecaster
        
        forecaster = TrafficForecaster()
        data = forecaster.generate_timeseries_dataset(n_days=30, samples_per_day=96)
        metrics = forecaster.train_model(data)
        forecaster.save_model(version='1.0.0')
        
        results['traffic_forecaster'] = {
            'status': 'success',
            'r2_score': metrics['r2_score']
        }
        print(f"✅ Traffic Forecaster: {metrics['r2_score']*100:.2f}% R² score")
        
    except Exception as e:
        print(f"❌ Traffic Forecaster failed: {e}")
        results['traffic_forecaster'] = {'status': 'failed', 'error': str(e)}
    
    # Summary
    print_header("🎉 TRAINING COMPLETE - SUMMARY")
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    print(f"\n📊 Overall Results: {success_count}/{total_count} models trained successfully\n")
    
    for model_name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        model_display = model_name.replace('_', ' ').title()
        
        print(f"{status_icon} {model_display:30s}", end='')
        
        if result['status'] == 'success':
            if 'accuracy' in result:
                print(f"Accuracy: {result['accuracy']*100:.2f}%")
            elif 'r2_score' in result:
                print(f"R² Score: {result['r2_score']*100:.2f}%")
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")
    
    # List generated files
    print(f"\n📁 Generated Files:")
    print(f"\n   Datasets:")
    datasets = [
        'synthetic_network_traffic.csv',
        'attack_classification.csv',
        'severity_prediction.csv',
        'traffic_forecasting.csv'
    ]
    for ds in datasets:
        path = f'data/datasets/{ds}'
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            print(f"      ✅ {ds:40s} ({size:.1f} KB)")
    
    print(f"\n   Models:")
    models = [
        'anomaly_detector_1.0.0.pkl',
        'attack_classifier_1.0.0.pkl',
        'severity_predictor_1.0.0.pkl',
        'traffic_forecaster_1.0.0.pkl'
    ]
    for model in models:
        path = f'models/{model}'
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            print(f"      ✅ {model:40s} ({size:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("\n🚀 Next Steps:")
    print("   1. Restart backend: python app.py")
    print("   2. Models will auto-load on startup")
    print("   3. Test via API endpoints")
    print("   4. Generate demo data: python utils/data_generator.py")
    print("   5. View dashboard: http://localhost:8080")
    print("\n" + "=" * 70 + "\n")
    
    return success_count == total_count

if __name__ == '__main__':
    success = run_all_training()
    sys.exit(0 if success else 1)
