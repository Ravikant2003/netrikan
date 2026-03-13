from fastapi import APIRouter
from agent_manager import AgentManager
from config import settings
from schemas import AnalyzeRequest, EmergencyResponse
from utils.data_preprocessing import preprocess_input
from utils.notifier import notify_guardians, notify_authorities

router = APIRouter()
manager = AgentManager()

@router.post("/emergency")
def emergency_api(payload: AnalyzeRequest) -> EmergencyResponse:
    """
    Handle emergency event and notify if critical.
    """
    data = preprocess_input(payload.model_dump())
    result = manager.run(data)["emergency"]

    if settings.ENABLE_NOTIFICATIONS and result.get("level") == "CRITICAL":
        notify_guardians("Emergency detected")
        notify_authorities("Immediate action required")

    return result
