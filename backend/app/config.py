from __future__ import annotations
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "NextRoute"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./nextroute.db"
    REDIS_URL: str = "redis://localhost:6379"
    GRAPH_DATA_DIR: str = "data/graphs"
    NEARBY_RADIUS_KM: float = 30.0
    MAX_TRANSFERS: int = 3
    MIN_TRANSFER_BUFFER_MINS: int = 20
    K_SHORTEST_PATHS: int = 50
    SEARCH_RESULT_LIMIT: int = 10
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
