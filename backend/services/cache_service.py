"""
Redis cache service
"""
import redis
from config import Config
import json
import socket

class CacheService:
    """Redis cache service"""
    
    def __init__(self):
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """Connect to Redis with fast timeout"""
        try:
            # Set short timeout to avoid blocking on connection
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=1,  # 1 second timeout
                socket_timeout=1,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Quick ping with timeout
            self.redis_client.ping()
            print("✅ Connected to Redis")
        except (redis.ConnectionError, redis.TimeoutError, socket.timeout, ConnectionRefusedError) as e:
            print(f"❌ Redis connection error: {e}")
            print("ℹ️  Using in-memory cache fallback")
            self.redis_client = None
        except Exception as e:
            print(f"❌ Redis error: {e}")
            self.redis_client = None
    
    def get(self, key):
        """Get value from cache"""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"❌ Redis get error: {e}")
            return None
    
    def set(self, key, value, expiration=None):
        """Set value in cache"""
        if not self.redis_client:
            return False
        try:
            value_json = json.dumps(value)
            if expiration:
                self.redis_client.setex(key, expiration, value_json)
            else:
                self.redis_client.set(key, value_json)
            return True
        except Exception as e:
            print(f"❌ Redis set error: {e}")
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"❌ Redis delete error: {e}")
            return False
    
    def ping(self):
        """Ping Redis to check connection"""
        if not self.redis_client:
            return False
        try:
            return self.redis_client.ping()
        except:
            return False

# Global cache instance
cache = CacheService()
