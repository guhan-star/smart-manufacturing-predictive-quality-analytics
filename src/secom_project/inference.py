"""Lightweight inference and CSV input validation utilities for the Phase 4 dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from secom_project import DATA_RAW_DIR, MODELS_DIR
from secom_project.inspect_data import load_raw_secom

EXCLUDED_NON_PREDICTOR_COLS = ("target_label", "timestamp", "timestamp_raw")


def load_selected_model_and_metadata(models_dir: Path = MODELS_DIR) -> tuple[object, dict]:
    """Load the saved Phase 3 model pipeline and metadata without retraining."""
    model_path = models_dir / "selected_model.joblib"
    meta_path = models_dir / "model_metadata.json"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Saved model artifact missing: {model_path}. Run `python -m secom_project.modeling` first."
        )
    if not meta_path.exists():
        raise FileNotFoundError(f"Model metadata missing: {meta_path}.")

    model = joblib.load(model_path)
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    return model, metadata


def build_sample_sensor_csv_bytes(
    n_rows: int = 10,
    raw_dir: Path = DATA_RAW_DIR,
    models_dir: Path = MODELS_DIR,
) -> bytes:
    """Create a downloadable sample sensor CSV from the tail of raw SECOM sensors (without targets/timestamps)."""
    feature_lists = json.loads((models_dir / "feature_lists.json").read_text(encoding="utf-8"))
    kept_features: list[str] = feature_lists["kept_features"]
    sensors_df, _ = load_raw_secom(raw_dir)
    sample_df = sensors_df[kept_features].tail(n_rows).reset_index(drop=True)
    return sample_df.to_csv(index=False).encode("utf-8")


def validate_and_predict_dataframe(
    input_df: pd.DataFrame,
    model: object,
    threshold: float,
) -> tuple[pd.DataFrame, list[str]]:
    """Validate an uploaded sensor DataFrame and generate Pass/Fail predictions using `model`.

    - Never uses `target_label`, `timestamp`, or `timestamp_raw` as predictors.
    - Enforces presence and numeric type of all required kept sensor features.
    """
    if input_df is None or input_df.empty:
        raise ValueError("Uploaded CSV contains no rows.")

    warnings_list: list[str] = []
    work_df = input_df.copy()

    stripped = [c for c in EXCLUDED_NON_PREDICTOR_COLS if c in work_df.columns]
    if stripped:
        work_df = work_df.drop(columns=stripped)
        warnings_list.append(
            f"Excluded non-predictor metadata/target column(s) from model input: {', '.join(stripped)}"
        )

    prep = model.named_steps["prep"]
    required_cols = list(prep.kept_features_)
    missing_cols = [c for c in required_cols if c not in work_df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing {len(missing_cols)} required sensor column(s), starting with: {missing_cols[:8]}"
        )

    feature_df = work_df[required_cols].copy()
    non_numeric = [c for c in required_cols if not pd.api.types.is_numeric_dtype(feature_df[c])]
    if non_numeric:
        raise ValueError(
            f"Non-numeric values found in {len(non_numeric)} sensor column(s), starting with: {non_numeric[:5]}"
        )

    probs = model.predict_proba(feature_df)[:, 1]
    preds_binary = (probs >= threshold).astype(int)
    pred_labels = np.where(preds_binary == 1, 1, -1)
    risk_bands = np.where(
        probs >= threshold,
        "High Risk (Flagged Fail)",
        np.where(probs >= threshold * 0.5, "Moderate Watch", "Low Risk (Pass)"),
    )

    out_df = pd.DataFrame(
        {
            "record_index": np.arange(1, len(feature_df) + 1),
            "fail_probability": np.round(probs, 6),
            "predicted_label": pred_labels,
            "predicted_outcome": np.where(pred_labels == 1, "Fail (1)", "Pass (-1)"),
            "risk_classification": risk_bands,
        }
    )
    return out_df, warnings_list
