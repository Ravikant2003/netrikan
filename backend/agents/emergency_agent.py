from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger("EmergencyAgent")


class EmergencyAgent:
    """
    Detects emergency situations using rule-based logic.
    """

    def detect(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Checking for emergency signals")
        
        if context.get("route_deviation") or "help" in context.get("text_signal", "").lower():
            return {
                "level": "CRITICAL",
                "message": "Emergency detected due to abnormal signals",
            }

        return {
            "level": "NONE",
            "message": "No emergency detected",
        }

