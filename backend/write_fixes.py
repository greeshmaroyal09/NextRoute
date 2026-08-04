import os

ROUTE_ENGINE_PY = '''from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import networkx as nx
from typing import Protocol

from app.config import get_settings
from app.domain.entities.journey import Journey, JourneySegment
from app.domain.value_objects.coordinate import Coordinate
from app.domain.value_objects.enums import TransportType

class IRoutingStrategy(Protocol):
    def can_handle(self, edge_data: dict) -> bool: ...
    def calculate_cost(self, edge_data: dict, distance: float) -> Decimal: ...

class TrainRoutingStrategy(IRoutingStrategy):
    def can_handle(self, edge_data: dict) -> bool:
        return edge_data.get("transport_type") == "TRAIN"
    def calculate_cost(self, edge_data: dict, distance: float) -> Decimal:
        return Decimal(str(edge_data.get("cost", distance * 0.5)))

class BusRoutingStrategy(IRoutingStrategy):
    def can_handle(self, edge_data: dict) -> bool:
        return edge_data.get("transport_type") == "BUS"
    def calculate_cost(self, edge_data: dict, distance: float) -> Decimal:
        return Decimal(str(max(10.0, float(edge_data.get("cost", 0)))))

class WalkRoutingStrategy(IRoutingStrategy):
    def can_handle(self, edge_data: dict) -> bool:
        return edge_data.get("transport_type") == "WALK"
    def calculate_cost(self, edge_data: dict, distance: float) -> Decimal:
        return Decimal('0')

class RouteEngine:
    def __init__(self, graph: nx.MultiDiGraph):
        self._graph = graph
        self._simple_graph = nx.DiGraph(graph)
        self._settings = get_settings()
        self._strategies = [TrainRoutingStrategy(), BusRoutingStrategy(), WalkRoutingStrategy()]

    def _get_nearby_nodes(self, station_code: str) -> list[str]:
        nodes = []
        target_node = None
        for node_id, data in self._graph.nodes(data=True):
            if data.get("code") == station_code:
                target_node = node_id
                break
        if not target_node:
            return []
        nodes.append(target_node)
        target_coord = Coordinate(
            latitude=self._graph.nodes[target_node].get("lat", 0),
            longitude=self._graph.nodes[target_node].get("lon", 0),
        )
        for node_id, data in self._graph.nodes(data=True):
            if node_id == target_node:
                continue
            coord = Coordinate(latitude=data.get("lat", 0), longitude=data.get("lon", 0))
            if target_coord.haversine_distance(coord) <= self._settings.NEARBY_RADIUS_KM:
                nodes.append(node_id)
        return nodes

    def find_routes(self, from_code: str, to_code: str, travel_date: datetime, max_transfers: int | None = None, allowed_modes: list[str] | None = None) -> list[Journey]:
        max_transfers = max_transfers or self._settings.MAX_TRANSFERS
        allowed_modes = allowed_modes or ["TRAIN", "BUS"]

        src_nodes = self._get_nearby_nodes(from_code)
        dst_nodes = self._get_nearby_nodes(to_code)

        if not src_nodes or not dst_nodes:
            return []

        all_paths = []
        for src in src_nodes:
            for dst in dst_nodes:
                try:
                    paths = list(nx.shortest_simple_paths(self._simple_graph, src, dst, weight="duration"))
                    for path_nodes in paths[: self._settings.K_SHORTEST_PATHS]:
                        p_edges = self._extract_path_edges(path_nodes, allowed_modes)
                        if p_edges:
                            all_paths.append(p_edges)
                except nx.NetworkXNoPath:
                    continue

        journeys = []
        for path in all_paths:
            journey = self._build_journey(path, travel_date)
            if journey and self._validate_timing(journey) and journey.transfer_count <= max_transfers:
                journeys.append(journey)

        return journeys

    def _extract_path_edges(self, path_nodes: list, allowed_modes: list[str]) -> list | None:
        edges = []
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            edge_data = None
            if self._graph.has_edge(u, v):
                edge_data = min(self._graph.get_edge_data(u, v).values(), key=lambda d: d.get("duration", 999))
            if not edge_data:
                return None
            t_type = edge_data.get("transport_type")
            if t_type != "WALK" and t_type not in allowed_modes:
                return None
            edges.append((u, v, edge_data))
        return edges
        
    def _check_runs_on(self, runs_on: str, date: datetime) -> bool:
        if not runs_on or len(runs_on) != 7:
            return True # Fallback if data is missing
        # Python weekday: Mon=0, Sun=6. Adjust depending on how dataset stores it.
        # Assuming index 0 = Monday.
        return runs_on[date.weekday()] == '1'

    def _build_journey(self, path: list, travel_date: datetime) -> Journey | None:
        if not path:
            return None
        segments = []
        total_cost = Decimal(0)
        transfer_count = 0
        last_transport = None
        base_dt = travel_date.replace(hour=8, minute=0, second=0)
        current_dt = base_dt

        for from_node, to_node, edge_data in path:
            transport = edge_data.get("transport_type", "TRAIN")
            if last_transport and last_transport != transport and transport != "WALK":
                transfer_count += 1
            if transport != "WALK":
                last_transport = transport

            from_data = self._graph.nodes.get(from_node, {})
            to_data = self._graph.nodes.get(to_node, {})

            dur = edge_data.get("duration", 60)
            dep_dt = current_dt

            dep_str = edge_data.get("departure")
            if dep_str and ":" in dep_str:
                h, m = map(int, dep_str.split(":"))
                new_dep_dt = dep_dt.replace(hour=h, minute=m)
                if new_dep_dt < dep_dt:
                    new_dep_dt += timedelta(days=1)
                
                # CRITICAL BUG FIX: Ensure the train actually runs on this new day
                if transport == "TRAIN":
                    runs_on = edge_data.get("runs_on", "1111111")
                    if not self._check_runs_on(runs_on, new_dep_dt):
                        return None # Invalid journey, train doesn't run on this day
                        
                dep_dt = new_dep_dt

            arr_dt = dep_dt + timedelta(minutes=dur)
            current_dt = arr_dt + timedelta(minutes=self._settings.MIN_TRANSFER_BUFFER_MINS)
            
            cost = Decimal(0)
            for strategy in self._strategies:
                if strategy.can_handle(edge_data):
                    cost = strategy.calculate_cost(edge_data, edge_data.get("distance", 0.0))
                    break
            total_cost += cost

            segments.append(
                JourneySegment(
                    segment_type=TransportType(transport) if transport in TransportType.__members__ else TransportType.TRAIN,
                    origin_code=from_data.get("code", from_node),
                    origin_name=from_data.get("name", from_node),
                    destination_code=to_data.get("code", to_node),
                    destination_name=to_data.get("name", to_node),
                    departure_time=dep_dt,
                    arrival_time=arr_dt,
                    duration_minutes=dur,
                    distance_km=edge_data.get("distance", 0.0),
                    cost_inr=cost,
                    travel_class=edge_data.get("travel_class"),
                    vehicle_name=edge_data.get("train_name") or edge_data.get("route_number"),
                    vehicle_number=edge_data.get("train_number") or edge_data.get("route_number"),
                    operator=edge_data.get("operator"),
                )
            )

        return Journey(journey_id=str(uuid.uuid4()), segments=segments)

    def _validate_timing(self, journey: Journey) -> bool:
        for i in range(len(journey.segments) - 1):
            if journey.segments[i].segment_type == TransportType.WALK:
                continue
            gap = (journey.segments[i+1].departure_time - journey.segments[i].arrival_time).total_seconds() / 60
            
            # CRITICAL BUG FIX: Chronological validation guarantees a transfer can never depart before previous arrives.
            if gap < self._settings.MIN_TRANSFER_BUFFER_MINS: 
                return False
        return True
'''

SEARCH_PY = '''import time
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
'''

def write_backend():
    with open('app/engines/route_engine.py', 'w', encoding='utf-8') as f:
        f.write(ROUTE_ENGINE_PY)
    with open('app/presentation/api/v1/search.py', 'w', encoding='utf-8') as f:
        f.write(SEARCH_PY)
    print("Backend fixes applied.")

if __name__ == "__main__":
    write_backend()
