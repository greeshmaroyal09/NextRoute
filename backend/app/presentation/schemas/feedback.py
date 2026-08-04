from __future__ import annotations

from pydantic import BaseModel


class FeedbackCreateSchema(BaseModel):
    route_hash: str
    overall_rating: int
    comfort_rating: int
    safety_rating: int
    accuracy_rating: int
    would_recommend: bool
    comments: str | None = None


class FeedbackStatsSchema(BaseModel):
    route_hash: str
    avg_overall: float
    avg_comfort: float
    avg_safety: float
    avg_accuracy: float
    recommend_pct: float
    total_count: int
