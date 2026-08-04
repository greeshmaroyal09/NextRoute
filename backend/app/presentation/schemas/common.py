from __future__ import annotations
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
