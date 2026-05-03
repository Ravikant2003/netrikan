import json
import os
from pathlib import Path

import pandas as pd
from sklearn.metrics import precision_recall_curve


def main() -> None:
    data_path = os.environ.get("NETRIKAN_CALIBRATION_DATA", "").strip()
    if not data_path:
        raise SystemExit("Set NETRIKAN_CALIBRATION_DATA to a CSV with label and risk_score columns.")

    df = pd.read_csv(data_path)
    if "label" not in df.columns or "risk_score" not in df.columns:
        raise SystemExit("CSV must include 'label' and 'risk_score' columns.")

    y_true = df["label"].astype(int)
    scores = df["risk_score"].astype(float)

    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    if thresholds.size == 0:
        raise SystemExit("Not enough data for calibration.")

    # Heuristic: pick warning threshold where recall >= 0.8, safe threshold where precision >= 0.7
    warning = thresholds[min(len(thresholds) - 1, max(0, (recall >= 0.8).argmax() - 1))]
    safe = thresholds[min(len(thresholds) - 1, max(0, (precision >= 0.7).argmax() - 1))]

    out_path = os.environ.get("NETRIKAN_THRESHOLDS_PATH", "").strip()
    if not out_path:
        out_path = str(Path(__file__).resolve().parents[1] / "core" / "models" / "thresholds.json")

    payload = {"safe": float(safe), "warning": float(warning)}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    report_path = str(Path(out_path).with_name("thresholds_report.json"))
    report = {
        "rows": int(len(df)),
        "safe_threshold": float(safe),
        "warning_threshold": float(warning),
        "precision_at_warning": float(precision[min(len(precision) - 1, max(0, (recall >= 0.8).argmax() - 1))]),
        "recall_at_safe": float(recall[min(len(recall) - 1, max(0, (precision >= 0.7).argmax() - 1))]),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Wrote thresholds to {out_path}: {payload}")
    print(f"Wrote calibration report to {report_path}")


if __name__ == "__main__":
    main()
