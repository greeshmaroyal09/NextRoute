import time
from fastapi import APIRouter, Depends, Request
from app.infrastructure.rate_limiter import rate_limiter
from app.infrastructure.providers.cache import get_cache

from app.application.use_cases.search_routes import SearchRoutesUseCase
from app.presentation.schemas.search import SearchRequest, SearchResponse

router = APIRouter()

@router.post("/routes", response_model=SearchResponse)
async def search_routes(req: SearchRequest, request: Request):
    rate_limiter.check(request)
    
    cache_key = f"search:{req.from_code}:{req.to_code}:{req.date}:{req.mode}"
    cache_repo = get_cache()
    cached_data = cache_repo.get(cache_key)
    if cached_data:
        # HIGH BUG FIX: Ensure cached data passes through Pydantic validation
        return SearchResponse.model_validate_json(cached_data)

    start_time = time.time()
    graph = request.app.state.graph

    use_case = SearchRoutesUseCase(graph, None)
    journeys = use_case.execute(req.from_code, req.to_code, req.date, req.mode)

    resp = SearchResponse(
        journeys=journeys,
        meta={
            "total": len(journeys),
            "search_time_ms": int((time.time() - start_time) * 1000),
            "search_id": "req-12345",
        },
    )
    cache_repo.set(cache_key, resp.model_dump_json(), ttl=300)
    return resp
