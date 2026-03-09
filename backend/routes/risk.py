
from fastapi import APIRouter
from agent_manager import AgentManager
from schemas import AnalyzeRequest, SafetyResponse
from utils.data_preprocessing import preprocess_input
from ml_models.predictor import predict_risk

router = APIRouter()
manager = AgentManager()

@router.post("/risk")
def risk_api(payload: AnalyzeRequest) -> SafetyResponse:
    """
    Assess risk at the given location and time using XGBoost ML model.
    """
    # Extract features from payload
    latitude = payload.latitude
    longitude = payload.longitude
    speed = payload.speed or 40  # Default speed if not provided
    time_of_day = payload.time_of_day or "12:00"
    
    # Extract hour from time_of_day
    try:
        hour = int(time_of_day.split(':')[0])
    except:
        hour = 12
    
    # Get crime severity from payload (if available)
    severity = getattr(payload, 'severity', 'low')
    
    # Use XGBoost model to predict risk score
    risk_score = predict_risk(
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        hour=hour,
        severity=severity
    )
    
    # Convert risk score to safety score (inverse: high risk = low safety)
    safety_score = 1.0 - risk_score
    
    # Build response with ML-predicted values
    risk_level = 'SAFE' if risk_score < 0.3 else ('MODERATE' if risk_score < 0.7 else 'UNSAFE')
    
    explanation = f"Risk assessment based on XGBoost ML model. " \
                  f"Time: {time_of_day} ({('Night' if hour >= 22 or hour < 6 else 'Day')}), " \
                  f"Speed: {speed}km/h, Severity: {severity.upper()}"
    
    return SafetyResponse(
        risk_score=risk_score,
        risk_level=risk_level,
        explanation=explanation
    )
