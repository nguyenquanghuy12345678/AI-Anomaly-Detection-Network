"""
Network monitoring service
"""
import threading
import time
import random
from datetime import datetime
import uuid
from services.websocket_service import emit_anomaly, emit_traffic_update, emit_alert
from services.cache_service import cache

# Global monitoring state
monitoring_active = False
monitoring_thread = None

def generate_mock_traffic_data():
    """Generate mock network traffic data"""
    from models.network_traffic import NetworkTraffic
    from database import db
    
    # Generate realistic traffic patterns
    base_traffic = random.uniform(10, 50)
    
    traffic = NetworkTraffic(
        timestamp=datetime.utcnow(),
        incoming_mbps=round(base_traffic + random.uniform(-5, 10), 2),
        outgoing_mbps=round(base_traffic * 0.6 + random.uniform(-3, 5), 2),
        total_mbps=round(base_traffic * 1.6, 2),
        tcp_traffic=round(base_traffic * 0.5, 2),
        udp_traffic=round(base_traffic * 0.2, 2),
        http_traffic=round(base_traffic * 0.15, 2),
        https_traffic=round(base_traffic * 0.1, 2),
        ssh_traffic=round(base_traffic * 0.03, 2),
        ftp_traffic=round(base_traffic * 0.02, 2),
        active_connections=random.randint(50, 500),
        anomaly_count=random.randint(0, 5),
        blocked_threats=random.randint(0, 3),
        avg_response_time=round(random.uniform(10, 100), 2)
    )
    
    db.session.add(traffic)
    db.session.commit()
    
    return traffic

def generate_mock_anomaly():
    """Generate mock anomaly data"""
    from models.anomaly import Anomaly
    from database import db
    
    types = ['DoS Attack', 'Port Scan', 'Brute Force', 'SQL Injection', 
             'XSS Attack', 'Malware', 'Suspicious Traffic', 'Unauthorized Access']
    severities = ['low', 'medium', 'high', 'critical']
    protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH']
    
    severity = random.choice(severities)
    anomaly_type = random.choice(types)
    
    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        source_ip=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        destination_ip=f"192.168.1.{random.randint(1, 255)}",
        source_port=random.randint(1024, 65535),
        destination_port=random.choice([80, 443, 22, 3306, 5432, 8080]),
        type=anomaly_type,
        severity=severity,
        confidence=round(random.uniform(0.6, 0.99), 2),
        status='active',
        description=f"Detected {anomaly_type} from suspicious IP address",
        protocol=random.choice(protocols),
        bytes_transferred=random.randint(1000, 1000000),
        packets=random.randint(10, 10000)
    )
    
    db.session.add(anomaly)
    db.session.commit()
    
    return anomaly

def monitoring_loop(socketio):
    """Main monitoring loop"""
    global monitoring_active
    
    print("🔍 Starting monitoring service...")
    
    traffic_counter = 0
    anomaly_counter = 0
    
    while monitoring_active:
        try:
            # Generate traffic data every 2 seconds
            if traffic_counter % 2 == 0:
                traffic = generate_mock_traffic_data()
                emit_traffic_update(traffic.to_dict())
            
            # Generate anomaly data every 10-30 seconds randomly
            if anomaly_counter >= random.randint(10, 30):
                if random.random() > 0.3:  # 70% chance to generate anomaly
                    anomaly = generate_mock_anomaly()
                    emit_anomaly(anomaly.to_dict())
                    
                    # Create alert for high/critical anomalies
                    if anomaly.severity in ['high', 'critical']:
                        from models.alert import Alert
                        from database import db
                        
                        alert = Alert(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.utcnow(),
                            severity=anomaly.severity,
                            status='unread',
                            type=anomaly.type,
                            title=f"New {anomaly.severity} severity threat detected",
                            description=anomaly.description,
                            source_ip=anomaly.source_ip,
                            affected_systems=1,
                            requires_action=True,
                            anomaly_id=anomaly.id
                        )
                        db.session.add(alert)
                        db.session.commit()
                        
                        emit_alert(alert.to_dict())
                
                anomaly_counter = 0
            
            traffic_counter += 1
            anomaly_counter += 1
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(5)

def start_monitoring(socketio):
    """Start background monitoring service"""
    global monitoring_active, monitoring_thread
    
    if monitoring_active:
        print("⚠️  Monitoring service already running")
        return
    
    monitoring_active = True
    monitoring_thread = threading.Thread(target=monitoring_loop, args=(socketio,), daemon=True)
    monitoring_thread.start()
    
    print("✅ Monitoring service started")

def stop_monitoring():
    """Stop background monitoring service"""
    global monitoring_active
    
    monitoring_active = False
    print("⏹️  Monitoring service stopped")
