from fastapi import APIRouter, Request
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
