from __future__ import annotations
from fastapi import APIRouter, Request, HTTPException
from app.presentation.schemas.journey import JourneyDetailSchema

router = APIRouter(tags=["Journey"])

@router.get("/journey/{journey_id}", response_model=JourneyDetailSchema)
async def get_journey(request: Request, journey_id: str):
    cache = getattr(request.app.state, "journey_cache", {})
    if journey_id not in cache:
        raise HTTPException(status_code=404, detail="Journey not found")
    return cache[journey_id]
