from pydantic import BaseModel
from typing import Optional, List

class StationInfo(BaseModel):
    id: str
    code: str
    name: str
    city: Optional[str]
    state: str
    type: str
    lat: float
    lon: float

class StationListResponse(BaseModel):
    stations: List[StationInfo]
    bus_stops: List[StationInfo]
