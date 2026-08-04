from datetime import datetime

from pydantic import BaseModel

from .station import StationInfo


class SeatAvailability(BaseModel):
    travel_class: str
    status: str
    probability: float | None = None
    last_updated: datetime


class CostBreakdown(BaseModel):
    base_fare: float
    taxes: float
    total_fare: float
    currency: str = "INR"


class SafetyInfo(BaseModel):
    rating: float
    has_women_only_coach: bool = True
    well_lit_transfer: bool = True
    cctv_available: bool = True


class ComfortInfo(BaseModel):
    rating: float
    ac_available: bool = False
    crowd_level: str = "MEDIUM"


class ReliabilityInfo(BaseModel):
    rating: float
    historical_delay_mins: int = 5
    cancellation_probability: float = 0.05


class ExplainReasonSchema(BaseModel):
    icon: str
    text: str
    factor: str
    impact: str
    strength: str


class JourneyScore(BaseModel):
    overall_score: float
    factor_scores: dict[str, float]
    rank: int


class JourneySegment(BaseModel):
    segment_type: str
    origin: StationInfo
    destination: StationInfo
    departure_time: datetime
    arrival_time: datetime
    duration_mins: int
    distance_km: float
    vehicle_info: dict | None
    cost: CostBreakdown | None
    seat_status: str | None


class TransferDifficultyResultSchema(BaseModel):
    station_name: str
    difficulty: str
    walking_meters: int
    buffer_minutes: int
    walking_minutes: int


class JourneyResponse(BaseModel):
    journey_id: str
    segments: list[JourneySegment]
    total_duration_mins: int
    total_cost: CostBreakdown
    total_transfers: int
    score: JourneyScore
    safety_info: SafetyInfo
    comfort_info: ComfortInfo
    reliability_info: ReliabilityInfo
    positive_reasons: list[ExplainReasonSchema]
    negative_reasons: list[ExplainReasonSchema]
    badges: list[str]
    recommendation_sentence: str
    transfer_difficulties: list[TransferDifficultyResultSchema]
