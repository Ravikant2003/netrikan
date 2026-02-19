from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger("CommunicationAgent")


class CommunicationAgent:
    """
    Central Orchestrator Agent.
    Responsible for combining outputs of all agents
    and deciding the final system action.
    """

    def orchestrate(
        self,
        safety_result: Dict[str, Any],
        route_result: Dict[str, Any],
        emergency_result: Dict[str, Any],
    ) -> Dict[str, Any]:

        logger.info("Orchestrating agent responses")

        decision = "STAY"
        reasons = []

        if emergency_result.get("level") == "CRITICAL":
            decision = "ALERT"
            reasons.append("Critical emergency detected")

        elif safety_result.get("risk_level") == "HIGH":
            decision = "REROUTE"
            reasons.append("High safety risk detected")

        else:
            reasons.append("Situation normal")

        return {
            "decision": decision,
            "reasons": reasons,
            "safety": safety_result,
            "route": route_result,
            "emergency": emergency_result,
        }
