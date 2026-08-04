import json
import time
from typing import Optional

class ICacheRepository:
    def get(self, key: str) -> Optional[str]:
        raise NotImplementedError
    def set(self, key: str, value: str, ttl: int):
        raise NotImplementedError

class MemoryCacheRepository(ICacheRepository):
    def __init__(self):
        self._cache = {}
        
    def get(self, key: str) -> Optional[str]:
        item = self._cache.get(key)
        if item and item['expires'] > time.time():
            return item['value']
        return None
        
    def set(self, key: str, value: str, ttl: int):
        self._cache[key] = {'value': value, 'expires': time.time() + ttl}

class RedisCacheRepository(ICacheRepository):
    def __init__(self, redis_url: str):
        import redis
        self._redis = redis.from_url(redis_url, decode_responses=True)
        
    def get(self, key: str) -> Optional[str]:
        try:
            return self._redis.get(key)
        except Exception:
            return None
            
    def set(self, key: str, value: str, ttl: int):
        try:
            self._redis.setex(key, ttl, value)
        except Exception:
            pass

def get_cache(redis_url: str = None) -> ICacheRepository:
    if redis_url and redis_url.startswith("redis"):
        try:
            return RedisCacheRepository(redis_url)
        except Exception:
            return MemoryCacheRepository()
    return MemoryCacheRepository()
