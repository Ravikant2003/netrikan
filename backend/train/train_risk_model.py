import os
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier


def _encode_category(value: str, mapping: dict, default: int = 0) -> int:
    return mapping.get(str(value).lower(), default)


def main() -> None:
    data_path = os.environ.get("NETRIKAN_TRAIN_DATA", "").strip()
    if not data_path:
        raise SystemExit("Set NETRIKAN_TRAIN_DATA to a CSV file with labels.")

    df = pd.read_csv(data_path)
    if "label" not in df.columns:
        raise SystemExit("Training CSV must include a 'label' column (0/1).")

    # Basic feature set - extend as you collect real telemetry.
    severity_map = {"low": 0, "medium": 1, "high": 2}
    network_map = {"none": 0, "cellular": 1, "wifi": 2}
    motion_map = {"still": 0, "moving": 1}

    df["severity_code"] = df.get("severity", "low").apply(lambda v: _encode_category(v, severity_map, 0))
    df["network_code"] = df.get("network_status", "unknown").apply(lambda v: _encode_category(v, network_map, 0))
    df["motion_code"] = df.get("device_motion", "unknown").apply(lambda v: _encode_category(v, motion_map, 0))

    hour = pd.to_numeric(df.get("hour", 12), errors="coerce").fillna(12).astype(int)
    df["hour_sin"] = np.sin(hour)
    df["hour_cos"] = np.cos(hour)

    feature_cols = [
        "latitude",
        "longitude",
        "speed",
        "acceleration_mps2",
        "stop_duration_s",
        "battery_level",
        "severity_code",
        "network_code",
        "motion_code",
        "route_risk",
        "crime_score",
        "hour_sin",
        "hour_cos",
    ]

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0

    X = df[feature_cols].fillna(0.0)
    y = df["label"].astype(int)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_val_scaled)
    y_prob = model.predict_proba(X_val_scaled)[:, 1]

    val_score = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred, zero_division=0)
    recall = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_val, y_prob)
    except Exception:
        auc = 0.0

    print(
        "Validation metrics: "
        f"acc={val_score:.3f} prec={precision:.3f} recall={recall:.3f} f1={f1:.3f} auc={auc:.3f}"
    )

    version = os.environ.get("NETRIKAN_MODEL_VERSION", "").strip() or "v1"
    out_dir = Path(__file__).resolve().parents[1] / "core" / "models" / version
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, out_dir / "xgboost_risk_model.pkl")
    joblib.dump(scaler, out_dir / "feature_scaler.pkl")
    joblib.dump(feature_cols, out_dir / "feature_cols.pkl")

    meta = {
        "version": version,
        "features": feature_cols,
        "val_accuracy": val_score,
        "val_precision": precision,
        "val_recall": recall,
        "val_f1": f1,
        "val_auc": auc,
    }
    with open(out_dir / "model_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    report = {
        "version": version,
        "metrics": {
            "accuracy": val_score,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "auc": auc,
        },
        "rows": int(len(df)),
        "feature_count": len(feature_cols),
    }
    with open(out_dir / "model_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Saved model artifacts to {out_dir}")


if __name__ == "__main__":
    main()
