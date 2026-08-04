from fastapi import APIRouter, HTTPException
from app.presentation.schemas.journey import JourneyResponse

router = APIRouter()

@router.get("/{journey_id}")
async def get_journey_detail(journey_id: str):
    # In a real app this would query a cache or database
    raise HTTPException(status_code=404, detail="Journey not found in cache")
