"""
Train AI/ML model for network anomaly detection
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

class ModelTrainer:
    """Train and evaluate anomaly detection model"""
    
    def __init__(self, model_dir='./models', data_dir='./data/datasets'):
        self.model_dir = model_dir
        self.data_dir = data_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
        print(f"📁 Model directory: {model_dir}")
        print(f"📁 Data directory: {data_dir}")
    
    def load_data(self, filename='synthetic_network_traffic.csv'):
        """Load training data"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset not found: {filepath}\nRun 'python prepare_dataset.py' first!")
        
        print(f"\n📂 Loading dataset: {filepath}")
        data = pd.read_csv(filepath)
        
        # Convert timestamp to features if it's a string
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data['hour'] = data['timestamp'].dt.hour
            data['day_of_week'] = data['timestamp'].dt.dayofweek
            data = data.drop('timestamp', axis=1)
        
        print(f"✅ Dataset loaded: {len(data)} samples, {len(data.columns)} columns")
        
        return data
    
    def prepare_features(self, data):
        """Prepare features for training"""
        print("\n🔧 Preparing features...")
        
        # Separate features and labels
        if 'label' in data.columns:
            X = data.drop('label', axis=1)
            y = data['label']
        else:
            X = data
            y = None
        
        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            # Simple label encoding for protocol
            if col == 'protocol':
                protocol_map = {'TCP': 1, 'UDP': 2, 'HTTP': 3, 'HTTPS': 4, 'SSH': 5, 'FTP': 6}
                X[col] = X[col].map(protocol_map).fillna(0)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        print(f"✅ Features prepared: {len(self.feature_names)} features")
        print(f"   Features: {', '.join(self.feature_names[:5])}...")
        
        return X, y
    
    def train_model(self, X_train, contamination=0.1):
        """Train Isolation Forest model"""
        print(f"\n🤖 Training Isolation Forest model...")
        print(f"   Contamination rate: {contamination}")
        print(f"   Training samples: {len(X_train)}")
        
        # Initialize model
        self.model = IsolationForest(
            contamination=contamination,
            max_samples=min(256, len(X_train)),
            random_state=42,
            n_estimators=100,
            n_jobs=-1,
            verbose=1
        )
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        print("Training in progress...")
        self.model.fit(X_scaled)
        
        print("✅ Model training complete!")
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n📊 Evaluating model...")
        
        # Scale test data
        X_scaled = self.scaler.transform(X_test)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        # Convert predictions: 1 (normal) -> 0, -1 (anomaly) -> 1
        predictions = np.where(predictions == 1, 0, 1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        
        print("\n📈 Model Performance:")
        print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
        print(f"   Recall:    {recall:.4f} ({recall*100:.2f}%)")
        print(f"   F1 Score:  {f1:.4f} ({f1*100:.2f}%)")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, predictions)
        print("\n📊 Confusion Matrix:")
        print(f"   True Negatives:  {cm[0][0]}")
        print(f"   False Positives: {cm[0][1]}")
        print(f"   False Negatives: {cm[1][0]}")
        print(f"   True Positives:  {cm[1][1]}")
        
        # Classification report
        print("\n📋 Classification Report:")
        print(classification_report(y_test, predictions, 
                                   target_names=['Normal', 'Anomaly']))
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist()
        }
    
    def save_model(self, version='1.0.0'):
        """Save trained model"""
        print(f"\n💾 Saving model (version {version})...")
        
        model_file = os.path.join(self.model_dir, f'anomaly_detector_{version}.pkl')
        scaler_file = os.path.join(self.model_dir, f'scaler_{version}.pkl')
        features_file = os.path.join(self.model_dir, f'features_{version}.json')
        
        # Save model
        joblib.dump(self.model, model_file)
        print(f"✅ Model saved: {model_file}")
        
        # Save scaler
        joblib.dump(self.scaler, scaler_file)
        print(f"✅ Scaler saved: {scaler_file}")
        
        # Save feature names
        import json
        with open(features_file, 'w') as f:
            json.dump({'features': self.feature_names}, f, indent=2)
        print(f"✅ Features saved: {features_file}")
    
    def update_model_metrics(self, metrics, app_context=None):
        """Update model metrics in database"""
        if app_context:
            print("\n📝 Updating model metrics in database...")
            try:
                with app_context:
                    from models.model_metrics import ModelMetrics
                    from database import db
                    
                    model_metrics = ModelMetrics(
                        timestamp=datetime.utcnow(),
                        model_version='1.0.0',
                        status='active',
                        accuracy=metrics['accuracy'],
                        precision=metrics['precision'],
                        recall=metrics['recall'],
                        f1_score=metrics['f1_score'],
                        detection_rate=metrics['recall'],
                        false_positive_rate=1 - metrics['precision'],
                        last_trained=datetime.utcnow(),
                        dataset_size=10000,
                        predictions_made=0
                    )
                    
                    db.session.add(model_metrics)
                    db.session.commit()
                    print("✅ Model metrics updated in database")
            except Exception as e:
                print(f"⚠️  Could not update database: {e}")

def main():
    """Main training function"""
    print("=" * 60)
    print("🤖 AI/ML Model Training")
    print("=" * 60)
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    try:
        # Load data
        data = trainer.load_data()
        
        # Prepare features
        X, y = trainer.prepare_features(data)
        
        # Split data
        print("\n✂️  Splitting data into train/test sets...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"   Training set: {len(X_train)} samples")
        print(f"   Test set: {len(X_test)} samples")
        
        # Train model
        contamination = (y_train == 1).sum() / len(y_train)
        trainer.train_model(X_train, contamination=contamination)
        
        # Evaluate model
        metrics = trainer.evaluate_model(X_test, y_test)
        
        # Save model
        trainer.save_model(version='1.0.0')
        
        # Try to update database metrics
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from app import app
            trainer.update_model_metrics(metrics, app.app_context())
        except:
            print("⚠️  Database update skipped (run separately if needed)")
        
        print("\n" + "=" * 60)
        print("✅ Model Training Complete!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   Model Accuracy: {metrics['accuracy']*100:.2f}%")
        print(f"   Model saved to: {trainer.model_dir}")
        print(f"\n💡 Your AI model is ready to use!")
        print(f"   Restart the backend to load the new model")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Solution: Run 'python prepare_dataset.py' first to generate dataset")
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
