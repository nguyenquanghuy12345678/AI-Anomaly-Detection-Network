"""
Real Network Data Capture Service
Thu thập dữ liệu THẬT từ network interface
"""
import psutil
import threading
import time
from datetime import datetime
from collections import defaultdict
import socket
from scapy.all import sniff, IP, TCP, UDP, ICMP
from flask import current_app

class RealNetworkService:
    """Service để capture dữ liệu mạng thật"""
    
    def __init__(self):
        self.capturing = False
        self.capture_thread = None
        self.stats = defaultdict(int)
        self.connections_cache = []
        self.interface = None
        
    def get_network_interfaces(self):
        """Lấy danh sách network interfaces"""
        interfaces = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces.append({
                        'name': iface,
                        'ip': addr.address,
                        'netmask': addr.netmask
                    })
        return interfaces
    
    def get_real_connections(self):
        """Lấy danh sách connections THẬT từ hệ thống"""
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' or conn.status == 'LISTENING':
                    try:
                        # Lấy thông tin process
                        process_name = "Unknown"
                        if conn.pid:
                            try:
                                process = psutil.Process(conn.pid)
                                process_name = process.name()
                            except:
                                pass
                        
                        local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                        remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                        
                        connections.append({
                            'local_address': local_addr,
                            'remote_address': remote_addr,
                            'status': conn.status,
                            'protocol': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                            'pid': conn.pid,
                            'process': process_name
                        })
                    except:
                        continue
        except Exception as e:
            print(f"❌ Error getting real connections: {e}")
        
        return connections
    
    def get_real_network_stats(self):
        """Lấy thống kê mạng THẬT"""
        try:
            # Network I/O counters
            net_io = psutil.net_io_counters()
            
            # Active connections count
            active_conns = len([c for c in psutil.net_connections() 
                              if c.status == 'ESTABLISHED'])
            
            # Convert bytes to Mbps (approximate)
            bytes_sent_mb = net_io.bytes_sent / (1024 * 1024)
            bytes_recv_mb = net_io.bytes_recv / (1024 * 1024)
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout,
                'active_connections': active_conns,
                'bytes_sent_mb': round(bytes_sent_mb, 2),
                'bytes_recv_mb': round(bytes_recv_mb, 2)
            }
        except Exception as e:
            print(f"❌ Error getting network stats: {e}")
            return {}
    
    def packet_callback(self, packet):
        """Callback khi capture được packet"""
        try:
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                
                # Protocol detection
                protocol = "OTHER"
                src_port = 0
                dst_port = 0
                
                if TCP in packet:
                    protocol = "TCP"
                    src_port = packet[TCP].sport
                    dst_port = packet[TCP].dport
                    self.stats['tcp'] += 1
                    
                    # Check for specific services
                    if dst_port == 80 or src_port == 80:
                        self.stats['http'] += 1
                    elif dst_port == 443 or src_port == 443:
                        self.stats['https'] += 1
                    elif dst_port == 22 or src_port == 22:
                        self.stats['ssh'] += 1
                    elif dst_port == 21 or src_port == 21:
                        self.stats['ftp'] += 1
                        
                elif UDP in packet:
                    protocol = "UDP"
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport
                    self.stats['udp'] += 1
                    
                elif ICMP in packet:
                    protocol = "ICMP"
                    self.stats['icmp'] += 1
                
                self.stats['total_packets'] += 1
                self.stats['total_bytes'] += len(packet)
                
                # Store packet info (limited to prevent memory issues)
                if len(self.connections_cache) < 1000:
                    self.connections_cache.append({
                        'timestamp': datetime.utcnow(),
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'src_port': src_port,
                        'dst_port': dst_port,
                        'protocol': protocol,
                        'size': len(packet)
                    })
                    
        except Exception as e:
            print(f"⚠️ Packet processing error: {e}")
    
    def start_capture(self, interface=None, filter_str=""):
        """Bắt đầu capture packets (requires admin/root)"""
        if self.capturing:
            print("⚠️ Already capturing")
            return False
        
        try:
            self.capturing = True
            self.interface = interface
            
            print(f"🔍 Starting packet capture on interface: {interface or 'default'}")
            print("⚠️ Note: Requires administrator/root privileges")
            
            # Start capture in background thread
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                args=(interface, filter_str),
                daemon=True
            )
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start capture: {e}")
            self.capturing = False
            return False
    
    def _capture_loop(self, interface, filter_str):
        """Main capture loop"""
        try:
            sniff(
                iface=interface,
                prn=self.packet_callback,
                filter=filter_str,
                store=0,  # Don't store packets in memory
                stop_filter=lambda x: not self.capturing
            )
        except PermissionError:
            print("❌ Permission denied. Run as administrator/root to capture packets.")
            self.capturing = False
        except Exception as e:
            print(f"❌ Capture error: {e}")
            self.capturing = False
    
    def stop_capture(self):
        """Dừng packet capture"""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        print("⏹️ Packet capture stopped")
    
    def get_capture_stats(self):
        """Lấy thống kê từ packet capture"""
        total = self.stats['total_packets']
        
        return {
            'total_packets': total,
            'total_bytes': self.stats['total_bytes'],
            'tcp_packets': self.stats['tcp'],
            'udp_packets': self.stats['udp'],
            'icmp_packets': self.stats['icmp'],
            'http_packets': self.stats['http'],
            'https_packets': self.stats['https'],
            'ssh_packets': self.stats['ssh'],
            'ftp_packets': self.stats['ftp'],
            'tcp_percentage': round(self.stats['tcp'] / total * 100, 2) if total > 0 else 0,
            'udp_percentage': round(self.stats['udp'] / total * 100, 2) if total > 0 else 0,
            'capturing': self.capturing,
            'interface': self.interface
        }
    
    def reset_stats(self):
        """Reset tất cả thống kê"""
        self.stats.clear()
        self.connections_cache.clear()
        print("📊 Statistics reset")

# Global instance
real_network_service = RealNetworkService()
