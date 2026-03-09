from typing import Dict


def get_route(start: Dict[str, float], end: Dict[str, float]) -> Dict[str, float]:
    """
    Deterministic fallback route estimate.
    Can be swapped with a real Maps API client.
    """
    start_lat = float(start.get("lat", 0.0))
    start_lon = float(start.get("lon", 0.0))
    end_lat = float(end.get("lat", start_lat))
    end_lon = float(end.get("lon", start_lon))

    lat_delta = abs(end_lat - start_lat)
    lon_delta = abs(end_lon - start_lon)
    distance_km = max(0.5, (lat_delta + lon_delta) * 111)

    eta_minutes = max(3, int(distance_km * 2.5))
    congestion_factor = min(0.5, distance_km / 25)
    risk_weight = min(1.0, 0.2 + congestion_factor)

    return {
        "distance_km": round(distance_km, 2),
        "eta_minutes": eta_minutes,
        "risk_weight": round(risk_weight, 2),
    }
