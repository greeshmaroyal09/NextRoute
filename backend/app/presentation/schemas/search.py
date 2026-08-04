from __future__ import annotations
from pydantic import BaseModel
from typing import Any
from datetime import datetime
from decimal import Decimal

class FilterSchema(BaseModel):
    max_transfers: int | None = None
    max_budget: int | None = None
    max_travel_time_min: int | None = None
    preferred_classes: list[str] | None = None
    preferred_bus_types: list[str] | None = None
    available_seats_only: bool | None = None
    govt_bus_only: bool | None = None
    avoid_night: bool | None = None
    max_walking_m: int | None = None
    max_waiting_min: int | None = None
    min_comfort: float | None = None
    min_reliability: float | None = None

class SearchRequest(BaseModel):
    from_code: str
    to_code: str
    date: str
    mode: str = 'DEFAULT'
    filters: FilterSchema | None = None

class SegmentSchema(BaseModel):
    segment_type: str
    origin_code: str
    origin_name: str
    dest_code: str
    dest_name: str
    departure: datetime
    arrival: datetime
    duration_min: int
    distance_km: float
    cost_inr: Decimal
    travel_class: str | None = None
    vehicle_name: str | None = None
    vehicle_number: str | None = None
    operator: str | None = None
    seat_status: str | None = None

class TransferDifficultySchema(BaseModel):
    station_name: str
    difficulty: str
    walking_meters: int
    buffer_minutes: int
    walking_minutes: int

class ReasonSchema(BaseModel):
    icon: str
    text: str
    factor: str
    impact: str
    strength: str

class ScoreBreakdownSchema(BaseModel):
    overall: float
    travel_time: float
    waiting_time: float
    transfers: float
    cost: float
    availability: float
    comfort: float
    safety: float
    reliability: float
    walking_distance: float
    arrival_penalty: float

class JourneySchema(BaseModel):
    journey_id: str
    segments: list[SegmentSchema]
    total_duration_min: int
    total_cost_inr: Decimal
    transfer_count: int
    score: float
    positive_reasons: list[ReasonSchema]
    negative_reasons: list[ReasonSchema]
    badges: list[str]
    recommendation: str
    transfers_difficulty: list[TransferDifficultySchema]

class SearchResponse(BaseModel):
    journeys: list[JourneySchema]
    meta: dict[str, Any]
