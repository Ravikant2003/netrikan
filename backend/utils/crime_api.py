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
            logger.info("Crime dataset loaded")
        except Exception as e:
            logger.warning(f"Could not load crime data: {e}")
            crime_df = pd.DataFrame()
    return crime_df


def crime_score(lat: float, lon: float) -> float:
    """
    Compute a heuristic crime risk score.
    (Spatial ML can replace this later.)
    """
    load_crime_data()
    return 0.4  # placeholder heuristic
