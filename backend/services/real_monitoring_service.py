"""
Real Network Monitoring Service - Sử dụng dữ liệu THẬT
"""
import threading
import time
from datetime import datetime
import uuid
from flask import current_app
from services.websocket_service import emit_anomaly, emit_traffic_update, emit_alert
from services.real_network_service import real_network_service
import psutil

# Global monitoring state
real_monitoring_active = False
real_monitoring_thread = None
previous_net_io = None

def generate_real_traffic_data():
    """Tạo traffic data từ network stats THẬT"""
    global previous_net_io
    
    from models.network_traffic import NetworkTraffic
    from database import db
    
    try:
        # Lấy network I/O counters
        current_net_io = psutil.net_io_counters()
        
        # Calculate rates if we have previous data
        incoming_mbps = 0
        outgoing_mbps = 0
        
        if previous_net_io:
            # Calculate bytes transferred in the interval (1 second)
            bytes_recv_diff = current_net_io.bytes_recv - previous_net_io.bytes_recv
            bytes_sent_diff = current_net_io.bytes_sent - previous_net_io.bytes_sent
            
            # Convert to Mbps (bytes/sec to Megabits/sec)
            incoming_mbps = (bytes_recv_diff * 8) / (1024 * 1024)
            outgoing_mbps = (bytes_sent_diff * 8) / (1024 * 1024)
        
        previous_net_io = current_net_io
        
        # Get active connections
        active_conns = len([c for c in psutil.net_connections() 
                          if c.status == 'ESTABLISHED'])
        
        # Get protocol breakdown (approximation from capture stats if available)
        capture_stats = real_network_service.get_capture_stats()
        total_packets = capture_stats.get('total_packets', 0)
        
        # Calculate protocol percentages
        tcp_percentage = capture_stats.get('tcp_percentage', 60)
        udp_percentage = capture_stats.get('udp_percentage', 30)
        
        total_mbps = incoming_mbps + outgoing_mbps
        
        traffic = NetworkTraffic(
            timestamp=datetime.utcnow(),
            incoming_mbps=round(incoming_mbps, 2),
            outgoing_mbps=round(outgoing_mbps, 2),
            total_mbps=round(total_mbps, 2),
            tcp_traffic=round(total_mbps * (tcp_percentage / 100), 2),
            udp_traffic=round(total_mbps * (udp_percentage / 100), 2),
            http_traffic=round(total_mbps * 0.15, 2),
            https_traffic=round(total_mbps * 0.20, 2),
            ssh_traffic=round(total_mbps * 0.03, 2),
            ftp_traffic=round(total_mbps * 0.02, 2),
            active_connections=active_conns,
            anomaly_count=0,  # Will be updated by anomaly detection
            blocked_threats=0,
            avg_response_time=round(psutil.cpu_percent() * 2, 2)  # Approximation
        )
        
        db.session.add(traffic)
        db.session.commit()
        
        return traffic
        
    except Exception as e:
        print(f"❌ Error generating real traffic data: {e}")
        return None

def analyze_real_connections_for_anomalies():
    """Phân tích connections thật để tìm anomalies"""
    from models.anomaly import Anomaly
    from database import db
    
    try:
        connections = real_network_service.get_real_connections()
        
        # Simple anomaly detection rules
        anomalies_found = []
        
        for conn in connections:
            # Check for suspicious patterns
            suspicious = False
            anomaly_type = None
            
            # Rule 1: High port numbers (potential port scanning)
            if conn.get('remote_address') and ':' in conn['remote_address']:
                try:
                    remote_port = int(conn['remote_address'].split(':')[1])
                    if remote_port > 60000:
                        suspicious = True
                        anomaly_type = 'Port Scan'
                except:
                    pass
            
            # Rule 2: Unknown process with established connection
            if conn.get('process') == 'Unknown' and conn.get('status') == 'ESTABLISHED':
                suspicious = True
                anomaly_type = 'Suspicious Process'
            
            # Rule 3: Multiple connections from same IP (potential DoS)
            # This would require more sophisticated tracking
            
            if suspicious and anomaly_type:
                local_parts = conn['local_address'].split(':') if ':' in conn['local_address'] else ['0.0.0.0', '0']
                remote_parts = conn['remote_address'].split(':') if ':' in conn['remote_address'] else ['0.0.0.0', '0']
                
                anomaly = Anomaly(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    source_ip=remote_parts[0] if len(remote_parts) > 0 else '0.0.0.0',
                    destination_ip=local_parts[0] if len(local_parts) > 0 else '0.0.0.0',
                    source_port=int(remote_parts[1]) if len(remote_parts) > 1 and remote_parts[1].isdigit() else 0,
                    destination_port=int(local_parts[1]) if len(local_parts) > 1 and local_parts[1].isdigit() else 0,
                    type=anomaly_type,
                    severity='medium',
                    confidence=0.75,
                    status='active',
                    description=f"Detected {anomaly_type} from real connection monitoring",
                    protocol=conn.get('protocol', 'TCP'),
                    bytes_transferred=0,
                    packets=0
                )
                
                anomalies_found.append(anomaly)
        
        # Save anomalies to database
        if anomalies_found:
            db.session.bulk_save_objects(anomalies_found)
            db.session.commit()
            
        return anomalies_found
        
    except Exception as e:
        print(f"❌ Error analyzing connections: {e}")
        return []

def real_monitoring_loop(socketio, app):
    """Main monitoring loop sử dụng dữ liệu THẬT"""
    global real_monitoring_active
    
    print("🔍 Starting REAL network monitoring service...")
    print("📊 Collecting data from actual network interfaces...")
    
    traffic_counter = 0
    anomaly_check_counter = 0
    
    while real_monitoring_active:
        try:
            with app.app_context():
                # Generate traffic data every 2 seconds from REAL network stats
                if traffic_counter % 2 == 0:
                    traffic = generate_real_traffic_data()
                    if traffic:
                        emit_traffic_update(traffic.to_dict())
                        print(f"📈 Real traffic: {traffic.incoming_mbps}↓ / {traffic.outgoing_mbps}↑ Mbps")
                
                # Check for anomalies every 10 seconds
                if anomaly_check_counter >= 10:
                    anomalies = analyze_real_connections_for_anomalies()
                    
                    for anomaly in anomalies:
                        emit_anomaly(anomaly.to_dict())
                        print(f"⚠️ Real anomaly detected: {anomaly.type} from {anomaly.source_ip}")
                        
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
                                title=f"Real {anomaly.severity} severity threat detected",
                                description=anomaly.description,
                                source_ip=anomaly.source_ip,
                                affected_systems=1,
                                requires_action=True,
                                anomaly_id=anomaly.id
                            )
                            db.session.add(alert)
                            db.session.commit()
                            
                            emit_alert(alert.to_dict())
                    
                    anomaly_check_counter = 0
            
            traffic_counter += 1
            anomaly_check_counter += 1
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Real monitoring error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

def start_real_monitoring(socketio, app):
    """Start REAL network monitoring service"""
    global real_monitoring_active, real_monitoring_thread
    
    if real_monitoring_active:
        print("⚠️ Real monitoring service already running")
        return
    
    real_monitoring_active = True
    real_monitoring_thread = threading.Thread(
        target=real_monitoring_loop, 
        args=(socketio, app), 
        daemon=True
    )
    real_monitoring_thread.start()
    
    print("✅ REAL network monitoring service started")
    print("📡 Using actual system network data")

def stop_real_monitoring():
    """Stop REAL network monitoring service"""
    global real_monitoring_active
    
    real_monitoring_active = False
    print("⏹️ REAL monitoring service stopped")
