from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def submit_feedback(data: dict):
    return {"status": "success"}


@router.get("/stats/{route_hash}")
async def get_feedback_stats(route_hash: str):
    return {
        "route_hash": route_hash,
        "average_rating": 4.5,
        "total_reviews": 12,
        "safety_score_avg": 4.8,
        "comfort_score_avg": 4.2,
    }
