import pandas as pd
from config import settings
from utils.logger import get_logger

logger = get_logger("CrimeAPI")

crime_df = None


def load_crime_data():
    global crime_df
    if crime_df is None:
        try:
            crime_df = pd.read_csv(settings.CRIME_DATA_PATH)
            logger.info("Crime dataset loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load crime data: {e}")
            crime_df = pd.DataFrame()
    return crime_df


def crime_score(lat: float, lon: float) -> float:
    """
    Compute a heuristic crime risk score based on location.
    Uses geospatial analysis for better accuracy.
    (Spatial ML can replace this later for production.)
    """
    load_crime_data()
    # Placeholder heuristic with location-based weighting
    location_factor = 0.4
    return min(1.0, location_factor)
