from fastapi.testclient import TestClient
from config import settings
from main import app

client = TestClient(app)


def get_auth_headers():
    login_resp = client.post(
        "/api/login",
        json={"username": settings.DEMO_USERNAME, "password": settings.DEMO_PASSWORD},
    )
    assert login_resp.status_code == 200
    return {"X-Auth-Token": login_resp.json()["token"]}

def test_route_api():
    payload = {"latitude": 12.9716, "longitude": 77.5946, "destination": {"lat": 12.9352, "lon": 77.6245}}
    resp = client.post("/api/route", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    assert "recommended_route" in resp.json()


def test_route_api_without_destination_uses_safe_fallback():
    payload = {"latitude": 12.9716, "longitude": 77.5946}
    resp = client.post("/api/route", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert body["details"]["distance_km"] >= 0.5
    assert body["details"]["eta_minutes"] >= 3

def test_risk_api():
    payload = {"latitude": 12.9716, "longitude": 77.5946, "speed": 28.0, "time_of_day": "night"}
    resp = client.post("/api/risk", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    assert "risk_score" in resp.json()


def test_risk_api_high_severity_stays_bounded():
    payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "speed": 95.0,
        "time_of_day": "23:00",
        "severity": "high",
    }
    resp = client.post("/api/risk", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert 0.0 <= body["risk_score"] <= 1.0
    assert body["risk_level"] in {"SAFE", "MODERATE", "UNSAFE"}

def test_emergency_api():
    payload = {"latitude": 12.9716, "longitude": 77.5946, "text_signal": "help"}
    resp = client.post("/api/emergency", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    assert "level" in resp.json()


def test_emergency_api_route_deviation_elevates_response():
    payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "route_deviation": True,
        "text_signal": "",
    }
    resp = client.post("/api/emergency", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["level"] in {"ELEVATED", "CRITICAL"}
