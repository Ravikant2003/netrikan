#!/usr/bin/env python3
"""
Train XGBoost Model for Bengaluru Safety Index Prediction
Uses real Karnataka crime data 2024 & 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_DIR = Path(__file__).parent.parent / "models"

def load_data():
    """Load prepared training data"""
    path = DATA_DIR / "bengaluru_safety_training_data.csv"
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} samples")
    return df

def prepare_features(df):
    """Prepare features for training"""
    
    # Encode categorical features
    le_severity = LabelEncoder()
    df["severity_encoded"] = le_severity.fit_transform(df["severity"])
    
    # Feature columns for model
    feature_cols = [
        "latitude", "longitude", "population_density",
        "theft", "robbery", "molestation", "cruelty_by_husband", 
        "pocso", "rape", "dacoity", "murder",
        "hour_of_day", "is_night", "is_weekend",
        "speed", "route_deviation", "severity_encoded"
    ]
    
    X = df[feature_cols].copy()
    y = df["safety_index"].values
    
    return X, y, feature_cols, le_severity

def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost model"""
    
    params = {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 200,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "random_state": 42,
    }
    
    model = xgb.XGBRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    return model

def evaluate_model(model, X, y, set_name="Test"):
    """Evaluate model performance"""
    y_pred = model.predict(X)
    
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    print(f"\n{set_name} Set Metrics:")
    print(f"  RMSE:  {rmse:.4f}")
    print(f"  MAE:   {mae:.4f}")
    print(f"  R²:    {r2:.4f}")
    
    return {"rmse": rmse, "mae": mae, "r2": r2}

def get_feature_importance(model, feature_cols):
    """Get feature importance"""
    importance = model.feature_importances_
    fi_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": importance
    }).sort_values("importance", ascending=False)
    
    print("\nTop 10 Feature Importance:")
    print(fi_df.head(10).to_string(index=False))
    
    return fi_df

def main():
    print("="*60)
    print("Bengaluru Safety Index XGBoost Training")
    print("="*60)
    
    print("\n[1/5] Loading data...")
    df = load_data()
    
    print("\n[2/5] Preparing features...")
    X, y, feature_cols, le_severity = prepare_features(df)
    print(f"  Features: {len(feature_cols)}")
    print(f"  Target range: {y.min():.4f} to {y.max():.4f}")
    
    print("\n[3/5] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42
    )
    print(f"  Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    print("\n[4/5] Training XGBoost model...")
    model = train_model(X_train, y_train, X_val, y_val)
    print("  Training complete!")
    
    print("\n[5/5] Evaluating model...")
    train_metrics = evaluate_model(model, X_train, y_train, "Train")
    val_metrics = evaluate_model(model, X_val, y_val, "Validation")
    test_metrics = evaluate_model(model, X_test, y_test, "Test")
    
    # Feature importance
    fi_df = get_feature_importance(model, feature_cols)
    
    # Save model and artifacts
    print("\n[Saving] Model and artifacts...")
    
    MODEL_DIR.mkdir(exist_ok=True)
    
    model_path = MODEL_DIR / "bengaluru_safety_model.pkl"
    scaler_path = MODEL_DIR / "feature_scaler.pkl"
    features_path = MODEL_DIR / "feature_cols.pkl"
    severity_path = MODEL_DIR / "severity_encoder.pkl"
    
    # Save model
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    # Save scaler
    scaler = StandardScaler()
    scaler.fit(X)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    
    # Save feature columns
    with open(features_path, "wb") as f:
        pickle.dump(feature_cols, f)
    
    # Save severity encoder
    with open(severity_path, "wb") as f:
        pickle.dump(le_severity, f)
    
    print(f"  Model: {model_path}")
    print(f"  Scaler: {scaler_path}")
    print(f"  Features: {features_path}")
    print(f"  Severity encoder: {severity_path}")
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)

if __name__ == "__main__":
    main()