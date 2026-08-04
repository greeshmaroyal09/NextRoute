from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="1.0.0")
