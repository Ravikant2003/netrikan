from agentic.orchestrator import AgenticSafetyOrchestrator


def build_payload(**overrides):
    payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "destination": {"lat": 12.9352, "lon": 77.6245},
        "time_of_day": "night",
        "speed": 32.0,
        "severity": "high",
        "route_deviation": False,
        "text_signal": "",
        "session_id": "runtime-test-session",
    }
    payload.update(overrides)
    return payload


def test_orchestrator_executes_specialist_tools():
    orchestrator = AgenticSafetyOrchestrator()

    result = orchestrator.run(build_payload())

    assert result["planner_mode"] in {"heuristic", "llm"}
    assert len(result["tool_trace"]) >= 3
    assert "crime_risk_lookup" in result["tools_used"]
    assert "ml_risk_prediction" in result["tools_used"]
    assert result["confidence"] >= 0.6
    assert result["safety"]["risk_score"] >= 0.0


def test_orchestrator_escalates_critical_emergency():
    orchestrator = AgenticSafetyOrchestrator()

    result = orchestrator.run(
        build_payload(route_deviation=True, text_signal="help me please")
    )

    assert result["emergency"]["level"] == "CRITICAL"
    assert result["decision"] == "ALERT"
    assert any("Critical emergency" in reason for reason in result["reasons"])


def test_orchestrator_reuses_session_memory_across_calls():
    orchestrator = AgenticSafetyOrchestrator()

    first = orchestrator.run(build_payload(session_id="shared-session"))
    second = orchestrator.run(build_payload(session_id="shared-session", speed=18.0))

    assert first["session_id"] == "shared-session"
    assert second["session_id"] == "shared-session"
    assert second["memory_size"] >= first["memory_size"]


def test_orchestrator_handles_missing_destination_without_route_tool_failure():
    orchestrator = AgenticSafetyOrchestrator()

    result = orchestrator.run(build_payload(destination={}))

    assert result["route"]["recommended_route"] in {"current_route", "safer_alternate"}
    assert result["route"]["details"]["distance_km"] >= 0.5
