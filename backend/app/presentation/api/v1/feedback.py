from __future__ import annotations
from fastapi import APIRouter
from app.presentation.schemas.feedback import FeedbackCreateSchema, FeedbackStatsSchema

router = APIRouter(tags=["Feedback"])

@router.post("/feedback")
async def submit_feedback(body: FeedbackCreateSchema):
    return {"status": "ok"}

@router.get("/feedback/stats/{route_hash}", response_model=FeedbackStatsSchema)
async def get_feedback_stats(route_hash: str):
    return FeedbackStatsSchema(route_hash=route_hash, avg_overall=5.0, avg_comfort=5.0, avg_safety=5.0, avg_accuracy=5.0, recommend_pct=100.0, total_count=1)
