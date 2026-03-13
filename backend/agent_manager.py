from typing import Any, Dict

from agentic import AgenticSafetyOrchestrator


class AgentManager:
    """
    Executes the agentic safety orchestrator.
    """

    def __init__(self):
        self.orchestrator = AgenticSafetyOrchestrator()

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.orchestrator.run(payload)
