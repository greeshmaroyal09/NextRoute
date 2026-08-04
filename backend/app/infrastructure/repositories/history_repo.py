from __future__ import annotations
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.domain.interfaces.repositories import ISearchHistoryRepository, ISavedRouteRepository
from app.infrastructure.database.models import SearchHistory, SavedRoute

class SearchHistoryRepository(ISearchHistoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, data: Any) -> Any:
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def get_recent(self, session_id: str, limit: int) -> list[Any]:
        stmt = select(SearchHistory).where(SearchHistory.session_id == session_id).order_by(SearchHistory.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class SavedRouteRepository(ISavedRouteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, data: Any) -> Any:
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def get_all(self, session_id: str) -> list[Any]:
        stmt = select(SavedRoute).where(SavedRoute.session_id == session_id).order_by(SavedRoute.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def toggle_favourite(self, id: str) -> bool:
        stmt = select(SavedRoute).where(SavedRoute.id == int(id))
        result = await self.session.execute(stmt)
        route = result.scalar_one_or_none()
        if route:
            route.is_favourite = not route.is_favourite
            await self.session.commit()
            return True
        return False

    async def delete(self, id: str) -> bool:
        stmt = delete(SavedRoute).where(SavedRoute.id == int(id))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
