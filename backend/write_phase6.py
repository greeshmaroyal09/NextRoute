import os

DB_CONNECTION = '''from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.infrastructure.database.models import Base

settings = get_settings()

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
'''

CACHE_PROVIDER = '''import json
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
'''

RATE_LIMITER = '''import time
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self._ip_history = {}

    def check(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up old
        history = self._ip_history.get(client_ip, [])
        history = [t for t in history if now - t < 60]
        
        if len(history) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
            
        history.append(now)
        self._ip_history[client_ip] = history
        return True
        
rate_limiter = RateLimiter(requests_per_minute=20)
'''

def apply_phase6():
    with open('app/infrastructure/database/connection.py', 'w', encoding='utf-8') as f:
        f.write(DB_CONNECTION)
    with open('app/infrastructure/providers/cache.py', 'w', encoding='utf-8') as f:
        f.write(CACHE_PROVIDER)
    with open('app/infrastructure/rate_limiter.py', 'w', encoding='utf-8') as f:
        f.write(RATE_LIMITER)
    print("Applied DB, Cache, and Rate Limiter")

if __name__ == "__main__":
    apply_phase6()
