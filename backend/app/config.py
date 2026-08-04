from __future__ import annotations
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    APP_NAME: str = "NextRoute"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    
    # Required for production
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: list[str]

    # App specific
    GRAPH_DATA_DIR: str = "data/graphs"
    NEARBY_RADIUS_KM: float = 30.0
    MAX_TRANSFERS: int = 3
    MIN_TRANSFER_BUFFER_MINS: int = 20
    K_SHORTEST_PATHS: int = 50
    SEARCH_RESULT_LIMIT: int = 10
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    # In 'dev', provide safe defaults if missing
    if os.getenv("ENVIRONMENT", "dev") == "dev":
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./nextroute.db")
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
        os.environ.setdefault("SECRET_KEY", "dev-secret-key-12345")
        os.environ.setdefault("CORS_ORIGINS", '["*"]')
        
    settings = Settings()
    
    # Strict Production Hardening
    if settings.ENVIRONMENT == "prod":
        if "sqlite" in settings.DATABASE_URL:
            raise ValueError("SQLite is strictly forbidden in production. Set a valid PostgreSQL DATABASE_URL.")
        if settings.SECRET_KEY == "dev-secret-key-12345":
            raise ValueError("SECRET_KEY cannot be default in production.")
        if "*" in settings.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS cannot allow '*' in production.")
            
    return settings
