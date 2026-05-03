import pandas as pd
import os
from config import settings
from utils.logger import get_logger

try:
    import h3
except Exception:
    h3 = None

logger = get_logger("CrimeAPI")

crime_df = None
crime_h3 = None
crime_total = 0


def load_crime_data():
    global crime_df, crime_h3, crime_total
    if crime_df is None:
        try:
            # Note: Ensure the path is correct in settings
            crime_df = pd.read_csv(settings.CRIME_DATA_PATH)
            logger.info("Crime dataset loaded successfully")
            crime_h3 = None
            crime_total = 0
            _build_h3_index()
        except Exception as e:
            logger.warning(f"Could not load crime data: {e}")
            crime_df = pd.DataFrame()
    return crime_df


def _build_h3_index() -> None:
    global crime_h3, crime_total
    if h3 is None or crime_df is None or crime_df.empty:
        return

    lat_col = None
    lon_col = None
    for cand in ("lat", "latitude", "LAT", "Latitude"):
        if cand in crime_df.columns:
            lat_col = cand
            break
    for cand in ("lon", "lng", "longitude", "LON", "Longitude"):
        if cand in crime_df.columns:
            lon_col = cand
            break

    if not lat_col or not lon_col:
        return

    res = int(os.environ.get("NETRIKAN_CRIME_H3_RES", "8"))
    counts = {}
    total = 0
    for _, row in crime_df.iterrows():
        try:
            lat = float(row[lat_col])
            lon = float(row[lon_col])
        except Exception:
            continue
        try:
            cell = h3.geo_to_h3(lat, lon, res)
        except Exception:
            continue
        counts[cell] = counts.get(cell, 0) + 1
        total += 1

    if counts:
        crime_h3 = {
            "res": res,
            "counts": counts,
        }
        crime_total = total


def crime_score(lat: float, lon: float) -> float:
    """
    Compute a heuristic crime risk score based on location.
    Uses geospatial analysis for better accuracy.
    (Spatial ML can replace this later for production.)
    """
    load_crime_data()

    if crime_h3 and h3 is not None:
        try:
            cell = h3.geo_to_h3(lat, lon, crime_h3["res"])
            count = crime_h3["counts"].get(cell, 0)
            density = count / max(1, crime_total)
            return round(min(1.0, 0.1 + density * 10.0), 2)
        except Exception:
            pass

    if crime_df is not None and not crime_df.empty:
        row_count_factor = min(0.3, len(crime_df) / 100000)
    else:
        row_count_factor = 0.0

    # Density factor based on coordinates (heuristic)
    urban_density_factor = min(0.4, (abs(lat) + abs(lon)) / 300)
    base_risk = 0.15
    return round(min(1.0, base_risk + row_count_factor + urban_density_factor), 2)
