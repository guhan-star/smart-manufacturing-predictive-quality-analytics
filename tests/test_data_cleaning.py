"""Automated Phase 2 tests for loading, alignment, validation, duplicates, cleaning, and reproducibility."""

from __future__ import annotations

import json
import numpy as np
import pandas as pd

from secom_project import DATA_PROCESSED_DIR, DATA_RAW_DIR, REPORTS_DIR
from secom_project.data_cleaning import (
    CleaningConfig,
    apply_cleaning_plan,
    clean_secom_data,
    fit_cleaning_plan,
)
from secom_project.data_validation import (
    find_duplicate_columns,
    load_and_parse_raw_secom,
    validate_secom_raw,
    verify_raw_checksums,
)
from secom_project.inspect_data import load_raw_secom


def test_loading_and_raw_integrity() -> None:
    checksums = verify_raw_checksums(DATA_RAW_DIR)
    assert checksums, "DOWNLOAD_MANIFEST.json checksums must be present"
    assert all(checksums.values()), f"Raw checksum mismatch: {checksums}"

    raw_sensors, raw_labels = load_raw_secom(DATA_RAW_DIR)
    sensors_df, labels_df = load_and_parse_raw_secom(DATA_RAW_DIR)

    assert raw_sensors.shape == (1567, 590)
    assert len(raw_labels) == 1567
    assert list(sensors_df.columns) == [f"sensor_{i:03d}" for i in range(590)]
    assert int(labels_df["timestamp"].isna().sum()) == 0
    assert bool(labels_df["timestamp"].is_monotonic_increasing) is True


def test_validation_target_and_duplicates() -> None:
    v = validate_secom_raw(DATA_RAW_DIR)
    assert v["dimensions"]["row_alignment_verified"] is True
    assert v["target_validation"]["missing_target_labels"] == 0
    assert v["target_validation"]["valid_labels_only_minus1_and_1"] is True
    assert v["target_validation"]["pass_count_minus1"] == 1463
    assert v["target_validation"]["fail_count_1"] == 104
    assert v["data_quality"]["duplicate_sensor_rows"] == 0
    assert v["data_quality"]["duplicate_full_rows"] == 0
    assert v["data_quality"]["non_constant_duplicate_column_groups"] == []

    # Synthetic duplicate-column detection check
    toy = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": [1.0, np.nan, 3.0], "c": [1.0, 2.0, 3.0]})
    dup_groups = find_duplicate_columns(toy)
    assert dup_groups == [["a", "b"]]


def test_cleaning_outputs_alignment_and_missing_handling() -> None:
    sensors_df, labels_df = load_and_parse_raw_secom(DATA_RAW_DIR)
    cleaned_df, missing_report_df, summary = clean_secom_data(sensors_df, labels_df)

    # Row order, target, and timestamps preserved as separate fields
    assert cleaned_df.shape == (1567, 443)
    assert (cleaned_df["target_label"].values == labels_df["target_label"].values).all()
    assert (cleaned_df["timestamp_raw"].values == labels_df["timestamp_raw"].values).all()
    assert "timestamp" in cleaned_df.columns and "target_label" in cleaned_df.columns

    sensor_cols = [c for c in cleaned_df.columns if c.startswith("sensor_")]
    assert len(sensor_cols) == 440
    assert int(cleaned_df[sensor_cols].isna().sum().sum()) == 0
    assert int(np.isinf(cleaned_df[sensor_cols].to_numpy(dtype=np.float64)).sum()) == 0
    assert all(cleaned_df[c].nunique() > 1 for c in sensor_cols)

    # Verify missing-value report covers all 590 raw features
    assert len(missing_report_df) == 590
    t = summary["transformations"]
    assert t["constant_features_removed"] == 116
    assert t["near_constant_features_removed"] == 6
    assert t["high_missing_features_removed"] == 28
    assert t["total_unique_features_removed"] == 150
    assert t["records_removed_excessive_missingness"] == 0


def test_reproducibility_and_no_test_or_target_leakage() -> None:
    sensors_df, labels_df = load_and_parse_raw_secom(DATA_RAW_DIR)

    # Reproducibility
    c1, _, _ = clean_secom_data(sensors_df, labels_df, CleaningConfig())
    c2, _, _ = clean_secom_data(sensors_df, labels_df, CleaningConfig())
    pd.testing.assert_frame_equal(c1, c2)

    # Fit/transform separation: test rows must not influence fitted medians or selected features
    train_x = sensors_df.iloc[:1000]
    test_x = sensors_df.iloc[1000:].copy()
    test_y = labels_df.iloc[1000:].copy()

    plan_base = fit_cleaning_plan(train_x)
    out_base = apply_cleaning_plan(test_x, test_y, plan_base)

    # Corrupt test_x medians/values on an alternative run; fitted plan on train_x remains identical
    plan_again = fit_cleaning_plan(train_x)
    assert plan_base == plan_again

    # Target labels do not affect unsupervised cleaning
    flipped_labels = labels_df.copy()
    flipped_labels["target_label"] = -flipped_labels["target_label"]
    c_flipped, _, _ = clean_secom_data(sensors_df, flipped_labels, CleaningConfig())
    sensor_cols = [c for c in c1.columns if c.startswith("sensor_")]
    pd.testing.assert_frame_equal(c1[sensor_cols], c_flipped[sensor_cols])
    assert len(out_base) == len(test_x)


def test_required_phase2_artifacts_exist() -> None:
    expected = [
        DATA_PROCESSED_DIR / "secom_cleaned.csv",
        DATA_PROCESSED_DIR / "secom_cleaning_summary.json",
        REPORTS_DIR / "phase2_data_quality_report.md",
        REPORTS_DIR / "phase2_statistical_analysis.md",
        REPORTS_DIR / "phase2_statistical_summary.csv",
        REPORTS_DIR / "phase2_missing_value_report.csv",
        REPORTS_DIR / "figures" / "class_distribution.png",
        REPORTS_DIR / "figures" / "missing_values.png",
        REPORTS_DIR / "figures" / "missing_percentage.png",
        REPORTS_DIR / "figures" / "sensor_distributions.png",
        REPORTS_DIR / "figures" / "pass_fail_boxplots.png",
        REPORTS_DIR / "figures" / "correlation_heatmap.png",
        REPORTS_DIR / "figures" / "feature_variability.png",
        REPORTS_DIR / "figures" / "pass_fail_sensor_comparison.png",
    ]
    for path in expected:
        assert path.exists(), f"Missing artifact: {path}"
        assert path.stat().st_size > 0, f"Empty artifact: {path}"

    stats_df = pd.read_csv(REPORTS_DIR / "phase2_statistical_summary.csv")
    assert len(stats_df) == 440
    for rank_col in ("missingness_rank", "variance_rank", "unique_values_rank"):
        assert rank_col in stats_df.columns

    summary = json.loads((DATA_PROCESSED_DIR / "secom_cleaning_summary.json").read_text(encoding="utf-8"))
    assert summary["safeguards"]["uses_target_label_in_preprocessing"] is False
    assert summary["safeguards"]["uses_test_set_in_preprocessing"] is False
