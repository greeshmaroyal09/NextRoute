from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.domain.interfaces.repositories import IStationRepository
from app.domain.entities.station import Station as StationEntity
from app.infrastructure.database.models import Station as StationModel
from app.domain.value_objects.coordinate import Coordinate

class StationRepository(IStationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: StationModel) -> StationEntity:
        return StationEntity(
            id=model.id,
            code=model.code,
            name=model.name,
            city=model.city,
            state=model.state,
            latitude=model.latitude,
            longitude=model.longitude,
            station_type=model.station_type,
            zone=model.zone
        )

    async def get_by_code(self, code: str) -> StationEntity | None:
        stmt = select(StationModel).where(StationModel.code == code)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_nearby(self, lat: float, lon: float, radius_km: float) -> list[StationEntity]:
        stmt = select(StationModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        target = Coordinate(lat, lon)
        nearby = []
        for model in models:
            coord = Coordinate(model.latitude, model.longitude)
            if target.haversine_distance(coord) <= radius_km:
                nearby.append(self._to_entity(model))
        return nearby

    async def search(self, query: str, limit: int) -> list[StationEntity]:
        stmt = select(StationModel).where(
            or_(
                StationModel.name.ilike(f"%{query}%"),
                StationModel.code.ilike(f"%{query}%")
            )
        ).limit(limit)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_state(self, state: str) -> list[StationEntity]:
        stmt = select(StationModel).where(StationModel.state == state)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
