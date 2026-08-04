from __future__ import annotations
from fastapi import APIRouter, Request
from app.presentation.schemas.station import StationSchema

router = APIRouter(tags=["Stations"])

@router.get("/stations", response_model=list[StationSchema])
async def list_stations(request: Request, state: str | None = None, limit: int = 10, offset: int = 0):
    return []

@router.get("/stations/{code}", response_model=StationSchema)
async def get_station(request: Request, code: str):
    return StationSchema(id="1", code=code, name="Example", city="City", state="State", latitude=0.0, longitude=0.0, station_type="TRAIN")
