"""Phase 4 dashboard tests: inference validation, model reload, and Streamlit AppTest smoke checks."""

from __future__ import annotations

import io

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from secom_project import MODELS_DIR, PROJECT_ROOT
from secom_project.inference import (
    build_sample_sensor_csv_bytes,
    load_selected_model_and_metadata,
    validate_and_predict_dataframe,
)


def test_dashboard_inference_valid_multi_record_shuffled_and_target_stripping() -> None:
    model, meta = load_selected_model_and_metadata(MODELS_DIR)
    sample_bytes = build_sample_sensor_csv_bytes(n_rows=25)
    sample_df = pd.read_csv(io.BytesIO(sample_bytes))
    assert sample_df.isna().sum().sum() > 0, "Sample raw rows should contain realistic NaNs for imputation"

    threshold = float(meta["selected_threshold"])
    preds_clean, warns_clean = validate_and_predict_dataframe(sample_df, model, threshold=threshold)
    assert len(preds_clean) == 25
    assert warns_clean == []
    assert np.all((preds_clean["fail_probability"] >= 0.0) & (preds_clean["fail_probability"] <= 1.0))
    assert set(preds_clean["predicted_label"]).issubset({-1, 1})

    # Reversed / shuffled column ordering must produce identical predictions
    reversed_df = sample_df[list(reversed(sample_df.columns))].copy()
    preds_rev, _ = validate_and_predict_dataframe(reversed_df, model, threshold=threshold)
    pd.testing.assert_frame_equal(preds_clean, preds_rev)

    # Adding target_label / timestamp must be stripped and yield identical predictions
    df_with_meta = sample_df.copy()
    df_with_meta["target_label"] = 1
    df_with_meta["timestamp"] = "2008-10-15 12:00:00"
    preds_meta, warns_meta = validate_and_predict_dataframe(df_with_meta, model, threshold=threshold)
    assert len(warns_meta) == 1
    pd.testing.assert_frame_equal(preds_clean, preds_meta)


def test_dashboard_inference_rejects_invalid_inputs() -> None:
    model, meta = load_selected_model_and_metadata(MODELS_DIR)
    threshold = float(meta["selected_threshold"])
    sample_df = pd.read_csv(io.BytesIO(build_sample_sensor_csv_bytes(n_rows=3)))

    with pytest.raises(ValueError, match="no rows"):
        validate_and_predict_dataframe(sample_df.iloc[0:0], model, threshold)

    with pytest.raises(ValueError, match="Missing"):
        validate_and_predict_dataframe(sample_df.drop(columns=["sensor_059"]), model, threshold)

    bad_df = sample_df.copy()
    bad_df["sensor_059"] = "corrupted_text"
    with pytest.raises(ValueError, match="Non-numeric"):
        validate_and_predict_dataframe(bad_df, model, threshold)


def test_streamlit_all_five_sections_render_without_exceptions() -> None:
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception, f"Section 1 exception: {at.exception}"

    sections = [
        "1. Project Overview",
        "2. Exploratory Data Analysis",
        "3. Predictive Model Comparison",
        "4. Interactive Prediction",
        "5. Explainability & Findings",
    ]
    for sec in sections:
        at.sidebar.radio[0].set_value(sec).run()
        assert not at.exception, f"{sec} raised exception: {at.exception}"
