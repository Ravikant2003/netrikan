from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class AnalyzeRequest(BaseModel):
    latitude: float
    longitude: float
    destination: Optional[Dict[str, float]] = None
    time_of_day: str = "day"
    speed: float = 0.0
    severity: str = "low"
    route_deviation: bool = False
    text_signal: str = ""
    is_user_alone: Optional[bool] = True
    safe_zones: Optional[List[Dict[str, Any]]] = None
    guardians: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class SafetyResponse(BaseModel):
    risk_score: float
    safety_level: str
    thresholds: Dict[str, float]

class AnalyzeResponse(BaseModel):
    status: str
    layer1_monitoring: SafetyResponse
    layer2_agents: Dict[str, Any]
    layer3_actions: Dict[str, Any]
    timestamp: str

class Location(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    start: Location
    destination: Location
    safety_context: Optional[Dict[str, Any]] = None


class SimulationRequest(BaseModel):
    """
    Simulation helper:
      - Provide `scenario_id` to run a built-in scenario, OR
      - Provide `steps` to run a custom step sequence.
    """
    scenario_id: Optional[str] = None
    # Use a plain dict list (instead of AnalyzeRequest) to keep test-time mocks simple.
    steps: Optional[List[Dict[str, Any]]] = None


class SimulationResponse(BaseModel):
    scenario_id: Optional[str] = None
    # Use plain dicts to keep test-time mocks simple.
    results: List[Dict[str, Any]]
