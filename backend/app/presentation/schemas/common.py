from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: dict[str, Any] | None = None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[Any]
