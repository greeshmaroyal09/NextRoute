import os

BASE_DIR = r"c:\Users\thispc\Downloads\NextRoute\backend\app"

FILES = {
    r"engines\route_engine.py": '''from __future__ import annotations
import networkx as nx
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Any
import uuid
import heapq

from app.domain.entities.journey import Journey, JourneySegment
from app.domain.value_objects.enums import TransportType, SeatStatus
from app.domain.value_objects.coordinate import Coordinate
from app.config import get_settings


class RouteEngine:
    """Discovers viable multi-modal travel paths using modified K-shortest paths."""
    
    def __init__(self, graph: nx.MultiDiGraph):
        self._graph = graph
        self._settings = get_settings()
    
    def find_routes(
        self,
        from_code: str,
        to_code: str,
        travel_date: datetime,
        max_transfers: int | None = None,
        allowed_modes: list[str] | None = None,
    ) -> list[Journey]:
        """Find K-best multimodal routes between two stations."""
        max_transfers = max_transfers or self._settings.MAX_TRANSFERS
        allowed_modes = allowed_modes or ["TRAIN", "BUS"]
        k = self._settings.K_SHORTEST_PATHS
        
        # 1. Expand source and destination to include nearby stations
        src_nodes = self._get_nearby_nodes(from_code)
        dst_nodes = self._get_nearby_nodes(to_code)
        
        if not src_nodes or not dst_nodes:
            return []
        
        # 2. Find K-shortest paths using modified BFS/Dijkstra
        raw_paths = self._find_k_paths(src_nodes, dst_nodes, k, max_transfers, allowed_modes)
        
        # 3. Validate timing constraints
        valid_journeys = []
        for path in raw_paths:
            journey = self._build_journey(path, travel_date)
            if journey and self._validate_timing(journey):
                valid_journeys.append(journey)
        
        return valid_journeys[:self._settings.SEARCH_RESULT_LIMIT * 5]  # Return extra for scoring to filter
    
    def _get_nearby_nodes(self, station_code: str) -> list[str]:
        """Get station code and nearby stations within radius."""
        nodes = []
        target_node = None
        
        for node_id, data in self._graph.nodes(data=True):
            if data.get('code') == station_code:
                target_node = node_id
                break
        
        if target_node is None:
            return []
        
        nodes.append(target_node)
        target_data = self._graph.nodes[target_node]
        target_coord = Coordinate(lat=target_data['lat'], lon=target_data['lon'])
        
        for node_id, data in self._graph.nodes(data=True):
            if node_id == target_node:
                continue
            node_coord = Coordinate(lat=data.get('lat', 0), lon=data.get('lon', 0))
            dist = target_coord.haversine_distance(node_coord)
            if dist <= self._settings.NEARBY_RADIUS_KM:
                nodes.append(node_id)
        
        return nodes
    
    def _find_k_paths(
        self,
        src_nodes: list[str],
        dst_nodes: list[str],
        k: int,
        max_transfers: int,
        allowed_modes: list[str],
    ) -> list[list[tuple[str, str, dict]]]:
        """Modified K-shortest paths with multimodal constraints."""
        all_paths = []
        dst_set = set(dst_nodes)
        
        for src in src_nodes:
            # BFS-based path finding with transfer counting
            # Each state: (current_node, path_so_far, transfers_used, last_transport_type)
            queue = [(0, src, [], 0, None)]  # (cost, node, path, transfers, last_mode)
            visited_states = set()
            
            while queue and len(all_paths) < k:
                cost, current, path, transfers, last_mode = heapq.heappop(queue)
                
                state_key = (current, transfers, last_mode)
                if state_key in visited_states:
                    continue
                visited_states.add(state_key)
                
                if current in dst_set and path:
                    all_paths.append(path)
                    continue
                
                if transfers > max_transfers:
                    continue
                
                for _, neighbor, edge_key, edge_data in self._graph.edges(current, keys=True, data=True):
                    transport = edge_data.get('transport_type', 'UNKNOWN')
                    
                    if transport == 'WALK':
                        new_transfers = transfers
                        new_mode = last_mode
                    elif transport in allowed_modes:
                        new_transfers = transfers + (1 if last_mode and last_mode != transport else 0)
                        new_mode = transport
                    else:
                        continue
                    
                    edge_cost = edge_data.get('duration', 60)
                    new_path = path + [(current, neighbor, edge_data)]
                    heapq.heappush(queue, (cost + edge_cost, neighbor, new_path, new_transfers, new_mode))
        
        return all_paths
    
    def _build_journey(self, path: list[tuple[str, str, dict]], travel_date: datetime) -> Journey | None:
        """Convert a graph path into a Journey entity."""
        if not path:
            return None
        
        segments = []
        total_cost = Decimal('0')
        transfer_count = 0
        last_transport = None
        
        for from_node, to_node, edge_data in path:
            transport_type = edge_data.get('transport_type', 'TRAIN')
            
            if transport_type == 'WALK':
                seg_type = TransportType.WALK
            elif transport_type == 'BUS':
                seg_type = TransportType.BUS
            else:
                seg_type = TransportType.TRAIN
            
            if last_transport and last_transport != transport_type and transport_type != 'WALK':
                transfer_count += 1
            if transport_type != 'WALK':
                last_transport = transport_type
            
            from_data = self._graph.nodes.get(from_node, {})
            to_data = self._graph.nodes.get(to_node, {})
            
            dep_time = edge_data.get('departure')
            arr_time = edge_data.get('arrival')
            duration = edge_data.get('duration', 60)
            
            base_date = travel_date.replace(hour=0, minute=0, second=0)
            if isinstance(dep_time, time):
                dep_dt = base_date.replace(hour=dep_time.hour, minute=dep_time.minute)
            elif isinstance(dep_time, str):
                parts = dep_time.split(':')
                dep_dt = base_date.replace(hour=int(parts[0]), minute=int(parts[1]))
            else:
                dep_dt = base_date.replace(hour=8, minute=0)
            
            arr_dt = dep_dt + timedelta(minutes=duration)
            cost = Decimal(str(edge_data.get('cost', 0)))
            total_cost += cost
            
            segment = JourneySegment(
                segment_type=seg_type,
                origin_code=from_data.get('code', from_node),
                origin_name=from_data.get('name', from_node),
                destination_code=to_data.get('code', to_node),
                destination_name=to_data.get('name', to_node),
                departure_time=dep_dt,
                arrival_time=arr_dt,
                duration_minutes=duration,
                distance_km=edge_data.get('distance', 0.0),
                cost_inr=cost,
                travel_class=edge_data.get('class'),
                vehicle_name=edge_data.get('train_name') or edge_data.get('route_number'),
                vehicle_number=edge_data.get('train_number') or edge_data.get('route_number'),
                operator=edge_data.get('operator'),
                seat_status=None,
            )
            segments.append(segment)
        
        if not segments:
            return None
        
        total_duration = sum(s.duration_minutes for s in segments)
        
        return Journey(
            journey_id=str(uuid.uuid4()),
            segments=segments,
            total_duration_minutes=total_duration,
            total_cost_inr=total_cost,
            transfer_count=transfer_count,
        )
    
    def _validate_timing(self, journey: Journey) -> bool:
        """Validate minimum buffer between connecting segments."""
        buffer = self._settings.MIN_TRANSFER_BUFFER_MINS
        for i in range(len(journey.segments) - 1):
            current = journey.segments[i]
            next_seg = journey.segments[i + 1]
            gap = (next_seg.departure_time - current.arrival_time).total_seconds() / 60
            if gap < 0:
                return False
        return True
''',
    r"engines\scoring_engine.py": '''from __future__ import annotations
from typing import Any
from app.domain.entities.journey import Journey, ScoredJourney
from app.engines.safety_engine import SafetyEngine
from app.engines.comfort_engine import ComfortEngine
from app.engines.reliability_engine import ReliabilityEngine
from app.engines.availability_engine import AvailabilityEngine

class ScoringEngine:
    def __init__(self, mode: str = "DEFAULT", safety_engine: SafetyEngine = None, comfort_engine: ComfortEngine = None, reliability_engine: ReliabilityEngine = None, availability_engine: AvailabilityEngine = None):
        self.mode = mode
        self.safety_engine = safety_engine or SafetyEngine()
        self.comfort_engine = comfort_engine or ComfortEngine()
        self.reliability_engine = reliability_engine or ReliabilityEngine()
        self.availability_engine = availability_engine or AvailabilityEngine()
        
        self.weights = {
            "travel_time": 0.20,
            "waiting_time": 0.10,
            "transfers": 0.10,
            "cost": 0.15,
            "availability": 0.10,
            "comfort": 0.10,
            "safety": 0.10,
            "reliability": 0.08,
            "walking_distance": 0.05,
            "arrival_penalty": 0.02
        }
        if mode == "WOMEN_ONLY":
            self.weights["safety"] = 0.25
            self.weights["cost"] = 0.10
        elif mode == "BUDGET":
            self.weights["cost"] = 0.40
            self.weights["comfort"] = 0.02
            
    def score_journeys(self, journeys: list[Journey]) -> list[ScoredJourney]:
        if not journeys:
            return []
            
        max_duration = max(j.total_duration_minutes for j in journeys) or 1
        max_cost = max(float(j.total_cost_inr) for j in journeys) or 1.0
        max_transfers = max(j.transfer_count for j in journeys) or 1
        
        scored = []
        for i, j in enumerate(journeys):
            time_score = 1.0 - (j.total_duration_minutes / max_duration)
            cost_score = 1.0 - (float(j.total_cost_inr) / max_cost)
            transfer_score = 1.0 - (j.transfer_count / max_transfers)
            
            safety = self.safety_engine.calculate(j, self.mode)
            comfort = self.comfort_engine.calculate(j)
            reliability = self.reliability_engine.calculate(j)
            avail = self.availability_engine.calculate(j)
            
            factors = {
                "travel_time": time_score,
                "waiting_time": 0.8,
                "transfers": transfer_score,
                "cost": cost_score,
                "availability": avail,
                "comfort": comfort,
                "safety": safety,
                "reliability": reliability,
                "walking_distance": 0.9,
                "arrival_penalty": 1.0
            }
            
            overall = sum(factors[k] * self.weights[k] for k in factors)
            scored.append(ScoredJourney(
                journey=j,
                overall_score=overall,
                factor_scores=factors,
                factor_raw_values={"duration": j.total_duration_minutes, "cost": float(j.total_cost_inr)},
                rank=0
            ))
            
        scored.sort(key=lambda x: x.overall_score, reverse=True)
        for i, s in enumerate(scored):
            s.rank = i + 1
            
        return scored
''',
    r"engines\safety_engine.py": '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType

class SafetyEngine:
    def calculate(self, journey: Journey, mode: str = "DEFAULT") -> float:
        score = 1.0
        for segment in journey.segments:
            if segment.arrival_time:
                hour = segment.arrival_time.hour
                if 23 <= hour or hour < 5:
                    score *= 0.3 if mode != "WOMEN_ONLY" else 0.1
                elif 20 <= hour < 23:
                    score *= 0.6 if mode != "WOMEN_ONLY" else 0.4
        
        if journey.transfer_count == 1:
            score *= 0.8
        elif journey.transfer_count == 2:
            score *= 0.6
        elif journey.transfer_count >= 3:
            score *= 0.4
            
        return max(0.0, score)
''',
    r"engines\comfort_engine.py": '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType

class ComfortEngine:
    def __init__(self):
        self.TRAIN_COMFORT = {"GENERAL": 0.2, "SLEEPER": 0.4, "AC_3": 0.6, "AC_2": 0.8, "AC_1": 1.0}
        self.BUS_COMFORT = {"ORDINARY": 0.2, "EXPRESS": 0.4, "SUPER_LUXURY": 0.7, "SLEEPER": 0.9}
        
    def calculate(self, journey: Journey) -> float:
        total_duration = journey.total_duration_minutes
        if total_duration == 0:
            return 1.0
            
        weighted_comfort = 0.0
        for seg in journey.segments:
            cls = seg.travel_class or "GENERAL"
            if seg.segment_type == TransportType.TRAIN:
                c_score = self.TRAIN_COMFORT.get(cls, 0.5)
            elif seg.segment_type == TransportType.BUS:
                c_score = self.BUS_COMFORT.get(cls, 0.5)
            else:
                c_score = 0.5
            weighted_comfort += c_score * seg.duration_minutes
            
        return weighted_comfort / total_duration
''',
    r"engines\reliability_engine.py": '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType

class ReliabilityEngine:
    def calculate(self, journey: Journey) -> float:
        if not journey.segments:
            return 1.0
        return 0.85
''',
    r"engines\availability_engine.py": '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType

class AvailabilityEngine:
    def calculate(self, journey: Journey) -> float:
        scores = []
        for seg in journey.segments:
            if seg.segment_type == TransportType.TRAIN:
                if seg.seat_status:
                    if "AVAILABLE" in str(seg.seat_status):
                        scores.append(1.0)
                    elif "RAC" in str(seg.seat_status):
                        scores.append(0.7)
                    elif "WL" in str(seg.seat_status):
                        scores.append(0.4)
                    else:
                        scores.append(0.0)
                else:
                    scores.append(1.0)
            elif seg.segment_type == TransportType.BUS:
                scores.append(1.0)
                
        if not scores:
            return 1.0
        return sum(scores) / len(scores)
''',
    r"engines\explainability_engine.py": '''from __future__ import annotations
from app.domain.entities.journey import ScoredJourney, ExplainedJourney, ExplainReason
from app.domain.value_objects.enums import TransportType

class ExplainabilityEngine:
    def explain(self, scored_journeys: list[ScoredJourney]) -> list[ExplainedJourney]:
        if not scored_journeys:
            return []
            
        explained = []
        min_cost = min(float(sj.journey.total_cost_inr) for sj in scored_journeys)
        min_duration = min(sj.journey.total_duration_minutes for sj in scored_journeys)
        
        for sj in scored_journeys:
            reasons = []
            badges = []
            
            if float(sj.journey.total_cost_inr) == min_cost:
                reasons.append(ExplainReason(icon="💰", text="Lowest cost among options", factor="cost", impact="positive", strength="strong"))
                badges.append("Cheapest")
            
            if sj.journey.total_duration_minutes == min_duration:
                reasons.append(ExplainReason(icon="⚡", text="Fastest route", factor="duration", impact="positive", strength="strong"))
                badges.append("Fastest")
                
            if sj.rank == 1:
                badges.append("Best Overall")
                
            explained.append(ExplainedJourney(
                journey=sj.journey,
                overall_score=sj.overall_score,
                factor_scores=sj.factor_scores,
                factor_raw_values=sj.factor_raw_values,
                rank=sj.rank,
                positive_reasons=[r for r in reasons if r.impact == "positive"],
                negative_reasons=[r for r in reasons if r.impact == "negative"],
                badges=badges,
                recommendation_sentence="Highly recommended route based on your preferences."
            ))
            
        return explained
''',
    r"engines\transfer_engine.py": '''from __future__ import annotations
from app.domain.entities.journey import Journey, TransferDifficultyResult
from app.domain.value_objects.enums import TransportType, TransferDifficulty

class TransferDifficultyEngine:
    def evaluate_journey(self, journey: Journey) -> list[TransferDifficultyResult]:
        results = []
        for i in range(len(journey.segments) - 1):
            seg1 = journey.segments[i]
            seg2 = journey.segments[i+1]
            
            if seg1.destination_code != seg2.origin_code:
                buffer_mins = (seg2.departure_time - seg1.arrival_time).total_seconds() / 60
                results.append(TransferDifficultyResult(
                    station_name=seg1.destination_name,
                    difficulty=TransferDifficulty.MODERATE if buffer_mins < 60 else TransferDifficulty.EASY,
                    walking_meters=500,
                    buffer_minutes=int(buffer_mins),
                    walking_minutes=10
                ))
                
        return results
''',
    r"presentation\schemas\common.py": '''from __future__ import annotations
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    status_code: int

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int

class HealthResponse(BaseModel):
    status: str
    version: str
    graph_nodes: int
    graph_edges: int
''',
    r"presentation\schemas\station.py": '''from __future__ import annotations
from pydantic import BaseModel

class StationSchema(BaseModel):
    id: str
    code: str
    name: str
    city: str | None = None
    state: str | None = None
    latitude: float
    longitude: float
    station_type: str
    zone: str | None = None

class AutocompleteItem(BaseModel):
    code: str
    name: str
    station_type: str
    state: str | None = None
    type: str = 'TRAIN'

class AutocompleteResponse(BaseModel):
    suggestions: list[AutocompleteItem]

class NearbyResponse(BaseModel):
    stations: list[StationSchema]
    bus_stops: list[StationSchema]
''',
    r"presentation\schemas\search.py": '''from __future__ import annotations
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
''',
    r"presentation\schemas\journey.py": '''from __future__ import annotations
from pydantic import BaseModel
from .search import JourneySchema, ScoreBreakdownSchema

class JourneyDetailSchema(JourneySchema):
    score_breakdown: ScoreBreakdownSchema
    map_coordinates: list[list[float]]
''',
    r"presentation\schemas\feedback.py": '''from __future__ import annotations
from pydantic import BaseModel

class FeedbackCreateSchema(BaseModel):
    route_hash: str
    overall_rating: int
    comfort_rating: int
    safety_rating: int
    accuracy_rating: int
    would_recommend: bool
    comments: str | None = None

class FeedbackStatsSchema(BaseModel):
    route_hash: str
    avg_overall: float
    avg_comfort: float
    avg_safety: float
    avg_accuracy: float
    recommend_pct: float
    total_count: int
''',
    r"presentation\api\v1\health.py": '''from __future__ import annotations
from fastapi import APIRouter, Request
from app.presentation.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def get_health(request: Request):
    app = request.app
    graph = getattr(app.state, "graph", None)
    nodes = len(graph.nodes) if graph else 0
    edges = len(graph.edges) if graph else 0
    return HealthResponse(
        status="ok",
        version="1.0.0",
        graph_nodes=nodes,
        graph_edges=edges
    )
''',
    r"presentation\api\v1\stations.py": '''from __future__ import annotations
from fastapi import APIRouter, Request
from app.presentation.schemas.station import StationSchema

router = APIRouter(tags=["Stations"])

@router.get("/stations", response_model=list[StationSchema])
async def list_stations(request: Request, state: str | None = None, limit: int = 10, offset: int = 0):
    return []

@router.get("/stations/{code}", response_model=StationSchema)
async def get_station(request: Request, code: str):
    return StationSchema(id="1", code=code, name="Example", city="City", state="State", latitude=0.0, longitude=0.0, station_type="TRAIN")
''',
    r"presentation\api\v1\search.py": '''from __future__ import annotations
from fastapi import APIRouter, Request
from datetime import datetime
from app.presentation.schemas.search import SearchRequest, SearchResponse
from app.presentation.schemas.station import AutocompleteResponse, NearbyResponse
from app.engines.route_engine import RouteEngine
from app.engines.scoring_engine import ScoringEngine
from app.engines.explainability_engine import ExplainabilityEngine
from app.engines.transfer_engine import TransferDifficultyEngine

router = APIRouter(tags=["Search"])

@router.post("/search/routes", response_model=SearchResponse)
async def search_routes(request: Request, body: SearchRequest):
    graph = getattr(request.app.state, "graph", None)
    if not graph:
        return SearchResponse(journeys=[], meta={"total": 0, "search_time_ms": 0, "search_id": ""})
        
    route_engine = RouteEngine(graph)
    travel_date = datetime.fromisoformat(body.date)
    raw_journeys = route_engine.find_routes(body.from_code, body.to_code, travel_date)
    
    scoring_engine = ScoringEngine(mode=body.mode)
    scored = scoring_engine.score_journeys(raw_journeys)
    
    expl_engine = ExplainabilityEngine()
    explained = expl_engine.explain(scored)
    
    trans_engine = TransferDifficultyEngine()
    for ej in explained:
        setattr(ej.journey, 'transfers_difficulty', trans_engine.evaluate_journey(ej.journey))
        
    return SearchResponse(journeys=[], meta={"total": 0, "search_time_ms": 0, "search_id": ""})

@router.get("/search/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(request: Request, q: str, limit: int = 10):
    return AutocompleteResponse(suggestions=[])

@router.get("/search/nearby", response_model=NearbyResponse)
async def nearby(request: Request, lat: float, lon: float, radius_km: float = 30):
    return NearbyResponse(stations=[], bus_stops=[])
''',
    r"presentation\api\v1\journey.py": '''from __future__ import annotations
from fastapi import APIRouter, Request, HTTPException
from app.presentation.schemas.journey import JourneyDetailSchema

router = APIRouter(tags=["Journey"])

@router.get("/journey/{journey_id}", response_model=JourneyDetailSchema)
async def get_journey(request: Request, journey_id: str):
    cache = getattr(request.app.state, "journey_cache", {})
    if journey_id not in cache:
        raise HTTPException(status_code=404, detail="Journey not found")
    return cache[journey_id]
''',
    r"presentation\api\v1\history.py": '''from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(tags=["History"])

@router.get("/history/recent")
async def get_recent_history(session_id: str, limit: int = 10):
    return []

@router.post("/routes/save")
async def save_route():
    return {"status": "ok"}

@router.get("/routes/saved")
async def get_saved_routes(session_id: str):
    return []

@router.put("/routes/{id}/favourite")
async def toggle_favourite(id: str):
    return {"status": "ok"}

@router.delete("/routes/{id}")
async def delete_route(id: str):
    return {"status": "ok"}
''',
    r"presentation\api\v1\feedback.py": '''from __future__ import annotations
from fastapi import APIRouter
from app.presentation.schemas.feedback import FeedbackCreateSchema, FeedbackStatsSchema

router = APIRouter(tags=["Feedback"])

@router.post("/feedback")
async def submit_feedback(body: FeedbackCreateSchema):
    return {"status": "ok"}

@router.get("/feedback/stats/{route_hash}", response_model=FeedbackStatsSchema)
async def get_feedback_stats(route_hash: str):
    return FeedbackStatsSchema(route_hash=route_hash, avg_overall=5.0, avg_comfort=5.0, avg_safety=5.0, avg_accuracy=5.0, recommend_pct=100.0, total_count=1)
''',
    r"application\use_cases\search_routes.py": '''from __future__ import annotations

class SearchRoutesUseCase:
    async def execute(self, req: dict) -> dict:
        return {}
''',
    r"application\use_cases\get_station.py": '''from __future__ import annotations

class AutocompleteUseCase:
    async def execute(self, query: str) -> list:
        return []

class NearbyStationsUseCase:
    async def execute(self, lat: float, lon: float) -> dict:
        return {}
''',
    r"application\use_cases\manage_history.py": '''from __future__ import annotations

class SaveSearchHistory:
    async def execute(self):
        pass

class GetRecentSearches:
    async def execute(self):
        return []
''',
    r"application\use_cases\manage_routes.py": '''from __future__ import annotations

class SaveRoute:
    async def execute(self):
        pass

class GetSavedRoutes:
    async def execute(self):
        return []

class ToggleFavourite:
    async def execute(self):
        pass

class DeleteRoute:
    async def execute(self):
        pass
''',
    r"application\use_cases\submit_feedback.py": '''from __future__ import annotations

class SubmitFeedback:
    async def execute(self):
        pass

class GetFeedbackStats:
    async def execute(self):
        pass
''',
    r"application\dto\search.py": '''from __future__ import annotations
from pydantic import BaseModel

class SearchRequestDTO(BaseModel):
    pass
class SearchResponseDTO(BaseModel):
    pass
class JourneyDTO(BaseModel):
    pass
class SegmentDTO(BaseModel):
    pass
''',
    r"application\dto\station.py": '''from __future__ import annotations
from pydantic import BaseModel

class StationDTO(BaseModel):
    pass
class AutocompleteResultDTO(BaseModel):
    pass
''',
    r"application\dto\feedback.py": '''from __future__ import annotations
from pydantic import BaseModel

class FeedbackRequestDTO(BaseModel):
    pass
class FeedbackStatsDTO(BaseModel):
    pass
'''
}

for k, v in FILES.items():
    path = os.path.join(BASE_DIR, k)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(v)

print("Created 27 files successfully!")
