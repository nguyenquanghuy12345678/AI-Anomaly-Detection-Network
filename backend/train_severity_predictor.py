"""
Train Alert Severity Prediction Model
Dự đoán mức độ nghiêm trọng của alerts: Low, Medium, High, Critical
"""
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class SeverityPredictor:
    """Train model to predict alert severity"""
    
    def __init__(self, model_dir='./models', data_dir='./data/datasets'):
        self.model_dir = model_dir
        self.data_dir = data_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
    
    def generate_severity_dataset(self, n_samples=3000):
        """Generate dataset with severity labels"""
        print(f"\n🔄 Generating severity prediction dataset...")
        
        data = []
        severities = ['low', 'medium', 'high', 'critical']
        
        for _ in range(n_samples):
            severity = np.random.choice(severities, p=[0.3, 0.35, 0.25, 0.1])
            
            if severity == 'low':
                record = {
                    'connection_rate': np.random.uniform(0, 10),
                    'failed_attempts': np.random.randint(1, 5),
                    'data_volume_mb': np.random.uniform(0, 10),
                    'unique_sources': np.random.randint(1, 3),
                    'unique_destinations': np.random.randint(1, 3),
                    'unusual_ports': np.random.randint(0, 2),
                    'time_window_minutes': np.random.uniform(1, 60),
                    'is_encrypted': np.random.choice([0, 1], p=[0.3, 0.7]),
                    'matches_known_signature': np.random.choice([0, 1], p=[0.9, 0.1]),
                    'geographic_anomaly': np.random.choice([0, 1], p=[0.95, 0.05]),
                    'affected_systems': np.random.randint(1, 2),
                    'business_hours': np.random.choice([0, 1], p=[0.3, 0.7]),
                    'severity': 'low'
                }
            elif severity == 'medium':
                record = {
                    'connection_rate': np.random.uniform(10, 50),
                    'failed_attempts': np.random.randint(5, 20),
                    'data_volume_mb': np.random.uniform(10, 100),
                    'unique_sources': np.random.randint(3, 10),
                    'unique_destinations': np.random.randint(3, 10),
                    'unusual_ports': np.random.randint(2, 5),
                    'time_window_minutes': np.random.uniform(5, 30),
                    'is_encrypted': np.random.choice([0, 1], p=[0.5, 0.5]),
                    'matches_known_signature': np.random.choice([0, 1], p=[0.7, 0.3]),
                    'geographic_anomaly': np.random.choice([0, 1], p=[0.8, 0.2]),
                    'affected_systems': np.random.randint(2, 5),
                    'business_hours': np.random.choice([0, 1], p=[0.5, 0.5]),
                    'severity': 'medium'
                }
            elif severity == 'high':
                record = {
                    'connection_rate': np.random.uniform(50, 150),
                    'failed_attempts': np.random.randint(20, 100),
                    'data_volume_mb': np.random.uniform(100, 1000),
                    'unique_sources': np.random.randint(10, 50),
                    'unique_destinations': np.random.randint(10, 30),
                    'unusual_ports': np.random.randint(5, 20),
                    'time_window_minutes': np.random.uniform(1, 15),
                    'is_encrypted': np.random.choice([0, 1], p=[0.7, 0.3]),
                    'matches_known_signature': np.random.choice([0, 1], p=[0.4, 0.6]),
                    'geographic_anomaly': np.random.choice([0, 1], p=[0.5, 0.5]),
                    'affected_systems': np.random.randint(5, 20),
                    'business_hours': np.random.choice([0, 1]),
                    'severity': 'high'
                }
            else:  # critical
                record = {
                    'connection_rate': np.random.uniform(150, 500),
                    'failed_attempts': np.random.randint(100, 1000),
                    'data_volume_mb': np.random.uniform(1000, 10000),
                    'unique_sources': np.random.randint(50, 200),
                    'unique_destinations': np.random.randint(30, 100),
                    'unusual_ports': np.random.randint(20, 100),
                    'time_window_minutes': np.random.uniform(0.1, 5),
                    'is_encrypted': np.random.choice([0, 1], p=[0.8, 0.2]),
                    'matches_known_signature': np.random.choice([0, 1], p=[0.2, 0.8]),
                    'geographic_anomaly': np.random.choice([0, 1], p=[0.3, 0.7]),
                    'affected_systems': np.random.randint(20, 100),
                    'business_hours': np.random.choice([0, 1]),
                    'severity': 'critical'
                }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        filepath = os.path.join(self.data_dir, 'severity_prediction.csv')
        df.to_csv(filepath, index=False)
        
        print(f"✅ Severity dataset generated: {filepath}")
        print(f"   Total samples: {len(df)}")
        for sev in severities:
            count = (df['severity'] == sev).sum()
            print(f"   {sev:10s}: {count:,} samples ({count/len(df)*100:.1f}%)")
        
        return df
    
    def train_model(self, data):
        """Train Gradient Boosting classifier"""
        print(f"\n🤖 Training Severity Prediction Model...")
        
        X = data.drop('severity', axis=1)
        y = data['severity']
        
        self.feature_names = X.columns.tolist()
        y_encoded = self.label_encoder.fit_transform(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        print(f"   Training samples: {len(X_train)}")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            verbose=1
        )
        
        print("Training in progress...")
        self.model.fit(X_train_scaled, y_train)
        print("✅ Model training complete!")
        
        return self.evaluate_model(X_test_scaled, y_test)
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model"""
        print("\n📊 Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📈 Model Performance:")
        print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=self.label_encoder.classes_))
        
        return {'accuracy': accuracy}
    
    def save_model(self, version='1.0.0'):
        """Save model"""
        print(f"\n💾 Saving severity predictor (version {version})...")
        
        model_file = os.path.join(self.model_dir, f'severity_predictor_{version}.pkl')
        scaler_file = os.path.join(self.model_dir, f'severity_scaler_{version}.pkl')
        encoder_file = os.path.join(self.model_dir, f'severity_encoder_{version}.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        joblib.dump(self.label_encoder, encoder_file)
        
        import json
        features_file = os.path.join(self.model_dir, f'severity_features_{version}.json')
        with open(features_file, 'w') as f:
            json.dump({
                'features': self.feature_names,
                'classes': self.label_encoder.classes_.tolist()
            }, f, indent=2)
        
        print(f"✅ All files saved successfully")

def main():
    print("=" * 60)
    print("🎯 Alert Severity Prediction Model Training")
    print("=" * 60)
    
    predictor = SeverityPredictor()
    data = predictor.generate_severity_dataset(n_samples=3000)
    metrics = predictor.train_model(data)
    predictor.save_model(version='1.0.0')
    
    print("\n" + "=" * 60)
    print("✅ Severity Predictor Training Complete!")
    print("=" * 60)
    print(f"\n📊 Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"\n💡 Model can now predict alert severity levels!")

if __name__ == '__main__':
    main()
