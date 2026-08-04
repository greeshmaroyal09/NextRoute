from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.presentation.api.v1 import search, journey, history, feedback, stations, health
from app.config import get_settings
from app.infrastructure.database.connection import get_session
from app.infrastructure.graph.builder import GraphBuilder

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build Graph on startup
    print("Building transport graph...")
    builder = GraphBuilder()
    async for session in get_session():
        graph = await builder.build_from_database(session)
        app.state.graph = graph
        break
    print(f"Graph loaded with {app.state.graph.number_of_nodes()} nodes.")
    yield
    print("Shutting down...")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(journey.router, prefix="/api/v1/journey", tags=["Journey"])
app.include_router(history.router, prefix="/api/v1/routes", tags=["History"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(stations.router, prefix="/api/v1/stations", tags=["Stations"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
