import pytest
from fastapi.testclient import TestClient
from config import settings
from main import app

client = TestClient(app)


def build_payload():
    return {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "destination": {"lat": 12.9352, "lon": 77.6245},
        "time_of_day": "night",
        "speed": 28.0,
        "route_deviation": False,
        "text_signal": "",
    }


def get_auth_headers():
    login_resp = client.post(
        "/api/login",
        json={"username": settings.DEMO_USERNAME, "password": settings.DEMO_PASSWORD},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    return {"X-Auth-Token": token}


def login_and_get_token():
    login_resp = client.post(
        "/api/login",
        json={"username": settings.DEMO_USERNAME, "password": settings.DEMO_PASSWORD},
    )
    assert login_resp.status_code == 200
    return login_resp.json()["token"]

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analyze_route():
    payload = build_payload()
    resp = client.post("/api/analyze", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert "route" in body
    assert "safety" in body
    assert "emergency" in body


def test_risk_endpoint():
    resp = client.post("/api/risk", json=build_payload(), headers=get_auth_headers())
    assert resp.status_code == 200
    assert "risk_score" in resp.json()


def test_route_endpoint():
    resp = client.post("/api/route", json=build_payload(), headers=get_auth_headers())
    assert resp.status_code == 200
    assert "recommended_route" in resp.json()


def test_emergency_endpoint_critical():
    payload = build_payload()
    payload["text_signal"] = "help me"
    resp = client.post("/api/emergency", json=payload, headers=get_auth_headers())
    assert resp.status_code == 200
    assert resp.json()["level"] == "CRITICAL"


def test_user_registration_and_guardian():
    register_resp = client.post(
        "/api/register",
        json={"id": "test-user-1", "name": "Test", "phone": "+910000000001"},
    )
    guardian_resp = client.post(
        "/api/guardian",
        json={"user_id": "test-user-1", "contact": "+910000000002"},
    )

    assert register_resp.status_code == 200
    assert guardian_resp.status_code == 200
    assert register_resp.json()["status"] == "registered"
    assert guardian_resp.json()["status"] == "guardian added"


def test_protected_endpoint_requires_auth_token():
    resp = client.post("/api/risk", json=build_payload())
    assert resp.status_code == 401


def test_login_success():
    resp = client.post(
        "/api/login",
        json={"username": settings.DEMO_USERNAME, "password": settings.DEMO_PASSWORD},
    )
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_me_endpoint_returns_user():
    token = login_and_get_token()
    resp = client.get("/api/me", headers={"X-Auth-Token": token})
    assert resp.status_code == 200
    assert resp.json()["username"] == settings.DEMO_USERNAME


def test_logout_invalidates_token():
    token = login_and_get_token()
    logout_resp = client.post("/api/logout", headers={"X-Auth-Token": token})
    assert logout_resp.status_code == 200

    protected_resp = client.post(
        "/api/risk",
        json=build_payload(),
        headers={"X-Auth-Token": token},
    )
    assert protected_resp.status_code == 401
