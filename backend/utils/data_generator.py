"""
Data generator for testing and demo purposes
"""
import random
import uuid
from datetime import datetime, timedelta
from models.anomaly import Anomaly
from models.alert import Alert
from models.network_traffic import NetworkTraffic
from models.connection import Connection
from database import db

class DataGenerator:
    """Generate mock data for testing"""
    
    ANOMALY_TYPES = [
        'DoS Attack', 'Port Scan', 'Brute Force', 'SQL Injection',
        'XSS Attack', 'Malware', 'Suspicious Traffic', 'Unauthorized Access',
        'Data Exfiltration', 'Other'
    ]
    
    SEVERITIES = ['low', 'medium', 'high', 'critical']
    PROTOCOLS = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'FTP']
    CONNECTION_STATES = ['ESTABLISHED', 'LISTENING', 'TIME_WAIT', 'CLOSE_WAIT']
    
    @staticmethod
    def generate_ip():
        """Generate random IP address"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    @staticmethod
    def generate_anomalies(count=100):
        """Generate multiple anomalies"""
        anomalies = []
        
        for i in range(count):
            severity = random.choice(DataGenerator.SEVERITIES)
            anomaly_type = random.choice(DataGenerator.ANOMALY_TYPES)
            
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 48)),
                source_ip=DataGenerator.generate_ip(),
                destination_ip=f"192.168.1.{random.randint(1, 255)}",
                source_port=random.randint(1024, 65535),
                destination_port=random.choice([80, 443, 22, 3306, 5432, 8080, 21]),
                type=anomaly_type,
                severity=severity,
                confidence=round(random.uniform(0.5, 0.99), 2),
                status=random.choice(['active', 'active', 'active', 'blocked', 'resolved']),
                description=f"Detected {anomaly_type} from suspicious source",
                protocol=random.choice(DataGenerator.PROTOCOLS),
                bytes_transferred=random.randint(1000, 10000000),
                packets=random.randint(10, 50000)
            )
            
            anomalies.append(anomaly)
        
        db.session.bulk_save_objects(anomalies)
        db.session.commit()
        
        print(f"✅ Generated {count} anomalies")
        return anomalies
    
    @staticmethod
    def generate_alerts(count=50):
        """Generate multiple alerts"""
        alerts = []
        
        for i in range(count):
            severity = random.choice(DataGenerator.SEVERITIES)
            alert_type = random.choice(DataGenerator.ANOMALY_TYPES)
            
            alert = Alert(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
                severity=severity,
                status=random.choice(['unread', 'unread', 'read', 'dismissed']),
                type=alert_type,
                title=f"{severity.capitalize()} severity threat detected",
                description=f"Detected {alert_type} activity requiring attention",
                source_ip=DataGenerator.generate_ip(),
                affected_systems=random.randint(1, 10),
                requires_action=severity in ['high', 'critical']
            )
            
            alerts.append(alert)
        
        db.session.bulk_save_objects(alerts)
        db.session.commit()
        
        print(f"✅ Generated {count} alerts")
        return alerts
    
    @staticmethod
    def generate_traffic(count=1000):
        """Generate network traffic data"""
        traffic_records = []
        
        for i in range(count):
            base_traffic = random.uniform(10, 100)
            
            traffic = NetworkTraffic(
                timestamp=datetime.utcnow() - timedelta(seconds=i * 10),
                incoming_mbps=round(base_traffic + random.uniform(-10, 20), 2),
                outgoing_mbps=round(base_traffic * 0.6 + random.uniform(-5, 10), 2),
                total_mbps=round(base_traffic * 1.6, 2),
                tcp_traffic=round(base_traffic * 0.5, 2),
                udp_traffic=round(base_traffic * 0.2, 2),
                http_traffic=round(base_traffic * 0.15, 2),
                https_traffic=round(base_traffic * 0.1, 2),
                ssh_traffic=round(base_traffic * 0.03, 2),
                ftp_traffic=round(base_traffic * 0.02, 2),
                active_connections=random.randint(50, 1000),
                anomaly_count=random.randint(0, 10),
                blocked_threats=random.randint(0, 5),
                avg_response_time=round(random.uniform(10, 200), 2)
            )
            
            traffic_records.append(traffic)
        
        db.session.bulk_save_objects(traffic_records)
        db.session.commit()
        
        print(f"✅ Generated {count} traffic records")
        return traffic_records
    
    @staticmethod
    def generate_connections(count=200):
        """Generate active connections"""
        connections = []
        
        for i in range(count):
            connection = Connection(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() - timedelta(seconds=random.randint(0, 3600)),
                source_ip=DataGenerator.generate_ip(),
                source_port=random.randint(1024, 65535),
                dest_ip=DataGenerator.generate_ip(),
                dest_port=random.choice([80, 443, 22, 3306, 5432, 8080]),
                protocol=random.choice(DataGenerator.PROTOCOLS),
                state=random.choice(DataGenerator.CONNECTION_STATES),
                bytes_transferred=random.randint(1000, 5000000),
                packets=random.randint(10, 10000),
                duration=random.randint(1, 3600),
                is_active=random.choice([True, True, True, False])
            )
            
            connections.append(connection)
        
        db.session.bulk_save_objects(connections)
        db.session.commit()
        
        print(f"✅ Generated {count} connections")
        return connections
    
    @staticmethod
    def generate_all():
        """Generate all types of data"""
        print("🔄 Generating demo data...")
        
        DataGenerator.generate_anomalies(100)
        DataGenerator.generate_alerts(50)
        DataGenerator.generate_traffic(1000)
        DataGenerator.generate_connections(200)
        
        print("✅ Demo data generation complete!")

if __name__ == '__main__':
    # Can be run standalone for testing
    from app import app
    
    with app.app_context():
        DataGenerator.generate_all()
