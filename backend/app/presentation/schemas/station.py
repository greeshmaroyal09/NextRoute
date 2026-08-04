from __future__ import annotations
from pydantic import BaseModel

class StationSchema(BaseModel):
    id: str
    code: str
    name: str
    city: str | None = None
    state: str | None = None
    latitude: float
    longitude: float
    station_type: str
    zone: str | None = None

class AutocompleteItem(BaseModel):
    code: str
    name: str
    station_type: str
    state: str | None = None
    type: str = 'TRAIN'

class AutocompleteResponse(BaseModel):
    suggestions: list[AutocompleteItem]

class NearbyResponse(BaseModel):
    stations: list[StationSchema]
    bus_stops: list[StationSchema]
