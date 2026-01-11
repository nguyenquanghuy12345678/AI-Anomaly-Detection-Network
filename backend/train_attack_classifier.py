"""
Train Attack Type Classification Model
Phân loại cụ thể loại tấn công: DoS, Port Scan, Brute Force, Data Exfiltration
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

class AttackClassifier:
    """Train classifier to identify specific attack types"""
    
    def __init__(self, model_dir='./models', data_dir='./data/datasets'):
        self.model_dir = model_dir
        self.data_dir = data_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        
    def generate_attack_dataset(self, n_samples=5000):
        """Generate dataset with labeled attack types"""
        print(f"\n🔄 Generating attack classification dataset...")
        
        data = []
        attack_types = ['dos', 'port_scan', 'brute_force', 'data_exfiltration']
        samples_per_type = n_samples // len(attack_types)
        
        for attack_type in attack_types:
            for _ in range(samples_per_type):
                if attack_type == 'dos':
                    record = {
                        'source_port': np.random.randint(1024, 65535),
                        'dest_port': np.random.choice([80, 443]),
                        'protocol': 1,  # TCP
                        'packet_size': np.random.normal(100, 50),
                        'packets': np.random.randint(1000, 10000),
                        'bytes': np.random.randint(100000, 1000000),
                        'duration': np.random.uniform(0.01, 0.5),
                        'flag_count': np.random.randint(5, 15),
                        'syn_flag': 1,
                        'ack_flag': 0,
                        'rst_flag': np.random.choice([0, 1]),
                        'connection_rate': np.random.uniform(50, 200),
                        'hour': np.random.randint(0, 24),
                        'day_of_week': np.random.randint(0, 7),
                        'attack_type': 'dos'
                    }
                elif attack_type == 'port_scan':
                    record = {
                        'source_port': np.random.randint(1024, 65535),
                        'dest_port': np.random.randint(1, 65535),
                        'protocol': 1,  # TCP
                        'packet_size': np.random.normal(64, 20),
                        'packets': np.random.randint(1, 5),
                        'bytes': np.random.randint(64, 500),
                        'duration': np.random.uniform(0.001, 0.1),
                        'flag_count': np.random.randint(1, 3),
                        'syn_flag': 1,
                        'ack_flag': 0,
                        'rst_flag': 1,
                        'connection_rate': np.random.uniform(10, 50),
                        'hour': np.random.randint(0, 24),
                        'day_of_week': np.random.randint(0, 7),
                        'attack_type': 'port_scan'
                    }
                elif attack_type == 'brute_force':
                    record = {
                        'source_port': np.random.randint(1024, 65535),
                        'dest_port': np.random.choice([22, 3389, 21, 23]),
                        'protocol': np.random.choice([1, 5]),  # TCP or SSH
                        'packet_size': np.random.normal(300, 100),
                        'packets': np.random.randint(5, 50),
                        'bytes': np.random.randint(1000, 10000),
                        'duration': np.random.uniform(1.0, 10.0),
                        'flag_count': np.random.randint(3, 10),
                        'syn_flag': 1,
                        'ack_flag': 1,
                        'rst_flag': np.random.choice([0, 1]),
                        'connection_rate': np.random.uniform(20, 100),
                        'hour': np.random.randint(0, 24),
                        'day_of_week': np.random.randint(0, 7),
                        'attack_type': 'brute_force'
                    }
                else:  # data_exfiltration
                    record = {
                        'source_port': np.random.randint(1024, 65535),
                        'dest_port': np.random.choice([80, 443, 8080]),
                        'protocol': np.random.choice([3, 4]),  # HTTP or HTTPS
                        'packet_size': np.random.normal(1400, 200),
                        'packets': np.random.randint(500, 5000),
                        'bytes': np.random.randint(500000, 5000000),
                        'duration': np.random.uniform(10.0, 300.0),
                        'flag_count': np.random.randint(2, 5),
                        'syn_flag': 1,
                        'ack_flag': 1,
                        'rst_flag': 0,
                        'connection_rate': np.random.uniform(1, 10),
                        'hour': np.random.randint(0, 24),
                        'day_of_week': np.random.randint(0, 7),
                        'attack_type': 'data_exfiltration'
                    }
                
                data.append(record)
        
        df = pd.DataFrame(data)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Save dataset
        filepath = os.path.join(self.data_dir, 'attack_classification.csv')
        df.to_csv(filepath, index=False)
        
        print(f"✅ Attack classification dataset generated: {filepath}")
        print(f"   Total samples: {len(df)}")
        for attack_type in attack_types:
            count = (df['attack_type'] == attack_type).sum()
            print(f"   {attack_type:20s}: {count:,} samples")
        
        return df
    
    def train_model(self, data):
        """Train Random Forest classifier"""
        print(f"\n🤖 Training Attack Type Classifier...")
        
        # Prepare features and labels
        X = data.drop('attack_type', axis=1)
        y = data['attack_type']
        
        self.feature_names = X.columns.tolist()
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        print(f"   Training samples: {len(X_train)}")
        print(f"   Test samples: {len(X_test)}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        print("Training in progress...")
        self.model.fit(X_train_scaled, y_train)
        print("✅ Model training complete!")
        
        # Evaluate
        return self.evaluate_model(X_test_scaled, y_test)
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n📊 Evaluating model...")
        
        # Predict
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📈 Model Performance:")
        print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n📊 Confusion Matrix:")
        attack_names = self.label_encoder.classes_
        print(f"   Classes: {', '.join(attack_names)}")
        print(f"\n{cm}")
        
        # Classification report
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=attack_names))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔍 Top 10 Important Features:")
        for idx, row in feature_importance.head(10).iterrows():
            print(f"   {row['feature']:20s}: {row['importance']:.4f}")
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': cm.tolist(),
            'classes': attack_names.tolist()
        }
    
    def save_model(self, version='1.0.0'):
        """Save trained model"""
        print(f"\n💾 Saving attack classifier (version {version})...")
        
        model_file = os.path.join(self.model_dir, f'attack_classifier_{version}.pkl')
        scaler_file = os.path.join(self.model_dir, f'attack_scaler_{version}.pkl')
        encoder_file = os.path.join(self.model_dir, f'attack_encoder_{version}.pkl')
        features_file = os.path.join(self.model_dir, f'attack_features_{version}.json')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        joblib.dump(self.label_encoder, encoder_file)
        
        import json
        with open(features_file, 'w') as f:
            json.dump({
                'features': self.feature_names,
                'classes': self.label_encoder.classes_.tolist()
            }, f, indent=2)
        
        print(f"✅ Model saved: {model_file}")
        print(f"✅ Scaler saved: {scaler_file}")
        print(f"✅ Encoder saved: {encoder_file}")
        print(f"✅ Features saved: {features_file}")

def main():
    """Main training function"""
    print("=" * 60)
    print("🎯 Attack Type Classification Model Training")
    print("=" * 60)
    
    classifier = AttackClassifier()
    
    # Generate dataset
    data = classifier.generate_attack_dataset(n_samples=5000)
    
    # Train model
    metrics = classifier.train_model(data)
    
    # Save model
    classifier.save_model(version='1.0.0')
    
    print("\n" + "=" * 60)
    print("✅ Attack Classifier Training Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Model Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"   Attack Types: {', '.join(metrics['classes'])}")
    print(f"\n💡 Model can now classify specific attack types!")

if __name__ == '__main__':
    main()
