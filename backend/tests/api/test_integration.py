import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

@pytest.fixture
def client():
    # Trigger lifespan manually in TestClient context
    with TestClient(app) as client:
        yield client

def test_health_check(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_search_routes_valid(client):
    payload = {
        "from_code": "MDU",
        "to_code": "SBC",
        "date": "2026-08-05",
        "mode": "DEFAULT"
    }
    response = client.post("/api/v1/search/routes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "journeys" in data
    assert "meta" in data

def test_search_routes_invalid_payload(client):
    payload = {
        "from_code": "MDU"
    }
    response = client.post("/api/v1/search/routes", json=payload)
    assert response.status_code == 422 # Pydantic validation error

def test_search_routes_empty(client):
    payload = {
        "from_code": "NON_EXISTENT",
        "to_code": "FAKE_STATION",
        "date": "2026-08-05",
        "mode": "DEFAULT"
    }
    response = client.post("/api/v1/search/routes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["journeys"]) == 0
