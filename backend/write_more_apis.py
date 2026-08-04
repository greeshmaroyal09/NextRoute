API_JOURNEY = """from fastapi import APIRouter, HTTPException
from app.presentation.schemas.journey import JourneyResponse

router = APIRouter()

@router.get("/{journey_id}")
async def get_journey_detail(journey_id: str):
    # In a real app this would query a cache or database
    raise HTTPException(status_code=404, detail="Journey not found in cache")
"""

API_HISTORY = """from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

@router.get("/recent")
async def get_recent_history(session_id: str):
    return {"history": []}

@router.post("/save")
async def save_route(session_id: str, route_data: Dict):
    return {"status": "success", "id": "123"}

@router.get("/saved")
async def get_saved_routes(session_id: str):
    return {"saved_routes": []}

@router.put("/{route_id}/favourite")
async def toggle_favourite(route_id: str):
    return {"status": "success", "favourite": True}

@router.delete("/{route_id}")
async def delete_saved_route(route_id: str):
    return {"status": "deleted"}
"""

API_FEEDBACK = """from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.post("/")
async def submit_feedback(data: Dict):
    return {"status": "success"}

@router.get("/stats/{route_hash}")
async def get_feedback_stats(route_hash: str):
    return {
        "route_hash": route_hash,
        "average_rating": 4.5,
        "total_reviews": 12,
        "safety_score_avg": 4.8,
        "comfort_score_avg": 4.2
    }
"""

API_STATIONS = """from fastapi import APIRouter, Request
from app.presentation.schemas.station import StationListResponse, StationInfo
from sqlalchemy import select
from app.infrastructure.database.models import Station, BusStop
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/autocomplete")
async def autocomplete_stations(q: str):
    # Simplified mock for API
    return {"suggestions": [
        {"code": "SBC", "name": "KSR Bengaluru", "type": "TRAIN", "state": "KA"},
        {"code": "MDU", "name": "Madurai Junction", "type": "TRAIN", "state": "TN"}
    ]}

@router.get("/nearby")
async def get_nearby_stations(lat: float, lon: float, radius_km: float = 30.0):
    return {"stations": [], "bus_stops": []}

@router.get("/")
async def list_stations():
    return {"stations": []}
"""

MAIN_PY = """from fastapi import FastAPI
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
"""


def write_files():
    with open("app/presentation/api/v1/journey.py", "w") as f:
        f.write(API_JOURNEY)
    with open("app/presentation/api/v1/history.py", "w") as f:
        f.write(API_HISTORY)
    with open("app/presentation/api/v1/feedback.py", "w") as f:
        f.write(API_FEEDBACK)
    with open("app/presentation/api/v1/stations.py", "w") as f:
        f.write(API_STATIONS)
    with open("app/main.py", "w") as f:
        f.write(MAIN_PY)
    print("Additional APIs and main.py written.")


if __name__ == "__main__":
    write_files()
