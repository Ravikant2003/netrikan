from typing import Dict, Any


def preprocess_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize incoming request data.
    """
    return {
        "latitude": float(payload.get("latitude", 0.0)),
        "longitude": float(payload.get("longitude", 0.0)),
        "destination": payload.get("destination", {}),
        "time_of_day": payload.get("time_of_day", "day"),
        "speed": float(payload.get("speed", 0.0)),
        "route_deviation": bool(payload.get("route_deviation", False)),
        "text_signal": payload.get("text_signal", ""),
    }
