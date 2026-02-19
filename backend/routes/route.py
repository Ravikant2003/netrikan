from fastapi import APIRouter
from agent_manager import AgentManager
from utils.data_preprocessing import preprocess_input

router = APIRouter()
manager = AgentManager()


@router.post("/route")
def route_api(payload: dict):
    data = preprocess_input(payload)
    return manager.run(data)["route"]
