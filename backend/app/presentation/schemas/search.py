from pydantic import BaseModel

from .journey import JourneyResponse


class SearchRequest(BaseModel):
    from_code: str
    to_code: str
    date: str
    mode: str | None = "DEFAULT"
    filters: dict | None = None


class SearchResponse(BaseModel):
    journeys: list[JourneyResponse]
    meta: dict
