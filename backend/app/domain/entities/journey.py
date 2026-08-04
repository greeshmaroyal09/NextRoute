from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from app.domain.value_objects.enums import TransportType, SeatStatus, TransferDifficulty

@dataclass
class JourneySegment:
    segment_type: TransportType
    origin_code: str
    origin_name: str
    destination_code: str
    destination_name: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    distance_km: float
    cost_inr: Decimal
    travel_class: str | None = None
    vehicle_name: str | None = None
    vehicle_number: str | None = None
    operator: str | None = None
    seat_status: SeatStatus | None = None

@dataclass
class Journey:
    journey_id: str
    segments: list[JourneySegment]
    
    @property
    def total_duration_minutes(self) -> int:
        if not self.segments:
            return 0
        delta = self.segments[-1].arrival_time - self.segments[0].departure_time
        return int(delta.total_seconds() / 60)

    @property
    def total_cost_inr(self) -> Decimal:
        return sum(s.cost_inr for s in self.segments)

    @property
    def transfer_count(self) -> int:
        return len([s for s in self.segments if s.segment_type != TransportType.WALK]) - 1

    @property
    def departure_time(self) -> datetime:
        return self.segments[0].departure_time

    @property
    def arrival_time(self) -> datetime:
        return self.segments[-1].arrival_time

@dataclass
class ScoredJourney:
    journey: Journey
    overall_score: float
    factor_scores: dict[str, float]
    factor_raw_values: dict[str, Any]
    rank: int

@dataclass
class ExplainReason:
    icon: str
    text: str
    factor: str
    impact: str
    strength: str

@dataclass
class TransferDifficultyResult:
    station_name: str
    difficulty: TransferDifficulty
    walking_meters: int
    buffer_minutes: int
    walking_minutes: int

@dataclass
class ExplainedJourney:
    scored_journey: ScoredJourney
    positive_reasons: list[ExplainReason]
    negative_reasons: list[ExplainReason]
    badges: list[str]
    recommendation_sentence: str
    transfer_difficulties: list[TransferDifficultyResult]
