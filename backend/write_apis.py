import os

SCHEMAS_COMMON = '''from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[Any]
'''

SCHEMAS_STATION = '''from pydantic import BaseModel
from typing import Optional, List

class StationInfo(BaseModel):
    id: str
    code: str
    name: str
    city: Optional[str]
    state: str
    type: str
    lat: float
    lon: float

class StationListResponse(BaseModel):
    stations: List[StationInfo]
    bus_stops: List[StationInfo]
'''

SCHEMAS_JOURNEY = '''from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from .station import StationInfo

class SeatAvailability(BaseModel):
    travel_class: str
    status: str
    probability: Optional[float] = None
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
    factor_scores: Dict[str, float]
    rank: int

class JourneySegment(BaseModel):
    segment_type: str
    origin: StationInfo
    destination: StationInfo
    departure_time: datetime
    arrival_time: datetime
    duration_mins: int
    distance_km: float
    vehicle_info: Optional[Dict]
    cost: Optional[CostBreakdown]
    seat_status: Optional[str]

class TransferDifficultyResultSchema(BaseModel):
    station_name: str
    difficulty: str
    walking_meters: int
    buffer_minutes: int
    walking_minutes: int

class JourneyResponse(BaseModel):
    journey_id: str
    segments: List[JourneySegment]
    total_duration_mins: int
    total_cost: CostBreakdown
    total_transfers: int
    score: JourneyScore
    safety_info: SafetyInfo
    comfort_info: ComfortInfo
    reliability_info: ReliabilityInfo
    positive_reasons: List[ExplainReasonSchema]
    negative_reasons: List[ExplainReasonSchema]
    badges: List[str]
    recommendation_sentence: str
    transfer_difficulties: List[TransferDifficultyResultSchema]
'''

SCHEMAS_SEARCH = '''from pydantic import BaseModel
from typing import Optional, List, Dict
from .journey import JourneyResponse

class SearchRequest(BaseModel):
    from_code: str
    to_code: str
    date: str
    mode: Optional[str] = "DEFAULT"
    filters: Optional[Dict] = None

class SearchResponse(BaseModel):
    journeys: List[JourneyResponse]
    meta: Dict
'''

