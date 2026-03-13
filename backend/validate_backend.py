from fastapi.testclient import TestClient

from config import settings
from main import app


def run_validation() -> None:
	client = TestClient(app)

	baseline_payload = {
		"latitude": 12.9716,
		"longitude": 77.5946,
		"destination": {"lat": 12.9352, "lon": 77.6245},
		"time_of_day": "night",
		"speed": 38.5,
		"severity": "medium",
		"route_deviation": False,
		"text_signal": "",
	}
	login_response = client.post(
		"/api/login",
		json={
			"username": settings.DEMO_USERNAME,
			"password": settings.DEMO_PASSWORD,
		},
	)
	if login_response.status_code != 200:
		raise RuntimeError(
			f"Validation failed for /api/login: {login_response.status_code} {login_response.text}"
		)

	token = login_response.json().get("token")
	headers = {"X-Auth-Token": token}

	endpoints = [
		("GET", "/health", None),
		("POST", "/api/register", {"id": "u-1", "name": "Demo User"}),
		(
			"POST",
			"/api/guardian",
			{"user_id": "u-1", "contact": "+910000000001"},
		),
		("GET", "/api/me", None),
	]

	for method, endpoint, request_payload in endpoints:
		request_headers = (
			headers
			if endpoint
			in {
				"/api/analyze",
				"/api/risk",
				"/api/route",
				"/api/emergency",
				"/api/me",
				"/api/logout",
			}
			else None
		)
		response = (
			client.get(endpoint, headers=request_headers)
			if method == "GET"
			else client.post(endpoint, json=request_payload, headers=request_headers)
		)

		if response.status_code != 200:
			raise RuntimeError(
				f"Validation failed for {endpoint}: {response.status_code} {response.text}"
			)

	scenarios = [
		(
			"baseline_analyze",
			"/api/analyze",
			baseline_payload,
			lambda body: "decision" in body and len(body.get("tool_trace", [])) >= 3,
		),
		(
			"high_risk_prediction",
			"/api/risk",
			{
				**baseline_payload,
				"speed": 92.0,
				"severity": "high",
				"time_of_day": "23:00",
			},
			lambda body: 0.0 <= body.get("risk_score", -1) <= 1.0,
		),
		(
			"fallback_route",
			"/api/route",
			{"latitude": 12.9716, "longitude": 77.5946},
			lambda body: body.get("details", {}).get("distance_km", 0) >= 0.5,
		),
		(
			"critical_emergency",
			"/api/emergency",
			{**baseline_payload, "text_signal": "help me now", "route_deviation": True},
			lambda body: body.get("level") == "CRITICAL",
		),
	]

	for scenario_name, endpoint, request_payload, validator in scenarios:
		response = client.post(endpoint, json=request_payload, headers=headers)
		if response.status_code != 200:
			raise RuntimeError(
				f"Scenario {scenario_name} failed for {endpoint}: {response.status_code} {response.text}"
			)
		body = response.json()
		if not validator(body):
			raise RuntimeError(
				f"Scenario {scenario_name} returned unexpected body: {body}"
			)

	logout_response = client.post("/api/logout", headers=headers)
	if logout_response.status_code != 200:
		raise RuntimeError(
			f"Validation failed for /api/logout: {logout_response.status_code} {logout_response.text}"
		)

	print("Backend validation passed.")


if __name__ == "__main__":
	run_validation()
