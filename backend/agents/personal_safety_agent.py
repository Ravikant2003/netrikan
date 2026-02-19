from typing import Dict, Any
from utils.logger import get_logger
from utils.feature_engineering import build_features
from utils.crime_api import crime_score

logger = get_logger("PersonalSafetyAgent")


class PersonalSafetyAgent:
    """
    Computes Safety Index using crime + temporal factors.
    """

    def assess(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Assessing personal safety")
        
        features = build_features(context)
        crime = crime_score(features["lat"], features["lon"])

        risk_score = min(1.0, crime + 0.3 * features["night_flag"])
        risk_level = "HIGH" if risk_score > 0.6 else "LOW"

        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "explanation": "Derived from crime density and time factors",
        }

