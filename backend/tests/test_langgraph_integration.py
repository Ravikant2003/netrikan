import sys
from pathlib import Path
from unittest.mock import AsyncMock


# Ensure `backend/` is on sys.path so imports like `from main import ...` work.
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))


def test_langgraph_endpoint(monkeypatch):
    """
    Smoke-test the `/api/analyze` handler wiring without exercising the full graph.
    We patch `main.safety_app.ainvoke` to keep this test fast + deterministic.
    """
    import main
    from schemas import AnalyzeRequest

    mock_app = AsyncMock()
    mock_app.ainvoke = AsyncMock(
        return_value={
            "status": "success",
            "safety_index": {"risk_score": 0.8, "safety_level": "CRITICAL"},
            "orchestrator_decision": {
                "decision": "EMERGENCY_ESCALATION",
                "required_actions": ["POLICE_NOTIFICATION"],
            },
            "action_results": {"police_status": True},
            "timestamp": "2026-03-17T05:00:00",
        }
    )

    monkeypatch.setattr(main, "safety_app", mock_app)

    payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "text_signal": "emergency",
        "severity": "high",
    }

    request = AnalyzeRequest(**payload)
    import asyncio
    response = asyncio.run(main.analyze(request))

    assert response["status"] == "success"
    assert response["layer1_monitoring"]["safety_level"] == "CRITICAL"
    assert "police_status" in response["layer3_actions"]
    mock_app.ainvoke.assert_awaited_once()
