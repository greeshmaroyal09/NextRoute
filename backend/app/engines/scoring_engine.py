from __future__ import annotations

from app.domain.entities.journey import Journey, ScoredJourney
from app.engines.availability_engine import AvailabilityEngine
from app.engines.comfort_engine import ComfortEngine
from app.engines.reliability_engine import ReliabilityEngine
from app.engines.safety_engine import SafetyEngine


class ScoringEngine:
    def __init__(self, db_weights: dict):
        self.weights = db_weights
        self.safety_eng = SafetyEngine()
        self.comfort_eng = ComfortEngine()
        self.reliability_eng = ReliabilityEngine()
        self.availability_eng = AvailabilityEngine()

    def rank(self, journeys: list[Journey]) -> list[ScoredJourney]:
        if not journeys:
            return []

        # Calculate raw factors
        raw_factors = []
        for j in journeys:
            rf = {
                "travel_time": float(j.total_duration_minutes),
                "waiting_time": max(
                    0,
                    float((j.arrival_time - j.departure_time).total_seconds() / 60)
                    - j.total_duration_minutes,
                ),
                "transfers": float(j.transfer_count),
                "cost": float(j.total_cost_inr),
                "availability": self.availability_eng.calculate(j),
                "comfort": self.comfort_eng.calculate(j),
                "safety": self.safety_eng.calculate(j),
                "reliability": self.reliability_eng.calculate(j),
                "walking_distance": float(
                    sum(
                        s.distance_km
                        for s in j.segments
                        if s.segment_type.value == "WALK"
                    )
                ),
                "arrival_penalty": 1.0
                if j.arrival_time.hour >= 22 or j.arrival_time.hour < 5
                else 0.0,
            }
            raw_factors.append((j, rf))

        # Min-Max Normalization (0 to 1, higher is better)
        def normalize(key, inverse=False):
            vals = [rf[key] for _, rf in raw_factors]
            min_v, max_v = min(vals), max(vals)
            if min_v == max_v:
                return [1.0] * len(vals)
            return [
                1.0 - (v - min_v) / (max_v - min_v)
                if inverse
                else (v - min_v) / (max_v - min_v)
                for v in vals
            ]

        norm = {
            "travel_time": normalize("travel_time", True),
            "waiting_time": normalize("waiting_time", True),
            "transfers": normalize("transfers", True),
            "cost": normalize("cost", True),
            "availability": normalize("availability", False),
            "comfort": normalize("comfort", False),
            "safety": normalize("safety", False),
            "reliability": normalize("reliability", False),
            "walking_distance": normalize("walking_distance", True),
            "arrival_penalty": normalize("arrival_penalty", True),
        }

        scored = []
        for idx, (j, raw) in enumerate(raw_factors):
            factor_scores = {k: norm[k][idx] for k in norm}
            overall = (
                sum(
                    factor_scores[k] * self.weights.get(k + "_weight", 0.1)
                    for k in factor_scores
                )
                * 100
            )
            scored.append(
                ScoredJourney(
                    journey=j,
                    overall_score=overall,
                    factor_scores=factor_scores,
                    factor_raw_values=raw,
                    rank=0,
                )
            )

        scored.sort(key=lambda sj: sj.overall_score, reverse=True)
        for idx, sj in enumerate(scored):
            sj.rank = idx + 1
        return scored
