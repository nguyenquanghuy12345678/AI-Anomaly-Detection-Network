"""
Zabbix integration service
"""
from pyzabbix import ZabbixAPI
from config import Config
import logging

class ZabbixService:
    """Zabbix API integration service"""
    
    def __init__(self):
        self.zabbix = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Connect to Zabbix API"""
        try:
            self.zabbix = ZabbixAPI(Config.ZABBIX_API_URL)
            self.zabbix.login(Config.ZABBIX_USER, Config.ZABBIX_PASSWORD)
            self.connected = True
            print("✅ Connected to Zabbix API")
        except Exception as e:
            print(f"⚠️  Zabbix connection error: {e}")
            print("ℹ️  Zabbix integration will be disabled until connection is established")
            self.connected = False
    
    def get_hosts(self):
        """Get all monitored hosts"""
        if not self.connected:
            return []
        try:
            hosts = self.zabbix.host.get(output=['hostid', 'host', 'name', 'status'])
            return hosts
        except Exception as e:
            print(f"❌ Zabbix get hosts error: {e}")
            return []
    
    def get_host_metrics(self, host_id):
        """Get metrics for a specific host"""
        if not self.connected:
            return {}
        try:
            items = self.zabbix.item.get(
                hostids=host_id,
                output=['itemid', 'name', 'lastvalue', 'units']
            )
            return items
        except Exception as e:
            print(f"❌ Zabbix get metrics error: {e}")
            return {}
    
    def get_network_traffic(self, host_id):
        """Get network traffic data from Zabbix"""
        if not self.connected:
            return None
        try:
            # Get network interface items
            items = self.zabbix.item.get(
                hostids=host_id,
                search={'key_': 'net.if'},
                output=['itemid', 'name', 'lastvalue', 'key_']
            )
            
            traffic_data = {
                'incoming': 0,
                'outgoing': 0
            }
            
            for item in items:
                if 'in' in item['key_'].lower():
                    traffic_data['incoming'] += float(item.get('lastvalue', 0))
                elif 'out' in item['key_'].lower():
                    traffic_data['outgoing'] += float(item.get('lastvalue', 0))
            
            return traffic_data
        except Exception as e:
            print(f"❌ Zabbix get traffic error: {e}")
            return None
    
    def get_alerts(self):
        """Get active alerts/triggers from Zabbix"""
        if not self.connected:
            return []
        try:
            triggers = self.zabbix.trigger.get(
                only_true=True,
                skipDependent=True,
                monitored=True,
                active=True,
                output=['triggerid', 'description', 'priority', 'lastchange'],
                expandDescription=True
            )
            return triggers
        except Exception as e:
            print(f"❌ Zabbix get alerts error: {e}")
            return []
    
    def create_trigger(self, expression, description, priority=3):
        """Create a new trigger in Zabbix"""
        if not self.connected:
            return None
        try:
            trigger = self.zabbix.trigger.create(
                expression=expression,
                description=description,
                priority=priority
            )
            return trigger
        except Exception as e:
            print(f"❌ Zabbix create trigger error: {e}")
            return None
    
    def get_system_status(self):
        """Get Zabbix system status"""
        if not self.connected:
            return {'status': 'offline', 'message': 'Not connected to Zabbix'}
        try:
            # Get API info
            api_info = self.zabbix.apiinfo.version()
            return {
                'status': 'online',
                'version': api_info,
                'connected': True
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'connected': False
            }

# Global Zabbix service instance
zabbix_service = ZabbixService()
