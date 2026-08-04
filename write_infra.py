import os

DOCKERFILE = '''FROM python:3.11-slim

# Create non-root user
RUN adduser --system --group appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn

# Copy app code
COPY app /app/app
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
'''

DOCKER_COMPOSE = '''version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://cache:6379
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks:
      - nextroute-net

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_DB=${POSTGRES_DB:-nextroute}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nextroute-net

  cache:
    image: redis:alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nextroute-net

volumes:
  pgdata:

networks:
  nextroute-net:
'''

GUNICORN_CONF = '''import multiprocessing

# Bind to 0.0.0.0 for Docker
bind = "0.0.0.0:8000"

# Uvicorn ASGI worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Dynamically calculate workers based on CPU cores
workers = multiprocessing.cpu_count() * 2 + 1

# Graceful timeout configurations
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
'''

CONFIG_PY = '''from __future__ import annotations
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
'''

TEST_API = '''import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

@pytest.fixture
def client():
    # Trigger lifespan manually in TestClient context
    with TestClient(app) as client:
        yield client

def test_health_check(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_search_routes_valid(client):
    payload = {
        "from_code": "MDU",
        "to_code": "SBC",
        "date": "2026-08-05",
        "mode": "DEFAULT"
    }
    response = client.post("/api/v1/search/routes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "journeys" in data
    assert "meta" in data

def test_search_routes_invalid_payload(client):
    payload = {
        "from_code": "MDU"
    }
    response = client.post("/api/v1/search/routes", json=payload)
    assert response.status_code == 422 # Pydantic validation error

def test_search_routes_empty(client):
    payload = {
        "from_code": "NON_EXISTENT",
        "to_code": "FAKE_STATION",
        "date": "2026-08-05",
        "mode": "DEFAULT"
    }
    response = client.post("/api/v1/search/routes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["journeys"]) == 0
'''

LOGGING_MW = '''from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s')
logger = logging.getLogger("nextroute")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        
        # Inject request_id into logging context via a thread-safe context var or simple dictionary trick if needed
        # For simplicity in V1, we'll format it directly.
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = req_id
            return record
        logging.setLogRecordFactory(record_factory)

        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Completed request: {request.method} {request.url.path} - Status: {response.status_code} - Latency: {process_time:.4f}s")
            response.headers["X-Request-ID"] = req_id
            return response
        except Exception as e:
            logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}", exc_info=True)
            raise e
'''

MAIN_PY_UPDATE = '''import json
from contextlib import asynccontextmanager
import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.infrastructure.database.connection import engine, create_tables
from app.infrastructure.graph.builder import GraphBuilder
from app.presentation.api.v1.search import router as search_router
from app.infrastructure.logging_middleware import StructuredLoggingMiddleware

logger = logging.getLogger("nextroute")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NextRoute Application")
    settings = get_settings()
    
    # Create tables
    await create_tables()
    
    # Initialize DB (Seed mock weights for dev)
    if settings.ENVIRONMENT == "dev":
        from patch_seed import seed_weights
        await seed_weights()

    # Build Graph
    start_time = time.time()
    builder = GraphBuilder()
    graph = await builder.build_graph()
    app.state.graph = graph
    app.state.settings = settings
    logger.info(f"Graph loaded in {time.time()-start_time:.2f}s with {graph.number_of_nodes()} nodes.")
    
    yield
    # Shutdown
    logger.info("Shutting down NextRoute Application")
    if engine:
        await engine.dispose()

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(StructuredLoggingMiddleware)
    
    app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
    
    @app.get("/api/v1/health/", tags=["System"])
    async def health_check():
        return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}
        
    return app

app = create_app()
'''

def write_files():
    # Docker
    with open('backend/Dockerfile', 'w', encoding='utf-8') as f:
        f.write(DOCKERFILE)
    with open('docker-compose.prod.yml', 'w', encoding='utf-8') as f:
        f.write(DOCKER_COMPOSE)
    with open('backend/gunicorn.conf.py', 'w', encoding='utf-8') as f:
        f.write(GUNICORN_CONF)
    
    # Backend Config & Middleware
    with open('backend/app/config.py', 'w', encoding='utf-8') as f:
        f.write(CONFIG_PY)
    with open('backend/app/infrastructure/logging_middleware.py', 'w', encoding='utf-8') as f:
        f.write(LOGGING_MW)
    with open('backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(MAIN_PY_UPDATE)
        
    # Backend Tests
    os.makedirs('backend/tests/api', exist_ok=True)
    with open('backend/tests/api/test_integration.py', 'w', encoding='utf-8') as f:
        f.write(TEST_API)
        
    print("Backend infrastructure and tests generated successfully.")

if __name__ == "__main__":
    write_files()
