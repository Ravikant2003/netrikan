from typing import Dict, Any
from utils.logger import get_logger
from utils.maps_api import get_route

logger = get_logger("RouteRationalizationAgent")


class RouteRationalizationAgent:
    """
    Suggests safer route alternatives.
    """

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Analyzing route safety")
        
        route = get_route(
            {"lat": context["latitude"], "lon": context["longitude"]},
            context.get("destination", {}),
        )

        recommended = (
            "safer_alternate" if route["risk_weight"] > 0.5 else "current_route"
        )

        return {
            "recommended_route": recommended,
            "route_risk": route["risk_weight"],
            "details": route,
        }

