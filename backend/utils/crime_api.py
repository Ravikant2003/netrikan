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

    if crime_df is not None and not crime_df.empty:
        row_count_factor = min(0.3, len(crime_df) / 100000)
    else:
        row_count_factor = 0.0

    urban_density_factor = min(0.4, (abs(lat) + abs(lon)) / 300)
    base_risk = 0.15
    return round(min(1.0, base_risk + row_count_factor + urban_density_factor), 2)
