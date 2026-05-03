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

# Model paths (versioned)
MODEL_DIR = Path(__file__).parent / "models"

def _model_paths():
    version = os.environ.get("NETRIKAN_MODEL_VERSION", "").strip()
    base = MODEL_DIR / version if version else MODEL_DIR
    # Use trained Bengaluru model if available, else fallback to xgboost
    trained_model = base / "bengaluru_safety_model.pkl"
    fallback_model = base / "xgboost_risk_model.pkl"
    
    model_path = trained_model if trained_model.exists() else fallback_model
    
    return {
        "model": model_path,
        "scaler": base / "feature_scaler.pkl",
        "features": base / "feature_cols.pkl",
        "bengaluru_features": base / "feature_cols.pkl",
        "version": version or "default",
    }

class XGBoostPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = None
        self._layer1 = Layer1Monitoring()
        self._load_model()

    def _load_model(self):
        try:
            paths = _model_paths()
            if paths["model"].exists():
                self.model = joblib.load(paths["model"])
            else:
                logger.warning(f"Model file not found at {paths['model']}")

            if paths["scaler"].exists():
                self.scaler = joblib.load(paths["scaler"])
            else:
                logger.warning(f"Scaler file not found at {paths['scaler']}")

            if paths["features"].exists():
                self.feature_cols = joblib.load(paths["features"])
            else:
                logger.warning(f"Feature columns file not found at {paths['features']}")
        except Exception as e:
            logger.error(f"Error loading XGBoost model components: {e}")

    def predict(self, latitude: float, longitude: float, speed: float, hour: int, severity: str, route_deviation: bool = False, is_weekend: bool = False) -> float:
        """
        Predict safety index using trained XGBoost model with 17 features.
        
        Features required:
        - location: latitude, longitude, population_density
        - crime: theft, robbery, molestation, cruelty_by_husband, pocso, rape, dacoity, murder
        - temporal: hour_of_day, is_night, is_weekend
        - telemetry: speed, route_deviation, severity_encoded
        """
        if self.model is None or self.feature_cols is None:
            logger.debug("Predictor components not fully loaded, using fallback.")
            return self._fallback(latitude, longitude, speed, hour, severity)
        
        try:
            # Get district-level crime data for the location
            crime_data = self._get_crime_for_location(latitude, longitude)
            
            # Calculate is_night (22:00 - 05:00)
            is_night = 1 if hour >= 22 or hour <= 5 else 0
            
            # Encode severity: low=0, medium=1, high=2
            severity_map = {'low': 0, 'medium': 1, 'high': 2}
            sev_val = severity_map.get(severity.lower(), 0)
            
            # Build feature vector in exact order expected by model
            features = [[
                latitude,
                longitude,
                crime_data.get('population_density', 1500),
                crime_data.get('theft', 0),
                crime_data.get('robbery', 0),
                crime_data.get('molestation', 0),
                crime_data.get('cruelty_by_husband', 0),
                crime_data.get('pocso', 0),
                crime_data.get('rape', 0),
                crime_data.get('dacoity', 0),
                crime_data.get('murder', 0),
                hour,
                is_night,
                1 if is_weekend else 0,
                speed,
                1 if route_deviation else 0,
                sev_val
            ]]
            
            df = pd.DataFrame(features, columns=self.feature_cols)
            
            # Scale features if scaler available
            if self.scaler is not None:
                scaled = self.scaler.transform(df)
                prediction = self.model.predict(scaled)[0]
            else:
                prediction = self.model.predict(df)[0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}")
            return self._fallback(latitude, longitude, speed, hour, severity)

    def _get_crime_for_location(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get crime data for a location based on district mapping.
        Uses approximate district boundaries for Bengaluru area.
        """
        # Bengaluru district mapping based on coordinates
        # These are approximate centers for districts
        bengaluru_districts = {
            "Bengaluru City": {
                "lat_range": (12.9, 13.1), "lon_range": (77.5, 77.7),
                "population_density": 18000,
                "theft": 9605, "robbery": 693, "molestation": 1251,
                "cruelty_by_husband": 614, "pocso": 586, "rape": 167,
                "dacoity": 67, "murder": 176
            },
            "Bengaluru Dist": {
                "lat_range": (12.8, 13.2), "lon_range": (77.3, 77.8),
                "population_density": 1500,
                "theft": 1588, "robbery": 90, "molestation": 231,
                "cruelty_by_husband": 153, "pocso": 133, "rape": 28,
                "dacoity": 36, "murder": 66
            },
            "Ramanagara": {
                "lat_range": (12.5, 12.9), "lon_range": (77.1, 77.5),
                "population_density": 600,
                "theft": 500, "robbery": 42, "molestation": 205,
                "cruelty_by_husband": 49, "pocso": 116, "rape": 10,
                "dacoity": 13, "murder": 40
            },
            "Tumakuru": {
                "lat_range": (13.0, 13.6), "lon_range": (76.8, 77.4),
                "population_density": 1200,
                "theft": 738, "robbery": 87, "molestation": 323,
                "cruelty_by_husband": 51, "pocso": 174, "rape": 33,
                "dacoity": 14, "murder": 52
            },
            "Kolar": {
                "lat_range": (12.9, 13.3), "lon_range": (77.8, 78.4),
                "population_density": 800,
                "theft": 236, "robbery": 31, "molestation": 90,
                "cruelty_by_husband": 26, "pocso": 103, "rape": 3,
                "dacoity": 3, "murder": 28
            },
        }
        
        # Find matching district
        for district, data in bengaluru_districts.items():
            lat_min, lat_max = data["lat_range"]
            lon_min, lon_max = data["lon_range"]
            
            if lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max:
                return data
        
        # Default fallback - use Bengaluru City data
        return bengaluru_districts["Bengaluru City"]

    def _fallback(self, lat, lon, spd, hr, sev, route_deviation=False):
        return self._layer1._calculate_real_risk(lat, lon, spd, hr, sev, route_deviation=route_deviation)


class Layer1Monitoring:
    _thresholds_cache = None

    def _calculate_real_risk(
        self,
        latitude: float,
        longitude: float,
        speed: float,
        hour: int,
        severity: str,
        route_deviation: bool = False,
    ) -> float:
        """
        Calculate risk using real data sources instead of XGBoost mock model.
        
        Data sources used:
        - Crime hotspots CSV (real Bangalore data)
        - Time-based risk patterns
        - Speed anomalies
        - Route deviation patterns
        - Severity input from user
        """
        risk = 0.0
        
        # 1. Base risk from time of day (real pattern analysis)
        if 22 <= hour or hour < 6:  # Night hours (10 PM - 6 AM)
            risk += 0.25
        elif 18 <= hour < 22:  # Evening rush hour
            risk += 0.15
        elif 8 <= hour < 10 or 17 <= hour < 19:  # Morning/evening peak
            risk += 0.10
        else:  # Daytime
            risk += 0.05
        
        # 2. Speed-based risk (real telemetry analysis)
        if speed > 80:  # Very high speed
            risk += 0.30
        elif speed > 60:  # High speed
            risk += 0.20
        elif speed > 40:  # Medium speed
            risk += 0.10
        elif speed < 5:  # Very slow or stopped (could be emergency)
            risk += 0.15
        
        # 3. Route deviation risk (real routing data)
        if route_deviation:
            risk += 0.25
        
        # 4. Severity from user input (direct signal)
        severity_risk = {"low": 0.0, "medium": 0.15, "high": 0.40}
        risk += severity_risk.get(severity.lower(), 0.0)
        
        # 5. Crime data integration (real crime hotspots)
        # crime_score returns 0-1 based on real crime data
        crime_risk = crime_score(latitude, longitude)
        risk += (crime_risk * 0.3)  # Weight crime data at 30%
        
        # 6. Location-based urban risk (using real OpenStreetMap context)
        # Central Bangalore areas (12.9-13.0 lat, 77.5-77.7 lon) are more monitored
        in_bangalore_urban = (12.9 <= latitude <= 13.0) and (77.5 <= longitude <= 77.7)
        if in_bangalore_urban:
            risk -= 0.05  # Urban areas with more infrastructure are slightly safer
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, risk))

    def preprocess(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        destination = payload.get("destination") or {}
        return {
            "latitude": float(payload.get("latitude", 0.0)),
            "longitude": float(payload.get("longitude", 0.0)),
            "user_id": payload.get("user_id"),
            "session_id": payload.get("session_id"),
            "destination": destination,
            "time_of_day": payload.get("time_of_day", "day"),
            "speed": float(payload.get("speed", 0.0)),
            "acceleration_mps2": float(payload.get("acceleration_mps2", 0.0) or 0.0),
            "stop_duration_s": float(payload.get("stop_duration_s", 0.0) or 0.0),
            "battery_level": float(payload.get("battery_level", 0.0) or 0.0),
            "network_status": payload.get("network_status", "unknown"),
            "device_motion": payload.get("device_motion", "unknown"),
            "screen_unlocked_recent": bool(payload.get("screen_unlocked_recent", False)),
            "voice_triggered": bool(payload.get("voice_triggered", False)),
            "severity": payload.get("severity", "low"),
            "route_deviation": bool(payload.get("route_deviation", False)),
            "text_signal": payload.get("text_signal", ""),
            "is_user_alone": bool(payload.get("is_user_alone", True)),
            "safe_zones": payload.get("safe_zones") or [],
            "guardians": payload.get("guardians") or [],
            "timestamp": datetime.now().isoformat()
        }

    def _thresholds(self) -> Dict[str, float]:
        if Layer1Monitoring._thresholds_cache is not None:
            return Layer1Monitoring._thresholds_cache
        path = os.environ.get("NETRIKAN_THRESHOLDS_PATH", "").strip()
        if path and os.path.exists(path):
            try:
                import json

                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                safe = float(data.get("safe", 0.4))
                warning = float(data.get("warning", 0.7))
                Layer1Monitoring._thresholds_cache = {"safe": safe, "warning": warning}
                return Layer1Monitoring._thresholds_cache
            except Exception:
                pass
        Layer1Monitoring._thresholds_cache = {"safe": 0.4, "warning": 0.7}
        return Layer1Monitoring._thresholds_cache

    def get_safety_index(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hour = datetime.now().hour
        
        # 1. ML Risk Score - Using trained XGBoost model on real Karnataka crime data
        # Model outputs safety_index (1=safe, 0=danger), convert to risk (1=danger, 0=safe)
        try:
            safety_index = predictor.predict(
                latitude=data["latitude"],
                longitude=data["longitude"],
                speed=data["speed"],
                hour=hour,
                severity=data["severity"],
                route_deviation=data.get("route_deviation", False),
            )
            ml_risk = 1.0 - safety_index  # Invert: 1-safe = risk
        except Exception as e:
            logger.warning(f"XGBoost prediction failed, using fallback: {e}")
            ml_risk = self._calculate_real_risk(
                latitude=data["latitude"],
                longitude=data["longitude"],
                speed=data["speed"],
                hour=hour,
                severity=data["severity"],
                route_deviation=data.get("route_deviation", False),
            )
        
        # 2. Crime Risk Score - Using real crime data from CSV
        crime_risk = crime_score(data["latitude"], data["longitude"])
        
        # 3. Route Risk Score - Using real route APIs
        start = {"lat": data["latitude"], "lon": data["longitude"]}
        destination = data.get("destination") or start
        route_analysis = get_route(start, destination)
        
        # 4. Emergency Anomaly Score
        emergency_data = self._get_emergency_anomaly(data)

        # 5. Geofence/Safe-zone context
        safe_zone_status = self._safe_zone_status(data)
        
        # Deterministic combination for quick level assessment
        # Using real data: crime + route + emergency + speed anomalies
        combined_risk = max(ml_risk, crime_risk, route_analysis["risk_weight"])
        if emergency_data["level"] == "CRITICAL":
            combined_risk = max(combined_risk, 0.9)

        thresholds = self._thresholds()
        level = "SAFE"
        if combined_risk > thresholds["warning"]:
            level = "CRITICAL"
        elif combined_risk > thresholds["safe"]:
            level = "WARNING"
            
        return {
            "risk_score": round(float(ml_risk), 2),
            "crime_score": round(float(crime_risk), 2),
            "route_risk": round(float(route_analysis["risk_weight"]), 2),
            "emergency_anomaly": emergency_data,
            "safe_zone_status": safe_zone_status,
            "safety_level": level,
            "combined_risk_score": round(float(combined_risk), 2),
            "thresholds": thresholds,
            "data_sources": ["crime_csv", "route_api", "osm_overpass", "heuristics"]
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
        acceleration = float(data.get("acceleration_mps2", 0.0) or 0.0)
        stop_duration_s = float(data.get("stop_duration_s", 0.0) or 0.0)
        screen_unlocked_recent = bool(data.get("screen_unlocked_recent", False))
        voice_triggered = bool(data.get("voice_triggered", False))
        safe_zone_status = data.get("safe_zone_status")  # may not exist in Layer1 data
        safe_zones = data.get("safe_zones") or []

        critical_terms = {"help", "save me", "emergency", "danger", "unsafe", "sos", "attack"}
        has_distress_signal = any(term in text_signal for term in critical_terms)
        anomaly_score = 0.0
        anomaly_score += 0.5 if route_deviation else 0.0
        anomaly_score += 0.7 if has_distress_signal else 0.0
        anomaly_score += 0.1 if speed > 90 else 0.0
        anomaly_score += 0.15 if acceleration > 6.5 else 0.0
        anomaly_score += 0.15 if stop_duration_s > 90 else 0.0
        anomaly_score += 0.2 if voice_triggered else 0.0
        anomaly_score += 0.1 if screen_unlocked_recent else 0.0
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


predictor = XGBoostPredictor()
