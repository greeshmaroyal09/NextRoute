import pytest
from app.engines.scoring_engine import ScoringEngine
from app.engines.route_engine import RouteEngine
from app.domain.entities.journey import Journey, JourneySegment
from app.domain.value_objects.enums import TransportType, SeatStatus
from datetime import datetime

def test_scoring_engine_initialization():
    weights = {"travel_time_weight": 0.2, "cost_weight": 0.8}
    engine = ScoringEngine(weights)
    assert engine.weights["cost_weight"] == 0.8

def test_scoring_engine_empty_list():
    engine = ScoringEngine({})
    assert engine.rank([]) == []

def test_route_engine_validation():
    import networkx as nx
    graph = nx.MultiDiGraph()
    graph.add_node("A", code="A", lat=10.0, lon=78.0)
    graph.add_node("B", code="B", lat=11.0, lon=79.0)
    graph.add_edge("A", "B", transport_type="WALK", duration=10, distance_meters=500, cost=0)
    
    engine = RouteEngine(graph)
    routes = engine.find_routes("A", "B", datetime.now())
    # Should not crash and should return empty or valid depending on graph constraints
    assert isinstance(routes, list)
