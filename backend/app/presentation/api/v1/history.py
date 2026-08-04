from fastapi import APIRouter

router = APIRouter()


@router.get("/recent")
async def get_recent_history(session_id: str):
    return {"history": []}


@router.post("/save")
async def save_route(session_id: str, route_data: dict):
    return {"status": "success", "id": "123"}


@router.get("/saved")
async def get_saved_routes(session_id: str):
    return {"saved_routes": []}


@router.put("/{route_id}/favourite")
async def toggle_favourite(route_id: str):
    return {"status": "success", "favourite": True}


@router.delete("/{route_id}")
async def delete_saved_route(route_id: str):
    return {"status": "deleted"}
