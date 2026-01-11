"""
Dataset downloader and generator for network anomaly detection
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import urllib.request
import zipfile
import json

class DatasetManager:
    """Manage datasets for anomaly detection"""
    
    def __init__(self, data_dir='./data/datasets'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        print(f"📁 Dataset directory: {data_dir}")
    
    def generate_synthetic_dataset(self, n_samples=10000, anomaly_ratio=0.1):
        """Generate synthetic network traffic dataset"""
        print(f"\n🔄 Generating synthetic dataset with {n_samples} samples...")
        
        # Calculate number of normal and anomaly samples
        n_anomalies = int(n_samples * anomaly_ratio)
        n_normal = n_samples - n_anomalies
        
        # Generate normal traffic
        normal_data = self._generate_normal_traffic(n_normal)
        
        # Generate anomalous traffic
        anomaly_data = self._generate_anomalous_traffic(n_anomalies)
        
        # Combine and shuffle
        data = pd.concat([normal_data, anomaly_data], ignore_index=True)
        data = data.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Save to CSV
        filepath = os.path.join(self.data_dir, 'synthetic_network_traffic.csv')
        data.to_csv(filepath, index=False)
        
        print(f"✅ Synthetic dataset generated: {filepath}")
        print(f"   Total samples: {len(data)}")
        print(f"   Normal: {n_normal} ({n_normal/len(data)*100:.1f}%)")
        print(f"   Anomalies: {n_anomalies} ({n_anomalies/len(data)*100:.1f}%)")
        
        return data
    
    def _generate_normal_traffic(self, n_samples):
        """Generate normal network traffic patterns"""
        data = []
        
        for _ in range(n_samples):
            record = {
                'timestamp': datetime.now() - timedelta(seconds=np.random.randint(0, 86400)),
                'source_port': np.random.randint(1024, 65535),
                'dest_port': np.random.choice([80, 443, 22, 3306, 5432], p=[0.4, 0.3, 0.15, 0.1, 0.05]),
                'protocol': np.random.choice(['TCP', 'UDP', 'HTTP', 'HTTPS'], p=[0.4, 0.2, 0.2, 0.2]),
                'packet_size': np.random.normal(512, 200),  # Normal packet size
                'packets': np.random.randint(10, 100),
                'bytes': np.random.randint(1000, 50000),
                'duration': np.random.uniform(0.1, 5.0),
                'flag_count': np.random.randint(0, 3),
                'syn_flag': np.random.choice([0, 1], p=[0.9, 0.1]),
                'ack_flag': np.random.choice([0, 1], p=[0.3, 0.7]),
                'rst_flag': 0,
                'connection_rate': np.random.uniform(0, 5),
                'label': 0  # Normal traffic
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    def _generate_anomalous_traffic(self, n_samples):
        """Generate anomalous network traffic patterns"""
        data = []
        
        anomaly_types = ['dos', 'port_scan', 'brute_force', 'data_exfiltration']
        
        for _ in range(n_samples):
            anomaly_type = np.random.choice(anomaly_types)
            
            if anomaly_type == 'dos':
                # DoS attack: high packet count, small packets, high rate
                record = {
                    'timestamp': datetime.now() - timedelta(seconds=np.random.randint(0, 86400)),
                    'source_port': np.random.randint(1024, 65535),
                    'dest_port': np.random.choice([80, 443]),
                    'protocol': 'TCP',
                    'packet_size': np.random.normal(100, 50),  # Small packets
                    'packets': np.random.randint(1000, 10000),  # Many packets
                    'bytes': np.random.randint(100000, 1000000),
                    'duration': np.random.uniform(0.01, 0.5),  # Short duration
                    'flag_count': np.random.randint(5, 15),
                    'syn_flag': 1,
                    'ack_flag': 0,
                    'rst_flag': np.random.choice([0, 1]),
                    'connection_rate': np.random.uniform(50, 200),  # High rate
                    'label': 1  # Anomaly
                }
            
            elif anomaly_type == 'port_scan':
                # Port scan: many different ports, small packets
                record = {
                    'timestamp': datetime.now() - timedelta(seconds=np.random.randint(0, 86400)),
                    'source_port': np.random.randint(1024, 65535),
                    'dest_port': np.random.randint(1, 65535),  # Random ports
                    'protocol': 'TCP',
                    'packet_size': np.random.normal(64, 20),  # Very small packets
                    'packets': np.random.randint(1, 5),
                    'bytes': np.random.randint(64, 500),
                    'duration': np.random.uniform(0.001, 0.1),
                    'flag_count': np.random.randint(1, 3),
                    'syn_flag': 1,
                    'ack_flag': 0,
                    'rst_flag': 1,
                    'connection_rate': np.random.uniform(10, 50),
                    'label': 1  # Anomaly
                }
            
            elif anomaly_type == 'brute_force':
                # Brute force: repeated connections to auth ports
                record = {
                    'timestamp': datetime.now() - timedelta(seconds=np.random.randint(0, 86400)),
                    'source_port': np.random.randint(1024, 65535),
                    'dest_port': np.random.choice([22, 3389, 21, 23]),  # Auth ports
                    'protocol': np.random.choice(['TCP', 'SSH']),
                    'packet_size': np.random.normal(300, 100),
                    'packets': np.random.randint(5, 50),
                    'bytes': np.random.randint(1000, 10000),
                    'duration': np.random.uniform(1.0, 10.0),
                    'flag_count': np.random.randint(3, 10),
                    'syn_flag': 1,
                    'ack_flag': 1,
                    'rst_flag': np.random.choice([0, 1]),
                    'connection_rate': np.random.uniform(20, 100),  # High rate
                    'label': 1  # Anomaly
                }
            
            else:  # data_exfiltration
                # Data exfiltration: large data transfer
                record = {
                    'timestamp': datetime.now() - timedelta(seconds=np.random.randint(0, 86400)),
                    'source_port': np.random.randint(1024, 65535),
                    'dest_port': np.random.choice([80, 443, 8080]),
                    'protocol': np.random.choice(['HTTP', 'HTTPS']),
                    'packet_size': np.random.normal(1400, 200),  # Large packets
                    'packets': np.random.randint(500, 5000),
                    'bytes': np.random.randint(500000, 5000000),  # Large data
                    'duration': np.random.uniform(10.0, 300.0),  # Long duration
                    'flag_count': np.random.randint(2, 5),
                    'syn_flag': 1,
                    'ack_flag': 1,
                    'rst_flag': 0,
                    'connection_rate': np.random.uniform(1, 10),
                    'label': 1  # Anomaly
                }
            
            data.append(record)
        
        return pd.DataFrame(data)
    
    def load_dataset(self, filename='synthetic_network_traffic.csv'):
        """Load dataset from file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️  Dataset not found: {filepath}")
            print("Generating new dataset...")
            return self.generate_synthetic_dataset()
        
        print(f"📂 Loading dataset: {filepath}")
        data = pd.read_csv(filepath)
        print(f"✅ Dataset loaded: {len(data)} samples")
        
        return data
    
    def download_cicids2017(self):
        """
        Download CICIDS2017 dataset (requires manual download)
        Info: https://www.unb.ca/cic/datasets/ids-2017.html
        """
        print("\n📥 CICIDS2017 Dataset Download Instructions:")
        print("=" * 60)
        print("The CICIDS2017 dataset is a real network traffic dataset")
        print("with labeled attacks. To use it:")
        print()
        print("1. Visit: https://www.unb.ca/cic/datasets/ids-2017.html")
        print("2. Download the CSV files")
        print("3. Extract to:", self.data_dir)
        print("4. Place CSV files in the datasets folder")
        print()
        print("For this demo, we'll use synthetic data instead.")
        print("=" * 60)
    
    def get_dataset_info(self):
        """Get information about available datasets"""
        datasets = []
        
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if file.endswith('.csv'):
                    filepath = os.path.join(self.data_dir, file)
                    size = os.path.getsize(filepath)
                    datasets.append({
                        'name': file,
                        'path': filepath,
                        'size': f"{size / 1024:.2f} KB"
                    })
        
        return datasets

def main():
    """Main function to generate or download datasets"""
    print("=" * 60)
    print("🤖 AI/ML Dataset Manager")
    print("=" * 60)
    
    # Initialize dataset manager
    manager = DatasetManager()
    
    # Show CICIDS2017 download info
    manager.download_cicids2017()
    
    # Generate synthetic dataset
    print("\nGenerating training dataset...")
    dataset = manager.generate_synthetic_dataset(n_samples=10000, anomaly_ratio=0.1)
    
    # Show dataset statistics
    print("\n📊 Dataset Statistics:")
    print(f"   Total samples: {len(dataset)}")
    print(f"   Features: {len(dataset.columns) - 1}")
    print(f"   Normal traffic: {(dataset['label'] == 0).sum()}")
    print(f"   Anomalies: {(dataset['label'] == 1).sum()}")
    
    # Show available datasets
    print("\n📚 Available Datasets:")
    for ds in manager.get_dataset_info():
        print(f"   - {ds['name']} ({ds['size']})")
    
    print("\n✅ Dataset preparation complete!")
    print(f"📁 Location: {manager.data_dir}")
    print("\n💡 Next step: Run 'python train_model.py' to train the model")

if __name__ == '__main__':
    main()
