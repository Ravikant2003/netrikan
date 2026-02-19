from typing import Dict, Any
from agents import (
    PersonalSafetyAgent,
    RouteRationalizationAgent,
    EmergencyAgent,
    CommunicationAgent,
)


class AgentManager:
    """
    Executes all agents and passes results
    to the Communication Agent.
    """

    def __init__(self):
        self.safety_agent = PersonalSafetyAgent()
        self.route_agent = RouteRationalizationAgent()
        self.emergency_agent = EmergencyAgent()
        self.communication_agent = CommunicationAgent()

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        safety = self.safety_agent.assess(payload)
        route = self.route_agent.analyze(payload)
        emergency = self.emergency_agent.detect(payload)

        return self.communication_agent.orchestrate(
            safety_result=safety,
            route_result=route,
            emergency_result=emergency,
        )
