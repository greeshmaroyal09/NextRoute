from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(tags=["History"])

@router.get("/history/recent")
async def get_recent_history(session_id: str, limit: int = 10):
    return []

@router.post("/routes/save")
async def save_route():
    return {"status": "ok"}

@router.get("/routes/saved")
async def get_saved_routes(session_id: str):
    return []

@router.put("/routes/{id}/favourite")
async def toggle_favourite(id: str):
    return {"status": "ok"}

@router.delete("/routes/{id}")
async def delete_route(id: str):
    return {"status": "ok"}
