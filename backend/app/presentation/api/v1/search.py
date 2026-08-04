from __future__ import annotations
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
