from pydantic import BaseModel


class StationInfo(BaseModel):
    id: str
    code: str
    name: str
    city: str | None
    state: str
    type: str
    lat: float
    lon: float


class StationListResponse(BaseModel):
    stations: list[StationInfo]
    bus_stops: list[StationInfo]
