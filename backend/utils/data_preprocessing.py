from typing import Dict, Any


def preprocess_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize incoming request data.
    """
    destination = payload.get("destination") or {}
    return {
        "latitude": float(payload.get("latitude", 0.0)),
        "longitude": float(payload.get("longitude", 0.0)),
        "destination": {
            "lat": float(destination.get("lat", payload.get("latitude", 0.0))),
            "lon": float(destination.get("lon", payload.get("longitude", 0.0))),
        } if destination else {},
        "time_of_day": str(payload.get("time_of_day", "day")).strip().lower(),
        "speed": float(payload.get("speed", 0.0)),
        "severity": str(payload.get("severity", "low")).strip().lower(),
        "route_deviation": bool(payload.get("route_deviation", False)),
        "text_signal": str(payload.get("text_signal", "")).strip(),
        "session_id": payload.get("session_id"),
        "user_id": payload.get("user_id"),
    }
