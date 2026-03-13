"""
XGBoost Model Loader and Predictor
Loads pre-trained XGBoost model for risk prediction
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODELS_DIR = Path(__file__).parent
MODEL_PATH = MODELS_DIR / 'xgboost_risk_model.pkl'
SCALER_PATH = MODELS_DIR / 'feature_scaler.pkl'
FEATURE_COLS_PATH = MODELS_DIR / 'feature_cols.pkl'

class XGBoostPredictor:
    """Loads and manages XGBoost risk model"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.model = None
        self.scaler = None
        self.feature_cols = None
        # Don't load on init - load on first prediction
        self._initialized = True
    
    def _load_model(self):
        """Load saved model and scaler"""
        try:
            if MODEL_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
                print(f"✓ Loaded XGBoost model from {MODEL_PATH}")
            else:
                print(f"⚠ Model not found at {MODEL_PATH}")
                return
            
            if SCALER_PATH.exists():
                self.scaler = joblib.load(SCALER_PATH)
                print(f"✓ Loaded feature scaler from {SCALER_PATH}")
            else:
                print(f"⚠ Scaler not found at {SCALER_PATH}")
            
            if FEATURE_COLS_PATH.exists():
                self.feature_cols = joblib.load(FEATURE_COLS_PATH)
                print(f"✓ Loaded feature columns: {self.feature_cols}")
            else:
                self.feature_cols = ['latitude', 'longitude', 'speed', 'hour_sin', 'hour_cos', 'lat_norm', 'lon_norm', 'severity_numeric']
                print(f"⚠ Using default feature columns")
        
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def predict(self, latitude: float, longitude: float, speed: int, hour: int, severity: str = 'low') -> float:
        """
        Predict risk score using XGBoost model
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            speed: Vehicle speed (km/h)
            hour: Hour of day (0-23)
            severity: Crime severity level ('low', 'medium', 'high')
        
        Returns:
            Risk score between 0 and 1
        """
        # Load model on first prediction
        if self.model is None:
            self._load_model()
        
        if self.model is None or self.scaler is None:
            # Fallback to simple heuristic if model not loaded
            return self._fallback_predict(latitude, longitude, speed, hour, severity)
        
        try:
            # Feature engineering (must match training)
            hour_sin = np.sin(2 * np.pi * hour / 24)
            hour_cos = np.cos(2 * np.pi * hour / 24)
            
            # These are meant to be normalized against training data mean/std
            # For prediction, we'll use approximate values
            lat_norm = (latitude - 12.9716) / 0.05
            lon_norm = (longitude - 77.5946) / 0.05
            severity_numeric = {'low': 0, 'medium': 1, 'high': 2}.get(severity.lower(), 0)
            
            feature_values = [
                latitude,
                longitude,
                speed,
                hour_sin,
                hour_cos,
                lat_norm,
                lon_norm,
                severity_numeric,
            ]

            feature_frame = pd.DataFrame(
                [feature_values],
                columns=self.feature_cols,
            )

            # Scale features
            features_scaled = self.scaler.transform(feature_frame)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            
            # Ensure prediction is between 0 and 1
            return float(np.clip(prediction, 0.0, 1.0))
        
        except Exception as e:
            print(f"Error in prediction: {e}")
            return self._fallback_predict(latitude, longitude, speed, hour, severity)
    
    def _fallback_predict(self, latitude: float, longitude: float, speed: int, hour: int, severity: str) -> float:
        """Fallback heuristic-based prediction if model not available"""
        # Risk increases at night (22-6am)
        night_risk = 0.6 if 22 <= hour or hour < 6 else 0.1
        
        # Risk increases with high speed
        speed_risk = min(0.7, speed / 100) * 0.3
        
        # Risk based on crime severity
        severity_risk = {'low': 0.1, 'medium': 0.4, 'high': 0.7}.get(severity.lower(), 0.2)
        
        # Location-based risk (some areas more dangerous)
        location_risk = 0.3 if abs(latitude - 12.95) < 0.05 else 0.1
        
        # Combine risks
        total_risk = min(1.0, night_risk + speed_risk + severity_risk * 0.5 + location_risk * 0.3)
        
        return total_risk

# Singleton instance
_predictor = None

def get_predictor() -> XGBoostPredictor:
    """Get singleton XGBoost predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = XGBoostPredictor()
    return _predictor

def predict_risk(latitude: float, longitude: float, speed: int, hour: int, severity: str = 'low') -> float:
    """Convenience function for risk prediction"""
    return get_predictor().predict(latitude, longitude, speed, hour, severity)
