from __future__ import annotations
from dataclasses import dataclass
from app.domain.value_objects.enums import StationType

@dataclass
class Station:
    id: str
    code: str
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    station_type: StationType
    zone: str | None = None

    @property
    def is_junction(self) -> bool:
        return "JN" in self.name.upper() or "JUNCTION" in self.name.upper()
