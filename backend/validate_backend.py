from fastapi.testclient import TestClient

from config import settings
from main import app


def run_validation() -> None:
	client = TestClient(app)

	payload = {
		"latitude": 12.9716,
		"longitude": 77.5946,
		"destination": {"lat": 12.9352, "lon": 77.6245},
		"time_of_day": "night",
		"speed": 38.5,
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
		("POST", "/api/analyze", payload),
		("POST", "/api/risk", payload),
		("POST", "/api/route", payload),
		("POST", "/api/emergency", payload),
		("GET", "/api/me", None),
		("POST", "/api/logout", None),
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

	print("Backend validation passed.")


if __name__ == "__main__":
	run_validation()
