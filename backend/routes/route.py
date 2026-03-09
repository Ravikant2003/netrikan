
from fastapi import APIRouter
from agent_manager import AgentManager
from schemas import AnalyzeRequest, RouteResponse
from utils.data_preprocessing import preprocess_input

router = APIRouter()
manager = AgentManager()

@router.post("/route")
def route_api(payload: AnalyzeRequest) -> RouteResponse:
    """
    Analyze and return the best route based on payload.
    """
    data = preprocess_input(payload.model_dump())
    return manager.run(data)["route"]
