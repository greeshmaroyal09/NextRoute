from __future__ import annotations
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.interfaces.repositories import ITrainRouteRepository, IBusRouteRepository
from app.domain.entities.route import TrainRoute, BusRoute
from app.infrastructure.database.models import TrainRoute as TrainRouteModel, TrainStop, Station, BusRoute as BusRouteModel, BusStopSequence, BusStop

class TrainRouteRepository(ITrainRouteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_stops_between(self, from_code: str, to_code: str) -> list[Any]:
        stmt = select(TrainStop, Station).join(Station, TrainStop.station_id == Station.id).order_by(TrainStop.stop_sequence)
        result = await self.session.execute(stmt)
        return list(result.all())

    async def get_by_number(self, train_number: str) -> TrainRoute | None:
        stmt = select(TrainRouteModel).where(TrainRouteModel.train_number == train_number)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return TrainRoute(
            id=model.id,
            train_number=model.train_number,
            train_name=model.train_name,
            train_type=model.train_type,
            runs_on=model.runs_on
        )

    async def list_routes_through_station(self, station_code: str) -> list[TrainRoute]:
        stmt = select(TrainRouteModel).join(TrainStop, TrainRouteModel.id == TrainStop.train_route_id).join(Station, TrainStop.station_id == Station.id).where(Station.code == station_code)
        result = await self.session.execute(stmt)
        return [
            TrainRoute(
                id=model.id,
                train_number=model.train_number,
                train_name=model.train_name,
                train_type=model.train_type,
                runs_on=model.runs_on
            ) for model in result.scalars().all()
        ]

class BusRouteRepository(IBusRouteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_routes_between(self, from_code: str, to_code: str) -> list[BusRoute]:
        return []

    async def get_by_operator(self, operator: str) -> list[BusRoute]:
        stmt = select(BusRouteModel).where(BusRouteModel.operator == operator)
        result = await self.session.execute(stmt)
        return [
            BusRoute(
                id=m.id,
                route_number=m.route_number,
                operator=m.operator,
                bus_type=m.bus_type,
                frequency_minutes=m.frequency_minutes
            ) for m in result.scalars().all()
        ]
