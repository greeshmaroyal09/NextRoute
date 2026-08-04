from fastapi import APIRouter, Depends, HTTPException
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
