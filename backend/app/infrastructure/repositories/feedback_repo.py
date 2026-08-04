from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories import IFeedbackRepository
from app.infrastructure.database.models import JourneyFeedback


class FeedbackRepository(IFeedbackRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, data: Any) -> Any:
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def get_stats_by_route_hash(self, route_hash: str) -> Any:
        stmt = select(
            func.count(JourneyFeedback.id).label("count"),
            func.avg(JourneyFeedback.would_recommend.cast(func.integer)).label(
                "recommendation_rate"
            ),
        ).where(JourneyFeedback.route_hash == route_hash)
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        if not row:
            return {"count": 0, "recommendation_rate": 0.0}
        return {
            "count": row.count,
            "recommendation_rate": float(row.recommendation_rate or 0.0),
        }
