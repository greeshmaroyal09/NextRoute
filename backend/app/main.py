import json
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
    # Database is persistent; skip automatic seeding in lifespan to avoid test crashes.

    # Build Graph
    start_time = time.time()
    builder = GraphBuilder()
    from app.infrastructure.database.connection import async_session
    async with async_session() as session:
        graph = await builder.build_from_database(session)
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
