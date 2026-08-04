from __future__ import annotations
from app.domain.entities.journey import Journey

class ReliabilityEngine:
    def calculate(self, journey: Journey) -> float:
        score = 1.0
        # More transfers = less reliable
        score -= min(0.5, journey.transfer_count * 0.15)
        # Tight buffer penalty
        for i in range(len(journey.segments) - 1):
            gap = (journey.segments[i+1].departure_time - journey.segments[i].arrival_time).total_seconds() / 60
            if gap > 0 and gap < 30:
                score -= 0.1
        return max(0.1, score)
