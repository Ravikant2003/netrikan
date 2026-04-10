from typing import Dict, Any
import os
import joblib
from datetime import datetime
from pathlib import Path
import math
import pandas as pd
import numpy as np
from utils.logger import get_logger
from utils.crime_api import crime_score
from utils.maps_api import get_route

logger = get_logger(__name__)

# Static paths for the one XGBoost model
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "xgboost_risk_model.pkl"
SCALER_PATH = MODEL_DIR / "feature_scaler.pkl"
FEATURE_COLS_PATH = MODEL_DIR / "feature_cols.pkl"

class XGBoostPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = None
        self._load_model()

    def _load_model(self):
        try:
            if MODEL_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
            else:
                logger.warning(f"Model file not found at {MODEL_PATH}")

            if SCALER_PATH.exists():
                self.scaler = joblib.load(SCALER_PATH)
            else:
                logger.warning(f"Scaler file not found at {SCALER_PATH}")

            if FEATURE_COLS_PATH.exists():
                self.feature_cols = joblib.load(FEATURE_COLS_PATH)
            else:
                logger.warning(f"Feature columns file not found at {FEATURE_COLS_PATH}")
        except Exception as e:
            logger.error(f"Error loading XGBoost model components: {e}")

    def predict(self, latitude: float, longitude: float, speed: float, hour: int, severity: str) -> float:
        if self.model is None or self.scaler is None or self.feature_cols is None:
            logger.debug("Predictor components not fully loaded, using fallback.")
            return self._fallback(latitude, longitude, speed, hour, severity)
        
        severity_map = {'low': 0, 'medium': 1, 'high': 2}
        sev_val = severity_map.get(severity.lower(), 0)
        
        # This is a placeholder for the exact 8 features expected by the pkl
        # We use standard normalization if the predictor was trained that way
        features = [[latitude, longitude, speed, np.sin(hour), np.cos(hour), 0, 0, sev_val]]
        
        try:
            df = pd.DataFrame(features, columns=self.feature_cols)
            scaled = self.scaler.transform(df)
            return float(self.model.predict(scaled)[0])
        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}")
            return self._fallback(latitude, longitude, speed, hour, severity)

    def _fallback(self, lat, lon, spd, hr, sev):
        # Heuristic-based fallback
        risk = 0.2
        if 22 <= hr or hr < 6: risk += 0.3
        if sev == 'high': risk += 0.4
        return min(0.95, risk)

predictor = XGBoostPredictor()

class Layer1Monitoring:
    def preprocess(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        destination = payload.get("destination") or {}
        return {
            "latitude": float(payload.get("latitude", 0.0)),
            "longitude": float(payload.get("longitude", 0.0)),
            "destination": destination,
            "time_of_day": payload.get("time_of_day", "day"),
            "speed": float(payload.get("speed", 0.0)),
            "severity": payload.get("severity", "low"),
            "route_deviation": bool(payload.get("route_deviation", False)),
            "text_signal": payload.get("text_signal", ""),
            "is_user_alone": bool(payload.get("is_user_alone", True)),
            "safe_zones": payload.get("safe_zones") or [],
            "guardians": payload.get("guardians") or [],
            "timestamp": datetime.now().isoformat()
        }

    def get_safety_index(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hour = datetime.now().hour
        
        # 1. ML Risk Score
        ml_risk = predictor.predict(
            data["latitude"], data["longitude"], data["speed"], hour, data["severity"]
        )
        
        # 2. Crime Risk Score
        crime_risk = crime_score(data["latitude"], data["longitude"])
        
        # 3. Route Risk Score
        start = {"lat": data["latitude"], "lon": data["longitude"]}
        destination = data.get("destination") or start
        route_analysis = get_route(start, destination)
        
        # 4. Emergency Anomaly Score
        emergency_data = self._get_emergency_anomaly(data)

        # 5. Geofence/Safe-zone context
        safe_zone_status = self._safe_zone_status(data)
        
        # Deterministic combination for quick level assessment
        # (Fine-grained weighted risk will be handled in Layer 2)
        combined_risk = max(ml_risk, crime_risk, route_analysis["risk_weight"])
        if emergency_data["level"] == "CRITICAL":
            combined_risk = max(combined_risk, 0.9)
            
        level = "SAFE"
        if combined_risk > 0.7: level = "CRITICAL"
        elif combined_risk > 0.4: level = "WARNING"
            
        return {
            "risk_score": round(float(ml_risk), 2),
            "crime_score": round(float(crime_risk), 2),
            "route_risk": round(float(route_analysis["risk_weight"]), 2),
            "emergency_anomaly": emergency_data,
            "safe_zone_status": safe_zone_status,
            "safety_level": level,
            "combined_risk_score": round(float(combined_risk), 2),
            "thresholds": {"safe": 0.4, "warning": 0.7}
        }

    def _safe_zone_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        zones = data.get("safe_zones") or []
        if not isinstance(zones, list) or len(zones) == 0:
            return {
                "zone_count": 0,
                "in_safe_zone": False,
                "nearest_distance_m": None,
                "nearest_zone_name": None,
            }

        lat = float(data.get("latitude", 0.0))
        lon = float(data.get("longitude", 0.0))

        nearest_d = None
        nearest_name = None
        in_any = False

        for z in zones:
            try:
                zlat = float(z.get("lat"))
                zlon = float(z.get("lon"))
                radius_m = float(z.get("radius_meters", 250))
                name = str(z.get("name", "Safe Zone"))
            except Exception:
                continue

            d = self._haversine_m(lat, lon, zlat, zlon)
            if nearest_d is None or d < nearest_d:
                nearest_d = d
                nearest_name = name
            if d <= radius_m:
                in_any = True

        return {
            "zone_count": len(zones),
            "in_safe_zone": bool(in_any),
            "nearest_distance_m": None if nearest_d is None else round(float(nearest_d), 1),
            "nearest_zone_name": nearest_name,
        }

    def _haversine_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000.0
        p1 = math.radians(lat1)
        p2 = math.radians(lat2)
        dlat = p2 - p1
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
        return 2 * r * math.asin(math.sqrt(a))

    def _get_emergency_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        route_deviation = data.get("route_deviation", False)
        text_signal = str(data.get("text_signal", "")).lower()
        speed = data.get("speed", 0.0)
        safe_zone_status = data.get("safe_zone_status")  # may not exist in Layer1 data
        safe_zones = data.get("safe_zones") or []

        critical_terms = {"help", "save me", "emergency", "danger", "unsafe", "sos", "attack"}
        has_distress_signal = any(term in text_signal for term in critical_terms)
        anomaly_score = 0.0
        anomaly_score += 0.5 if route_deviation else 0.0
        anomaly_score += 0.7 if has_distress_signal else 0.0
        anomaly_score += 0.1 if speed > 90 else 0.0
        # Mild boost if user is outside any configured safe zone (if zones are configured)
        if isinstance(safe_zones, list) and len(safe_zones) > 0:
          try:
            status = self._safe_zone_status(data)
            anomaly_score += 0.15 if not status.get("in_safe_zone", False) else 0.0
          except Exception:
            pass

        level = "NONE"
        if anomaly_score >= 0.7:
            level = "CRITICAL"
        elif anomaly_score >= 0.3:
            level = "ELEVATED"

        return {
            "level": level,
            "anomaly_score": round(anomaly_score, 2)
        }
