import os

base_dir = r"c:\Users\thispc\Downloads\NextRoute\backend"

files = {}

files["app/domain/value_objects/enums.py"] = """
from enum import Enum

class StationType(str, Enum):
    MAJOR_JUNCTION = "MAJOR_JUNCTION"
    JUNCTION = "JUNCTION"
    REGULAR = "REGULAR"
    HALT = "HALT"

class TrainType(str, Enum):
    EXPRESS = "EXPRESS"
    SUPERFAST = "SUPERFAST"
    MAIL = "MAIL"
    PASSENGER = "PASSENGER"
    RAJDHANI = "RAJDHANI"
    SHATABDI = "SHATABDI"
    GARIB_RATH = "GARIB_RATH"
    LOCAL = "LOCAL"

class TravelClass(str, Enum):
    GENERAL = "GENERAL"
    SLEEPER = "SLEEPER"
    AC_3 = "AC_3"
    AC_2 = "AC_2"
    AC_1 = "AC_1"

class BusOperator(str, Enum):
    APSRTC = "APSRTC"
    TSRTC = "TSRTC"
    TNSTC = "TNSTC"
    KSRTC = "KSRTC"

class BusType(str, Enum):
    ORDINARY = "ORDINARY"
    EXPRESS = "EXPRESS"
    SUPER_LUXURY = "SUPER_LUXURY"
    SLEEPER = "SLEEPER"

class SeatStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RAC = "RAC"
    WL_1_TO_10 = "WL_1_TO_10"
    WL_11_TO_30 = "WL_11_TO_30"
    WL_30_PLUS = "WL_30_PLUS"
    UNAVAILABLE = "UNAVAILABLE"

class TransferType(str, Enum):
    STATION_TO_STATION = "STATION_TO_STATION"
    STATION_TO_BUS = "STATION_TO_BUS"
    BUS_TO_STATION = "BUS_TO_STATION"
    BUS_TO_BUS = "BUS_TO_BUS"

class TravelMode(str, Enum):
    DEFAULT = "DEFAULT"
    WOMEN = "WOMEN"
    SENIOR = "SENIOR"
    STUDENT = "STUDENT"
    FAMILY = "FAMILY"

class TransportType(str, Enum):
    TRAIN = "TRAIN"
    BUS = "BUS"
    WALK = "WALK"
    WAIT = "WAIT"

class TransferDifficulty(str, Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    DIFFICULT = "DIFFICULT"

class LightingQuality(str, Enum):
    WELL_LIT = "WELL_LIT"
    MODERATE = "MODERATE"
    POOR = "POOR"
    UNKNOWN = "UNKNOWN"

class CrowdLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"

class DatasetStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    GRAPH_BUILDING = "GRAPH_BUILDING"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ROLLED_BACK = "ROLLED_BACK"
    REJECTED = "REJECTED"
"""

files["app/domain/value_objects/coordinate.py"] = """
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2

@dataclass
class Coordinate:
    lat: float
    lon: float

    def haversine_distance(self, other: 'Coordinate') -> float:
        R = 6371.0
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        lat2 = radians(other.lat)
        lon2 = radians(other.lon)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
"""

files["app/domain/value_objects/money.py"] = """
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Money:
    amount_inr: Decimal
"""

files["app/domain/entities/station.py"] = """
from dataclasses import dataclass
from typing import Optional
from app.domain.value_objects.enums import StationType
from app.domain.value_objects.coordinate import Coordinate

@dataclass
class Station:
    id: str
    code: str
    name: str
    city: str
    state: str
    lat: float
    lon: float
    station_type: StationType
    zone: Optional[str] = None
    
    @property
    def coordinate(self) -> Coordinate:
        return Coordinate(lat=self.lat, lon=self.lon)
"""

files["app/domain/entities/route.py"] = """
from dataclasses import dataclass
from typing import List, Optional
from app.domain.value_objects.enums import TrainType, BusOperator, BusType

@dataclass
class TrainRoute:
    train_number: str
    name: str
    type: TrainType
    runs_on: List[int]

@dataclass
class BusRoute:
    route_id: str
    operator: BusOperator
    type: BusType
    name: str
"""

files["app/domain/entities/journey.py"] = """
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from app.domain.value_objects.enums import TransportType, TravelClass
from app.domain.value_objects.money import Money

@dataclass
class JourneySegment:
    type: TransportType
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    duration: float
    cost: Money
    class_type: Optional[TravelClass] = None
    route_id: Optional[str] = None

@dataclass
class Journey:
    segments: List[JourneySegment]
    total_duration: float
    total_cost: Money
    transfers: int
"""

files["app/domain/entities/user.py"] = """
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    name: Optional[str] = None
"""

files["app/domain/interfaces/repositories.py"] = """
from abc import ABC, abstractmethod
from typing import List, Optional

class IStationRepository(ABC):
    @abstractmethod
    async def get_by_code(self, code: str):
        pass

    @abstractmethod
    async def get_nearby(self, lat: float, lon: float, radius: float):
        pass

    @abstractmethod
    async def search(self, query: str):
        pass

    @abstractmethod
    async def list_all(self):
        pass

class ITrainRouteRepository(ABC):
    @abstractmethod
    async def get_stops_between(self, src: str, dst: str):
        pass

    @abstractmethod
    async def get_by_number(self, number: str):
        pass

class IBusRouteRepository(ABC):
    @abstractmethod
    async def get_routes_between(self, src: str, dst: str):
        pass

class ISearchHistoryRepository(ABC):
    @abstractmethod
    async def save(self, history):
        pass

    @abstractmethod
    async def get_recent(self, user_id: str, limit: int = 10):
        pass

class ISavedRouteRepository(ABC):
    @abstractmethod
    async def save(self, route):
        pass

    @abstractmethod
    async def get_all(self, user_id: str):
        pass

    @abstractmethod
    async def toggle_favourite(self, user_id: str, route_id: str):
        pass

    @abstractmethod
    async def delete(self, user_id: str, route_id: str):
        pass

class IFeedbackRepository(ABC):
    @abstractmethod
    async def save(self, feedback):
        pass

    @abstractmethod
    async def get_stats_by_route_hash(self, route_hash: str):
        pass
"""

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n" if content else "")

print("Domain files generated.")
