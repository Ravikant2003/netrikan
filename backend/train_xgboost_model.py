"""
XGBoost Risk Prediction Model Training
Trains on crime data, traffic data, and synthetic ride logs
"""
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import numpy as np

# Paths - adjust based on where script is run from
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)  # Go up one level from backend
DATASETS_DIR = os.path.join(root_dir, 'datasets')
MODELS_DIR = os.path.join(script_dir, 'ml_models')
MODEL_PATH = os.path.join(MODELS_DIR, 'xgboost_risk_model.pkl')
SCALER_PATH = os.path.join(MODELS_DIR, 'feature_scaler.pkl')
FEATURE_COLS_PATH = os.path.join(MODELS_DIR, 'feature_cols.pkl')

def load_and_prepare_data():
    """Load datasets and prepare features for training"""
    print("Loading datasets...")
    
    # Load crime data
    try:
        crimes = pd.read_csv(os.path.join(DATASETS_DIR, 'crime_data.csv'))
        print(f"Crime data shape: {crimes.shape}")
    except Exception as e:
        print(f"Warning: Could not load crime data: {e}")
        crimes = pd.DataFrame()
    
    # Load traffic data
    try:
        traffic = pd.read_csv(os.path.join(DATASETS_DIR, 'traffic_data.csv'))
        print(f"Traffic data shape: {traffic.shape}")
    except Exception as e:
        print(f"Warning: Could not load traffic data: {e}")
        traffic = pd.DataFrame()
    
    # Load synthetic ride logs
    try:
        rides = pd.read_csv(os.path.join(DATASETS_DIR, 'synthetic_ride_logs.csv'))
        print(f"Ride logs shape: {rides.shape}")
    except Exception as e:
        print(f"Warning: Could not load ride logs: {e}")
        rides = pd.DataFrame()
    
    # Prepare synthetic training data (combine info from all sources)
    training_data = []
    
    # Extract features from crime data
    if not crimes.empty and 'severity' in crimes.columns:
        for _, row in crimes.iterrows():
            # Parse timestamp - handle ISO format (e.g., "2026-03-01T18:30:00")
            timestamp = row.get('timestamp', '12:00')
            if isinstance(timestamp, str):
                if 'T' in timestamp:
                    # ISO format: extract hour from "2026-03-01T18:30:00"
                    hour = int(timestamp.split('T')[1].split(':')[0])
                else:
                    # Simple format: "HH:MM"
                    hour = int(timestamp.split(':')[0])
            else:
                hour = 12
            
            training_data.append({
                'latitude': row.get('lat', 12.9716),
                'longitude': row.get('lon', 77.5946),
                'hour': hour,
                'severity': row.get('severity', 'low'),
                'speed': 30,  # Average city speed
                'risk_score': min(0.9, (1.0 if row.get('severity') == 'high' else 0.5 if row.get('severity') == 'medium' else 0.2))
            })
    
    # Extract features from traffic data
    if not traffic.empty:
        for _, row in traffic.iterrows():
            training_data.append({
                'latitude': row.get('latitude', 12.9716),
                'longitude': row.get('longitude', 77.5946),
                'hour': row.get('hour', 12),
                'severity': row.get('congestion_level', 'low'),
                'speed': max(5, row.get('average_speed', 30)),
                'risk_score': min(0.8, row.get('average_speed', 30) / 100)  # Higher speed = lower risk in traffic
            })
    
    # If no real data, generate synthetic training data
    if len(training_data) < 50:
        print("Generating synthetic training data...")
        np.random.seed(42)
        for _ in range(200):
            hour = np.random.randint(0, 24)
            lat = 12.9716 + np.random.normal(0, 0.1)
            lon = 77.5946 + np.random.normal(0, 0.1)
            speed = np.random.randint(10, 80)
            
            # Risk increases at night (22-6am), in certain areas, with high speed
            night_risk = 0.6 if 22 <= hour or hour < 6 else 0.1
            speed_risk = min(0.7, speed / 100)
            location_risk = 0.3 if abs(lat - 12.95) < 0.05 else 0.1
            
            risk = min(1.0, night_risk + speed_risk * 0.3 + location_risk)
            
            training_data.append({
                'latitude': lat,
                'longitude': lon,
                'hour': hour,
                'severity': np.random.choice(['low', 'medium', 'high']),
                'speed': speed,
                'risk_score': risk
            })
    
    df = pd.DataFrame(training_data)
    print(f"Final training data shape: {df.shape}")
    print(f"Risk score range: {df['risk_score'].min():.2f} - {df['risk_score'].max():.2f}")
    return df

def train_model(df):
    """Train XGBoost model"""
    print("\nPreparing features...")
    
    # Feature engineering
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['lat_norm'] = (df['latitude'] - df['latitude'].mean()) / (df['latitude'].std() + 1e-8)
    df['lon_norm'] = (df['longitude'] - df['longitude'].mean()) / (df['longitude'].std() + 1e-8)
    df['severity_numeric'] = df['severity'].map({'low': 0, 'medium': 1, 'high': 2})
    
    # Select features for model
    feature_cols = ['latitude', 'longitude', 'speed', 'hour_sin', 'hour_cos', 'lat_norm', 'lon_norm', 'severity_numeric']
    X = df[feature_cols]
    y = df['risk_score']
    
    print(f"Features: {feature_cols}")
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Train XGBoost
    print("\nTraining XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=1
    )
    
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Train R² score: {train_score:.4f}")
    print(f"Test R² score: {test_score:.4f}")
    
    return model, scaler, feature_cols

def save_model(model, scaler, feature_cols):
    """Save trained model and scaler"""
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, 'feature_cols.pkl'))
    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Scaler saved to: {SCALER_PATH}")

if __name__ == '__main__':
    df = load_and_prepare_data()
    model, scaler, feature_cols = train_model(df)
    save_model(model, scaler, feature_cols)
    print("\n✓ XGBoost model training complete!")
