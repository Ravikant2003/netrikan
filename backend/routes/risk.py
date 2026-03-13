from fastapi import APIRouter
from agent_manager import AgentManager
from schemas import AnalyzeRequest, SafetyResponse
from utils.data_preprocessing import preprocess_input

router = APIRouter()
manager = AgentManager()

@router.post("/risk")
def risk_api(payload: AnalyzeRequest) -> SafetyResponse:
    """
    Assess risk using the agentic safety ensemble.
    """
    data = preprocess_input(payload.model_dump())
    return manager.run(data)["safety"]
