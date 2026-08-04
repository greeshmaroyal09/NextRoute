from pydantic import BaseModel
from typing import Optional, List, Dict
from .journey import JourneyResponse

class SearchRequest(BaseModel):
    from_code: str
    to_code: str
    date: str
    mode: Optional[str] = "DEFAULT"
    filters: Optional[Dict] = None

class SearchResponse(BaseModel):
    journeys: List[JourneyResponse]
    meta: Dict
