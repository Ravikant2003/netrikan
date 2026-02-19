from typing import Dict, Any


def build_features(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert raw inputs into ML-friendly features.
    Extracts location, temporal, and behavioral signals.
    """
    return {
        "lat": data["latitude"],
        "lon": data["longitude"],
        "night_flag": 1 if data["time_of_day"] == "night" else 0,
        "speed": data["speed"],
        "route_deviation": int(data["route_deviation"]),
        "hour": 21 if data["time_of_day"] == "night" else 12,  # Added hour feature
    }
