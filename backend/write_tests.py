import os

TEST_HEALTH = '''from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}
'''

TEST_ENGINES = '''import pytest
from app.engines.scoring_engine import ScoringEngine
from app.engines.route_engine import RouteEngine
from app.domain.entities.journey import Journey, JourneySegment
from app.domain.value_objects.enums import TransportType, SeatStatus
from datetime import datetime

def test_scoring_engine_initialization():
    weights = {"travel_time_weight": 0.2, "cost_weight": 0.8}
    engine = ScoringEngine(weights)
    assert engine._weights["cost_weight"] == 0.8

def test_scoring_engine_empty_list():
    engine = ScoringEngine({})
    assert engine.rank([]) == []

def test_route_engine_validation():
    import networkx as nx
    graph = nx.MultiDiGraph()
    graph.add_node("A", code="A")
    graph.add_node("B", code="B")
    graph.add_edge("A", "B", transport_type="WALK", duration=10, distance_meters=500, cost=0)
    
    engine = RouteEngine(graph)
    routes = engine.find_routes("A", "B", datetime.now())
    # Should not crash and should return empty or valid depending on graph constraints
    assert isinstance(routes, list)
'''

def write_tests():
    os.makedirs('tests/api', exist_ok=True)
    os.makedirs('tests/engines', exist_ok=True)
    
    with open('tests/api/test_health.py', 'w') as f:
        f.write(TEST_HEALTH)
    
    with open('tests/engines/test_engines.py', 'w') as f:
        f.write(TEST_ENGINES)
        
    print("Backend tests written.")

if __name__ == "__main__":
    write_tests()
