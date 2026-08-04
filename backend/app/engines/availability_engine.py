from __future__ import annotations

import hashlib

from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import SeatStatus


class AvailabilityEngine:
    def calculate(self, journey: Journey) -> float:
        # Mock availability based on hash
        h = int(hashlib.md5(journey.journey_id.encode()).hexdigest(), 16) % 100
        if h < 20:
            return 0.0  # Unavailable
        if h < 50:
            return 0.2  # WL
        if h < 70:
            return 0.7  # RAC
        return 1.0  # Available

    def populate_segments(self, journey: Journey):
        # Update seat_status on segments
        h = int(hashlib.md5(journey.journey_id.encode()).hexdigest(), 16) % 100
        status = SeatStatus.AVAILABLE
        if h < 20:
            status = SeatStatus.UNAVAILABLE
        elif h < 40:
            status = SeatStatus.WL_30_PLUS
        elif h < 70:
            status = SeatStatus.RAC
        for seg in journey.segments:
            if seg.segment_type.value != "WALK":
                seg.seat_status = status
