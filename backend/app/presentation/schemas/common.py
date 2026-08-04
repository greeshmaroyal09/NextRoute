from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[Any]
