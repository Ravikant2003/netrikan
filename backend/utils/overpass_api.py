import math
import os
from typing import Dict, List, Optional

import httpx


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = p2 - p1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_safe_places(lat: float, lon: float, radius_m: int = 2000, limit: int = 5) -> List[Dict[str, object]]:
    if os.environ.get("NETRIKAN_NO_NETWORK", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        return []

    endpoint = os.environ.get("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter").strip()
    if not endpoint:
        return []

    query = f"""
[out:json][timeout:8];
(
        node[amenity~"^(police|hospital|clinic|pharmacy)$"](around:{radius_m},{lat},{lon});
        way[amenity~"^(police|hospital|clinic|pharmacy)$"](around:{radius_m},{lat},{lon});
        relation[amenity~"^(police|hospital|clinic|pharmacy)$"](around:{radius_m},{lat},{lon});
        node[shop="mall"](around:{radius_m},{lat},{lon});
        way[shop="mall"](around:{radius_m},{lat},{lon});
        relation[shop="mall"](around:{radius_m},{lat},{lon});
);
out center;
"""

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(endpoint, data=query)
            if resp.status_code >= 300:
                return []
            data = resp.json()
    except Exception:
        return []

    results: List[Dict[str, object]] = []
    for el in data.get("elements", []):
        tags = el.get("tags") or {}
        amenity = tags.get("amenity") or "unknown"
        name = tags.get("name") or amenity.replace("_", " ").title()

        if "lat" in el and "lon" in el:
            plat = float(el["lat"])
            plon = float(el["lon"])
        else:
            center = el.get("center") or {}
            if "lat" not in center or "lon" not in center:
                continue
            plat = float(center["lat"])
            plon = float(center["lon"])

        dist = _haversine_m(lat, lon, plat, plon)
        results.append(
            {
                "name": name,
                "amenity": amenity,
                "lat": plat,
                "lon": plon,
                "distance_m": round(dist, 1),
            }
        )

    results.sort(key=lambda r: r["distance_m"])  # type: ignore[index]
    return results[:limit]


def get_road_context(lat: float, lon: float, radius_m: int = 80) -> Optional[Dict[str, object]]:
    if os.environ.get("NETRIKAN_NO_NETWORK", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        return None

    endpoint = os.environ.get("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter").strip()
    if not endpoint:
        return None

    query = f"""
    [out:json][timeout:8];
    (
      way[highway](around:{radius_m},{lat},{lon});
    );
    out tags center 1;
    """

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(endpoint, data=query)
            if resp.status_code >= 300:
                return None
            data = resp.json()
    except Exception:
        return None

    elements = data.get("elements") or []
    if not elements:
        return None

    el = elements[0]
    tags = el.get("tags") or {}
    highway = tags.get("highway")
    lit = tags.get("lit")

    return {
        "highway": highway,
        "lit": lit,
    }
