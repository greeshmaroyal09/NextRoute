from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from datetime import date
from app.domain.entities.station import Station
from app.domain.entities.route import TrainRoute, BusRoute
from app.domain.value_objects.enums import SeatStatus

class IStationRepository(ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> Station | None:
        pass

    @abstractmethod
    async def get_nearby(self, lat: float, lon: float, radius_km: float) -> list[Station]:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int) -> list[Station]:
        pass

    @abstractmethod
    async def list_by_state(self, state: str) -> list[Station]:
        pass

class ITrainRouteRepository(ABC):
    @abstractmethod
    async def get_stops_between(self, from_code: str, to_code: str) -> list[Any]:
        pass

    @abstractmethod
    async def get_by_number(self, train_number: str) -> TrainRoute | None:
        pass

    @abstractmethod
    async def list_routes_through_station(self, station_code: str) -> list[TrainRoute]:
        pass

class IBusRouteRepository(ABC):
    @abstractmethod
    async def get_routes_between(self, from_code: str, to_code: str) -> list[BusRoute]:
        pass

    @abstractmethod
    async def get_by_operator(self, operator: str) -> list[BusRoute]:
        pass

class ISearchHistoryRepository(ABC):
    @abstractmethod
    async def save(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def get_recent(self, session_id: str, limit: int) -> list[Any]:
        pass

class ISavedRouteRepository(ABC):
    @abstractmethod
    async def save(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def get_all(self, session_id: str) -> list[Any]:
        pass

    @abstractmethod
    async def toggle_favourite(self, id: str) -> bool:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

class IFeedbackRepository(ABC):
    @abstractmethod
    async def save(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def get_stats_by_route_hash(self, route_hash: str) -> Any:
        pass

class IAvailabilityProvider(ABC):
    @abstractmethod
    async def get_availability(self, train_number: str, from_code: str, to_code: str, travel_date: date, travel_class: str) -> SeatStatus:
        pass
