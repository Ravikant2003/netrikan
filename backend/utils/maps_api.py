import urllib.request
import json
import math
import os
from typing import Dict, List, Optional

import httpx

from utils.crime_api import crime_score
from utils.overpass_api import get_road_context


def _fetch_osrm_route(s_lon: float, s_lat: float, e_lon: float, e_lat: float,
                      via_lon: Optional[float] = None, via_lat: Optional[float] = None) -> Optional[dict]:
    """
    Fetches a single route from OSRM. Optionally routes via a midpoint.
    Returns a dict with distance_km, eta_minutes, coordinates — or None on failure.
    """
    if os.environ.get("NETRIKAN_NO_NETWORK", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        return None
    if via_lon is not None and via_lat is not None:
        coords_str = f"{s_lon},{s_lat};{via_lon},{via_lat};{e_lon},{e_lat}"
    else:
        coords_str = f"{s_lon},{s_lat};{e_lon},{e_lat}"

    url = (
        f"http://router.project-osrm.org/route/v1/driving/{coords_str}"
        f"?overview=full&geometries=geojson"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Netrikan/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        if data.get("code") == "Ok" and data.get("routes"):
            r = data["routes"][0]
            dist_km = float(r.get("distance", 0)) / 1000.0
            eta_min = float(r.get("duration", 0)) / 60.0
            raw_coords = r.get("geometry", {}).get("coordinates", [])
            formatted = [{"lat": float(c[1]), "lon": float(c[0])} for c in raw_coords]
            return {
                "distance_km": round(dist_km, 2),
                "eta_minutes": int(eta_min),
                "risk_weight": 0.20,
                "coordinates": formatted,
            }
    except Exception as e:
        print(f"OSRM fetch error: {e}")
    return None


def _fetch_ors_route(s_lon: float, s_lat: float, e_lon: float, e_lat: float,
                     via_lon: Optional[float] = None, via_lat: Optional[float] = None) -> Optional[dict]:
    """
    Fetches a single route from OpenRouteService Directions API.
    Returns a dict with distance_km, eta_minutes, coordinates - or None on failure.
    """
    if os.environ.get("NETRIKAN_NO_NETWORK", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        return None

    token = os.environ.get("OPENROUTESERVICE_API_KEY", "").strip()
    if not token:
        return None

    coords = [[s_lon, s_lat]]
    if via_lon is not None and via_lat is not None:
        coords.append([via_lon, via_lat])
    coords.append([e_lon, e_lat])

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    payload = {
        "coordinates": coords,
        "instructions": False,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload, headers={"Authorization": token})
            if resp.status_code >= 300:
                return None
            data = resp.json()

        features = data.get("features") or []
        if not features:
            return None

        props = features[0].get("properties") or {}
        summary = props.get("summary") or {}
        geom = features[0].get("geometry") or {}
        raw_coords = geom.get("coordinates") or []

        dist_km = float(summary.get("distance", 0)) / 1000.0
        eta_min = float(summary.get("duration", 0)) / 60.0
        formatted = [{"lat": float(c[1]), "lon": float(c[0])} for c in raw_coords]
        return {
            "distance_km": round(dist_km, 2),
            "eta_minutes": int(eta_min),
            "risk_weight": 0.20,
            "coordinates": formatted,
        }
    except Exception:
        return None
    return None


def _deflect_midpoint(s_lat: float, s_lon: float, e_lat: float, e_lon: float,
                      bearing_offset_deg: float, deflection_km: float):
    """
    Computes a via-point by taking the geographic midpoint and moving it
    perpendicular to the direct path by `deflection_km` km.
    """
    mid_lat = (s_lat + e_lat) / 2.0
    mid_lon = (s_lon + e_lon) / 2.0

    # Direct bearing in radians
    d_lat = math.radians(e_lat - s_lat)
    d_lon = math.radians(e_lon - s_lon)
    direct_bearing_rad = math.atan2(d_lon, d_lat)

    # Perpendicular bearing
    perp_bearing_rad = direct_bearing_rad + math.radians(bearing_offset_deg)

    # Convert km to degrees (~111 km per degree)
    delta = deflection_km / 111.0

    via_lat = mid_lat + delta * math.cos(perp_bearing_rad)
    via_lon = mid_lon + delta * math.sin(perp_bearing_rad)
    return via_lat, via_lon


def _straight_line_fallback(s_lat: float, s_lon: float, e_lat: float, e_lon: float, 
                           via_lat: Optional[float] = None, via_lon: Optional[float] = None) -> dict:
    lat_delta = abs(e_lat - s_lat)
    lon_delta = abs(e_lon - s_lon)
    distance_km = max(0.5, (lat_delta + lon_delta) * 111)
    eta_minutes = max(3, int(distance_km * 2.5))
    risk_weight = min(1.0, 0.2 + min(0.5, distance_km / 25))
    
    # Build path - if via-point provided, go via it, otherwise straight line
    steps = 10
    if via_lat is not None and via_lon is not None:
        # Two segments: start -> via -> end
        coords = []
        for i in range(steps + 1):
            t = i / steps
            coords.append({
                "lat": s_lat + (via_lat - s_lat) * t,
                "lon": s_lon + (via_lon - s_lon) * t,
            })
        for i in range(steps + 1):
            if i == 0:
                continue
            t = i / steps
            coords.append({
                "lat": via_lat + (e_lat - via_lat) * t,
                "lon": via_lon + (e_lon - via_lon) * t,
            })
    else:
        coords = [
            {
                "lat": s_lat + (e_lat - s_lat) * i / steps,
                "lon": s_lon + (e_lon - s_lon) * i / steps,
            }
            for i in range(steps + 1)
        ]
    return {
        "distance_km": round(distance_km, 2),
        "eta_minutes": int(eta_minutes),
        "risk_weight": round(risk_weight, 2),
        "coordinates": coords,
    }


def _road_risk_from_context(context: Optional[Dict[str, object]]) -> float:
    if not context:
        return 0.2
    highway = str(context.get("highway") or "")
    lit = str(context.get("lit") or "").lower()

    road_risk = 0.2
    if highway in {"motorway", "trunk", "primary"}:
        road_risk = 0.55
    elif highway in {"secondary", "tertiary"}:
        road_risk = 0.4
    elif highway in {"residential", "living_street"}:
        road_risk = 0.25

    if lit in {"no", "0", "false"}:
        road_risk += 0.15
    elif lit in {"yes", "1", "true"}:
        road_risk -= 0.05

    return min(0.95, max(0.05, road_risk))


def _contextual_route_risk(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    if os.environ.get("NETRIKAN_ROUTE_CONTEXT", "").strip() not in {"1", "true", "TRUE", "yes", "YES"}:
        return 0.0

    mid_lat = (lat_a + lat_b) * 0.5
    mid_lon = (lon_a + lon_b) * 0.5

    road_context = get_road_context(mid_lat, mid_lon)
    road_risk = _road_risk_from_context(road_context)

    incident_risk = max(
        crime_score(lat_a, lon_a),
        crime_score(mid_lat, mid_lon),
        crime_score(lat_b, lon_b),
    )

    return min(0.99, 0.5 * road_risk + 0.5 * incident_risk)


def get_route(start: Dict[str, float], end: Dict[str, float]) -> Dict:
    """Simple single-route estimate (kept for backward compatibility)."""
    s_lat, s_lon = float(start.get("lat", 0.0)), float(start.get("lon", 0.0))
    e_lat, e_lon = float(end.get("lat", s_lat)), float(end.get("lon", s_lon))
    result = _fetch_ors_route(s_lon, s_lat, e_lon, e_lat)
    if result:
        context_risk = _contextual_route_risk(s_lat, s_lon, e_lat, e_lon)
        if context_risk:
            result["risk_weight"] = round(max(result["risk_weight"], context_risk), 2)
            result["context_risk"] = round(context_risk, 2)
        return result
    result = _fetch_osrm_route(s_lon, s_lat, e_lon, e_lat)
    if result:
        return result
    fallback = _straight_line_fallback(s_lat, s_lon, e_lat, e_lon)
    context_risk = _contextual_route_risk(s_lat, s_lon, e_lat, e_lon)
    if context_risk:
        fallback["risk_weight"] = round(max(fallback["risk_weight"], context_risk), 2)
        fallback["context_risk"] = round(context_risk, 2)
    return fallback


def get_multiple_routes(start: Dict[str, float], end: Dict[str, float],
                        safety_context: Optional[Dict] = None) -> list:
    """
    Returns exactly 3 genuinely distinct routes using via-point deflection.
    When safety_context is provided (XGBoost output), it blends:
       final_risk = route_geometry_risk * 0.5 + ml_risk * 0.3 + crime_risk * 0.2
    """
    s_lat, s_lon = float(start.get("lat", 0.0)), float(start.get("lon", 0.0))
    e_lat, e_lon = float(end.get("lat", s_lat)), float(end.get("lon", s_lon))

    # Extract ML context for blending (defaults to no adjustment)
    ml_risk    = float((safety_context or {}).get("ml_risk", 0.0))
    crime_risk = float((safety_context or {}).get("crime_risk", 0.0))

    # Deflection magnitude proportional to trip length
    direct_dist_km = max(1.0, math.sqrt((e_lat - s_lat) ** 2 + (e_lon - s_lon) ** 2) * 111)
    deflection_km = max(0.5, direct_dist_km * 0.15)

    # Three route strategies: direct, left-deflected, right-deflected
    strategies = [
        {"via": None, "name": "Safest Choice",      "geom_risk": 0.20},
        {"via":  90,  "name": "Secure Urban Path",  "geom_risk": 0.45},
        {"via": -90,  "name": "Quick Alternative",  "geom_risk": 0.75},
    ]

    final_routes = []
    for s in strategies:
        if s["via"] is not None:
            vl, vn = _deflect_midpoint(s_lat, s_lon, e_lat, e_lon, s["via"], deflection_km)
            result = _fetch_ors_route(s_lon, s_lat, e_lon, e_lat, via_lon=vn, via_lat=vl)
            if result is None:
                result = _fetch_osrm_route(s_lon, s_lat, e_lon, e_lat, via_lon=vn, via_lat=vl)
            if result is None:
                result = _straight_line_fallback(s_lat, s_lon, e_lat, e_lon, via_lat=vl, via_lon=vn)
        else:
            result = _fetch_ors_route(s_lon, s_lat, e_lon, e_lat)
            if result is None:
                result = _fetch_osrm_route(s_lon, s_lat, e_lon, e_lat)
            if result is None:
                result = _straight_line_fallback(s_lat, s_lon, e_lat, e_lon)

        context_risk = _contextual_route_risk(s_lat, s_lon, e_lat, e_lon)
        if context_risk:
            result["risk_weight"] = round(max(result["risk_weight"], context_risk), 2)
            result["context_risk"] = round(context_risk, 2)

        # Blend geometry risk with XGBoost output
        geom_risk = s["geom_risk"]
        context_risk = float(result.get("context_risk") or 0.0)
        blended_base = max(geom_risk, context_risk)
        if safety_context:
            blended = blended_base * 0.5 + ml_risk * 0.3 + crime_risk * 0.2
        else:
            blended = blended_base

        final_routes.append({
            "name":         s["name"],
            "distance_km":  result["distance_km"],
            "eta_minutes":  result["eta_minutes"],
            "risk_weight":  round(float(min(0.99, blended)), 2),
            "coordinates":  result["coordinates"],
            "context_risk":  result.get("context_risk"),
            "ml_context": {
                "ml_risk":    round(ml_risk, 2),
                "crime_risk": round(crime_risk, 2),
                "blended":    round(blended, 2),
            } if safety_context else None,
        })

    return final_routes
