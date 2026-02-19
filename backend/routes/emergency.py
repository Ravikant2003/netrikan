from fastapi import APIRouter
from agent_manager import AgentManager
from utils.data_preprocessing import preprocess_input
from utils.notifier import notify_guardians, notify_authorities

router = APIRouter()
manager = AgentManager()


@router.post("/emergency")
def emergency_api(payload: dict):
    data = preprocess_input(payload)
    result = manager.run(data)["emergency"]

    if result["level"] == "CRITICAL":
        notify_guardians("Emergency detected")
        notify_authorities("Immediate action required")

    return result
