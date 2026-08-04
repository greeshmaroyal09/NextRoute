from datetime import datetime

from app.engines.explainability_engine import ExplainabilityEngine
from app.engines.recommendation_engine import RecommendationEngine
from app.engines.route_engine import RouteEngine
from app.engines.scoring_engine import ScoringEngine
from app.engines.transfer_engine import TransferEngine
from app.presentation.schemas.journey import (
    ComfortInfo,
    CostBreakdown,
    ExplainReasonSchema,
    JourneyResponse,
    JourneyScore,
    JourneySegment,
    ReliabilityInfo,
    SafetyInfo,
    StationInfo,
    TransferDifficultyResultSchema,
)


class SearchRoutesUseCase:
    def __init__(self, graph, db_session):
        self.route_engine = RouteEngine(graph)
        # In a real app we'd fetch weights from db_session
        default_weights = {
            "travel_time_weight": 0.2,
            "waiting_time_weight": 0.1,
            "transfers_weight": 0.1,
            "cost_weight": 0.15,
            "availability_weight": 0.1,
            "comfort_weight": 0.1,
            "safety_weight": 0.1,
            "reliability_weight": 0.08,
            "walking_distance_weight": 0.05,
            "arrival_penalty_weight": 0.02,
        }
        self.scoring_engine = ScoringEngine(default_weights)
        self.transfer_engine = TransferEngine()
        self.explain_engine = ExplainabilityEngine()
        self.rec_engine = RecommendationEngine()

    def execute(self, from_code: str, to_code: str, travel_date: str, mode: str):
        t_date = datetime.strptime(travel_date, "%Y-%m-%d")
        raw_journeys = self.route_engine.find_routes(from_code, to_code, t_date)
        if not raw_journeys:
            return []

        scored = self.scoring_engine.rank(raw_journeys)

        explained = []
        for sj in scored:
            transfers = self.transfer_engine.analyze_transfers(sj.journey)
            ex_j = self.explain_engine.explain(sj, transfers)
            explained.append(ex_j)

        recommended = self.rec_engine.tag_recommendations(explained)

        # Map to DTO
        dtos = []
        for rj in recommended:
            segs = []
            for s in rj.scored_journey.journey.segments:
                segs.append(
                    JourneySegment(
                        segment_type=s.segment_type.value,
                        origin=StationInfo(
                            id="",
                            code=s.origin_code,
                            name=s.origin_name,
                            city="",
                            state="",
                            type="",
                            lat=0,
                            lon=0,
                        ),
                        destination=StationInfo(
                            id="",
                            code=s.destination_code,
                            name=s.destination_name,
                            city="",
                            state="",
                            type="",
                            lat=0,
                            lon=0,
                        ),
                        departure_time=s.departure_time,
                        arrival_time=s.arrival_time,
                        duration_mins=s.duration_minutes,
                        distance_km=s.distance_km,
                        vehicle_info={
                            "name": s.vehicle_name,
                            "number": s.vehicle_number,
                        },
                        cost=CostBreakdown(
                            base_fare=float(s.cost_inr),
                            taxes=0,
                            total_fare=float(s.cost_inr),
                        ),
                        seat_status=s.seat_status.value if s.seat_status else None,
                    )
                )

            dtos.append(
                JourneyResponse(
                    journey_id=rj.scored_journey.journey.journey_id,
                    segments=segs,
                    total_duration_mins=rj.scored_journey.journey.total_duration_minutes,
                    total_cost=CostBreakdown(
                        base_fare=float(rj.scored_journey.journey.total_cost_inr),
                        taxes=0,
                        total_fare=float(rj.scored_journey.journey.total_cost_inr),
                    ),
                    total_transfers=rj.scored_journey.journey.transfer_count,
                    score=JourneyScore(
                        overall_score=rj.scored_journey.overall_score,
                        factor_scores=rj.scored_journey.factor_scores,
                        rank=rj.scored_journey.rank,
                    ),
                    safety_info=SafetyInfo(
                        rating=rj.scored_journey.factor_scores.get("safety", 0.5)
                    ),
                    comfort_info=ComfortInfo(
                        rating=rj.scored_journey.factor_scores.get("comfort", 0.5)
                    ),
                    reliability_info=ReliabilityInfo(
                        rating=rj.scored_journey.factor_scores.get("reliability", 0.5)
                    ),
                    positive_reasons=[
                        ExplainReasonSchema(
                            icon=e.icon,
                            text=e.text,
                            factor=e.factor,
                            impact=e.impact,
                            strength=e.strength,
                        )
                        for e in rj.positive_reasons
                    ],
                    negative_reasons=[
                        ExplainReasonSchema(
                            icon=e.icon,
                            text=e.text,
                            factor=e.factor,
                            impact=e.impact,
                            strength=e.strength,
                        )
                        for e in rj.negative_reasons
                    ],
                    badges=rj.badges,
                    recommendation_sentence=rj.recommendation_sentence,
                    transfer_difficulties=[
                        TransferDifficultyResultSchema(
                            station_name=t.station_name,
                            difficulty=t.difficulty.value,
                            walking_meters=t.walking_meters,
                            buffer_minutes=t.buffer_minutes,
                            walking_minutes=t.walking_minutes,
                        )
                        for t in rj.transfer_difficulties
                    ],
                )
            )

        return dtos
