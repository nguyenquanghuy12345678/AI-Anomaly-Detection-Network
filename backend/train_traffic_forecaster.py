"""
Train Traffic Forecasting Model
Dự đoán xu hướng network traffic để phát hiện anomalies sớm
"""
import os
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class TrafficForecaster:
    """Train model to forecast network traffic patterns"""
    
    def __init__(self, model_dir='./models', data_dir='./data/datasets'):
        self.model_dir = model_dir
        self.data_dir = data_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
    
    def generate_timeseries_dataset(self, n_days=30, samples_per_day=96):
        """Generate time series traffic data (15-min intervals)"""
        print(f"\n🔄 Generating traffic forecasting dataset...")
        print(f"   Period: {n_days} days")
        print(f"   Samples per day: {samples_per_day} (15-min intervals)")
        
        data = []
        start_date = datetime.now() - timedelta(days=n_days)
        
        total_samples = n_days * samples_per_day
        
        for i in range(total_samples):
            timestamp = start_date + timedelta(minutes=15*i)
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            day_of_month = timestamp.day
            
            # Base traffic with daily/weekly patterns
            base_traffic = 100
            
            # Daily pattern (higher during business hours)
            if 8 <= hour <= 18:
                base_traffic *= np.random.uniform(2.0, 3.0)
            elif 19 <= hour <= 23:
                base_traffic *= np.random.uniform(1.5, 2.0)
            else:
                base_traffic *= np.random.uniform(0.5, 1.0)
            
            # Weekly pattern (lower on weekends)
            if day_of_week >= 5:  # Weekend
                base_traffic *= 0.6
            
            # Add some randomness
            base_traffic *= np.random.uniform(0.8, 1.2)
            
            # Occasional spikes (simulate peaks)
            if np.random.random() < 0.05:
                base_traffic *= np.random.uniform(2.0, 4.0)
            
            record = {
                'timestamp': timestamp,
                'hour': hour,
                'day_of_week': day_of_week,
                'day_of_month': day_of_month,
                'is_weekend': int(day_of_week >= 5),
                'is_business_hours': int(8 <= hour <= 18),
                'traffic_mbps': base_traffic,
                'connections_count': int(base_traffic * np.random.uniform(5, 15)),
                'packets_per_sec': int(base_traffic * np.random.uniform(50, 200)),
                'avg_packet_size': np.random.uniform(400, 800),
                'tcp_ratio': np.random.uniform(0.6, 0.9),
                'udp_ratio': np.random.uniform(0.1, 0.3),
                'http_ratio': np.random.uniform(0.3, 0.6),
                # Lag features (previous intervals)
                'traffic_lag_1': base_traffic * np.random.uniform(0.9, 1.1),
                'traffic_lag_2': base_traffic * np.random.uniform(0.8, 1.2),
                'traffic_lag_3': base_traffic * np.random.uniform(0.7, 1.3),
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        
        # Create target (next interval's traffic)
        df['target_traffic'] = df['traffic_mbps'].shift(-1)
        df = df.dropna()
        
        filepath = os.path.join(self.data_dir, 'traffic_forecasting.csv')
        df.to_csv(filepath, index=False)
        
        print(f"✅ Traffic forecasting dataset generated: {filepath}")
        print(f"   Total samples: {len(df):,}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return df
    
    def train_model(self, data):
        """Train Gradient Boosting regressor"""
        print(f"\n🤖 Training Traffic Forecasting Model...")
        
        # Drop timestamp and target
        feature_cols = [col for col in data.columns 
                       if col not in ['timestamp', 'target_traffic']]
        
        X = data[feature_cols]
        y = data['target_traffic']
        
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False  # Time series - don't shuffle
        )
        
        print(f"   Training samples: {len(X_train):,}")
        print(f"   Test samples: {len(X_test):,}")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            random_state=42,
            verbose=1
        )
        
        print("Training in progress...")
        self.model.fit(X_train_scaled, y_train)
        print("✅ Model training complete!")
        
        return self.evaluate_model(X_test_scaled, y_test)
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate forecasting model"""
        print("\n📊 Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n📈 Model Performance:")
        print(f"   MAE (Mean Absolute Error): {mae:.2f} Mbps")
        print(f"   RMSE (Root Mean Squared Error): {rmse:.2f} Mbps")
        print(f"   R² Score: {r2:.4f} ({r2*100:.2f}%)")
        
        # Show sample predictions
        print(f"\n🔍 Sample Predictions:")
        for i in range(min(5, len(y_test))):
            actual = y_test.iloc[i]
            predicted = y_pred[i]
            error = abs(actual - predicted)
            print(f"   Actual: {actual:.2f} Mbps | Predicted: {predicted:.2f} Mbps | Error: {error:.2f}")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2_score': r2
        }
    
    def save_model(self, version='1.0.0'):
        """Save forecasting model"""
        print(f"\n💾 Saving traffic forecaster (version {version})...")
        
        model_file = os.path.join(self.model_dir, f'traffic_forecaster_{version}.pkl')
        scaler_file = os.path.join(self.model_dir, f'traffic_scaler_{version}.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        
        import json
        features_file = os.path.join(self.model_dir, f'traffic_features_{version}.json')
        with open(features_file, 'w') as f:
            json.dump({'features': self.feature_names}, f, indent=2)
        
        print(f"✅ Model saved: {model_file}")
        print(f"✅ Scaler saved: {scaler_file}")
        print(f"✅ Features saved: {features_file}")

def main():
    print("=" * 60)
    print("📈 Traffic Forecasting Model Training")
    print("=" * 60)
    
    forecaster = TrafficForecaster()
    data = forecaster.generate_timeseries_dataset(n_days=30, samples_per_day=96)
    metrics = forecaster.train_model(data)
    forecaster.save_model(version='1.0.0')
    
    print("\n" + "=" * 60)
    print("✅ Traffic Forecaster Training Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   R² Score: {metrics['r2_score']*100:.2f}%")
    print(f"   MAE: {metrics['mae']:.2f} Mbps")
    print(f"\n💡 Model can now forecast network traffic patterns!")

if __name__ == '__main__':
    main()
