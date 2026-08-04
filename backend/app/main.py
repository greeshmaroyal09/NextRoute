from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.infrastructure.database.connection import create_tables
from app.infrastructure.graph.builder import GraphBuilder
from app.infrastructure.database.connection import async_sessionmaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    app.state.graph = None

app = FastAPI(
    title=get_settings().APP_NAME,
    version=get_settings().APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"message": "Internal server error"})
