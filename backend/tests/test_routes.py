import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_route_api():
    payload = {"latitude": 12.9716, "longitude": 77.5946}
    resp = client.post("/api/route", json=payload)
    assert resp.status_code == 200
    assert "route" in resp.json() or resp.json() != {}

def test_risk_api():
    payload = {"latitude": 12.9716, "longitude": 77.5946}
    resp = client.post("/api/risk", json=payload)
    assert resp.status_code == 200
    assert "safety" in resp.json() or resp.json() != {}

def test_emergency_api():
    payload = {"latitude": 12.9716, "longitude": 77.5946}
    resp = client.post("/api/emergency", json=payload)
    assert resp.status_code == 200
    assert "emergency" in resp.json() or resp.json() != {}