USECASES_SEARCH = '''from app.engines.route_engine import RouteEngine
from app.engines.scoring_engine import ScoringEngine
from app.engines.explainability_engine import ExplainabilityEngine
from app.engines.recommendation_engine import RecommendationEngine
from app.engines.transfer_engine import TransferEngine
from app.presentation.schemas.journey import (
    JourneyResponse, JourneySegment, StationInfo, CostBreakdown,
    JourneyScore, SafetyInfo, ComfortInfo, ReliabilityInfo,
    ExplainReasonSchema, TransferDifficultyResultSchema
)
from app.domain.value_objects.enums import TransportType
from datetime import datetime

class SearchRoutesUseCase:
    def __init__(self, graph, db_session):
        self.route_engine = RouteEngine(graph)
        # In a real app we'd fetch weights from db_session
        default_weights = {
            "travel_time_weight": 0.2, "waiting_time_weight": 0.1, "transfers_weight": 0.1,
            "cost_weight": 0.15, "availability_weight": 0.1, "comfort_weight": 0.1,
            "safety_weight": 0.1, "reliability_weight": 0.08, "walking_distance_weight": 0.05,
            "arrival_penalty_weight": 0.02
        }
        self.scoring_engine = ScoringEngine(default_weights)
        self.transfer_engine = TransferEngine()
        self.explain_engine = ExplainabilityEngine()
        self.rec_engine = RecommendationEngine()

    def execute(self, from_code: str, to_code: str, travel_date: str, mode: str):
        t_date = datetime.strptime(travel_date, "%Y-%m-%d")
        raw_journeys = self.route_engine.find_routes(from_code, to_code, t_date)
        if not raw_journeys: return []
        
        scored = self.scoring_engine.rank(raw_journeys)
        
        explained = []
        for sj in scored:
            transfers = self.transfer_engine.analyze_transfers(sj.journey)
            ex_j = self.explain_engine.explain(sj, transfers)
            explained.append(ex_j)
            
        recommended = self.rec_engine.recommend(explained)
        
        # Map to DTO
        dtos = []
        for rj in recommended:
            segs = []
            for s in rj.scored_journey.journey.segments:
                segs.append(JourneySegment(
                    segment_type=s.segment_type.value,
                    origin=StationInfo(id="", code=s.origin_code, name=s.origin_name, city="", state="", type="", lat=0, lon=0),
                    destination=StationInfo(id="", code=s.destination_code, name=s.destination_name, city="", state="", type="", lat=0, lon=0),
                    departure_time=s.departure_time,
                    arrival_time=s.arrival_time,
                    duration_mins=s.duration_minutes,
                    distance_km=s.distance_km,
                    vehicle_info={"name": s.vehicle_name, "number": s.vehicle_number},
                    cost=CostBreakdown(base_fare=float(s.cost_inr), taxes=0, total_fare=float(s.cost_inr)),
                    seat_status=s.seat_status.value if s.seat_status else None
                ))
            
            dtos.append(JourneyResponse(
                journey_id=rj.scored_journey.journey.journey_id,
                segments=segs,
                total_duration_mins=rj.scored_journey.journey.total_duration_minutes,
                total_cost=CostBreakdown(base_fare=float(rj.scored_journey.journey.total_cost_inr), taxes=0, total_fare=float(rj.scored_journey.journey.total_cost_inr)),
                total_transfers=rj.scored_journey.journey.transfer_count,
                score=JourneyScore(overall_score=rj.scored_journey.overall_score, factor_scores=rj.scored_journey.factor_scores, rank=rj.scored_journey.rank),
                safety_info=SafetyInfo(rating=rj.scored_journey.factor_scores.get('safety', 0.5)),
                comfort_info=ComfortInfo(rating=rj.scored_journey.factor_scores.get('comfort', 0.5)),
                reliability_info=ReliabilityInfo(rating=rj.scored_journey.factor_scores.get('reliability', 0.5)),
                positive_reasons=[ExplainReasonSchema(icon=e.icon, text=e.text, factor=e.factor, impact=e.impact, strength=e.strength) for e in rj.positive_reasons],
                negative_reasons=[ExplainReasonSchema(icon=e.icon, text=e.text, factor=e.factor, impact=e.impact, strength=e.strength) for e in rj.negative_reasons],
                badges=rj.badges,
                recommendation_sentence=rj.recommendation_sentence,
                transfer_difficulties=[TransferDifficultyResultSchema(station_name=t.station_name, difficulty=t.difficulty.value, walking_meters=t.walking_meters, buffer_minutes=t.buffer_minutes, walking_minutes=t.walking_minutes) for t in rj.transfer_difficulties]
            ))
            
        return dtos
'''

API_SEARCH = '''from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.presentation.schemas.search import SearchRequest, SearchResponse
from app.application.use_cases.search_routes import SearchRoutesUseCase
from fastapi import Request
import time

router = APIRouter()

@router.post("/routes", response_model=SearchResponse)
async def search_routes(req: SearchRequest, request: Request):
    start_time = time.time()
    graph = request.app.state.graph
    
    use_case = SearchRoutesUseCase(graph, None)
    journeys = use_case.execute(req.from_code, req.to_code, req.date, req.mode)
    
    return SearchResponse(
        journeys=journeys,
        meta={
            "total": len(journeys),
            "search_time_ms": int((time.time() - start_time) * 1000),
            "search_id": "req-12345"
        }
    )
'''

API_HEALTH = '''from fastapi import APIRouter
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="1.0.0")
'''

def write_files():
    os.makedirs("app/presentation/schemas", exist_ok=True)
    os.makedirs("app/presentation/api/v1", exist_ok=True)
    os.makedirs("app/application/use_cases", exist_ok=True)
    
    with open("app/presentation/schemas/common.py", "w") as f: f.write(SCHEMAS_COMMON)
    with open("app/presentation/schemas/station.py", "w") as f: f.write(SCHEMAS_STATION)
    with open("app/presentation/schemas/journey.py", "w") as f: f.write(SCHEMAS_JOURNEY)
    with open("app/presentation/schemas/search.py", "w") as f: f.write(SCHEMAS_SEARCH)
    
    with open("app/application/use_cases/search_routes.py", "w") as f: f.write(USECASES_SEARCH)
    
    with open("app/presentation/api/v1/search.py", "w") as f: f.write(API_SEARCH)
    with open("app/presentation/api/v1/health.py", "w") as f: f.write(API_HEALTH)
    
    print("API files written.")

if __name__ == "__main__":
    write_files()
