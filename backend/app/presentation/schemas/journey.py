from __future__ import annotations
from pydantic import BaseModel
from .search import JourneySchema, ScoreBreakdownSchema

class JourneyDetailSchema(JourneySchema):
    score_breakdown: ScoreBreakdownSchema
    map_coordinates: list[list[float]]
