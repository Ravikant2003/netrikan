from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    latitude: float
    longitude: float
    destination: Dict[str, Any] = Field(default_factory=dict)
    time_of_day: str = "day"
    speed: float = 0.0
    route_deviation: bool = False
    text_signal: str = ""


class SafetyResponse(BaseModel):
    risk_score: float
    risk_level: str
    explanation: str


class RouteDetails(BaseModel):
    distance_km: float
    eta_minutes: int
    risk_weight: float


class RouteResponse(BaseModel):
    recommended_route: str
    route_risk: float
    details: RouteDetails


class EmergencyResponse(BaseModel):
    level: str
    message: str


class AnalyzeResponse(BaseModel):
    decision: str
    reasons: list[str]
    safety: SafetyResponse
    route: RouteResponse
    emergency: EmergencyResponse


class RegisterUserRequest(BaseModel):
    id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AddGuardianRequest(BaseModel):
    user_id: str
    contact: str


class StatusResponse(BaseModel):
    status: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: str
    token: str
    username: str


class MeResponse(BaseModel):
    status: str
    username: str
