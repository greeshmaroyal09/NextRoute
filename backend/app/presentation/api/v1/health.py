from __future__ import annotations
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
