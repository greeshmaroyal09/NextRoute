from __future__ import annotations

from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType


class SafetyEngine:
    def calculate(self, journey: Journey) -> float:
        score = 1.0
        # Night travel penalty
        for seg in journey.segments:
            if seg.segment_type == TransportType.WALK:
                if seg.distance_km > 1.0:
                    score -= 0.1
                if seg.departure_time.hour >= 20 or seg.departure_time.hour <= 5:
                    score -= 0.2
            else:
                if seg.arrival_time.hour >= 23 or seg.arrival_time.hour <= 4:
                    score -= 0.1

        # Transfers penalty
        score -= min(0.4, journey.transfer_count * 0.1)
        return max(0.1, score)
