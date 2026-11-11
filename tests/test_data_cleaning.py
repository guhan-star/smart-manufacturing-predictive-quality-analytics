"""Phase 2 automated tests: strict validation, duplicate NaN-mask checks, leakage prevention, and outputs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

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


def _copy_raw_to_tmp(tmp_path: Path) -> Path:
    raw_tmp = tmp_path / "raw"
    raw_tmp.mkdir(parents=True, exist_ok=True)
    for fname in ("secom.zip", "secom.data", "secom.names", "secom_labels.data", "DOWNLOAD_MANIFEST.json"):
        shutil.copy2(DATA_RAW_DIR / fname, raw_tmp / fname)
    return raw_tmp


def test_raw_files_unmodified() -> None:
    checksums = verify_raw_checksums(DATA_RAW_DIR, strict=True)
    assert checksums
    assert all(checksums.values())


def test_strict_validation_rejects_corruptions(tmp_path: Path) -> None:
    # 1. Missing manifest
    raw_no_manifest = _copy_raw_to_tmp(tmp_path / "m1")
    (raw_no_manifest / "DOWNLOAD_MANIFEST.json").unlink()
    with pytest.raises(FileNotFoundError, match="Missing checksum manifest"):
        validate_secom_raw(raw_no_manifest, strict=True)

    # 2. Missing raw dataset file
    raw_no_data = _copy_raw_to_tmp(tmp_path / "m2")
    (raw_no_data / "secom.data").unlink()
    with pytest.raises(FileNotFoundError, match="Missing required raw dataset file"):
        validate_secom_raw(raw_no_data, strict=True)

    # 3. Checksum mismatch
    raw_bad_hash = _copy_raw_to_tmp(tmp_path / "m3")
    with (raw_bad_hash / "secom.names").open("a", encoding="utf-8") as fh:
        fh.write("\ncorrupted")
    with pytest.raises(ValueError, match="SHA-256 checksum verification failed"):
        validate_secom_raw(raw_bad_hash, strict=True)

    # 4. Row misalignment (bypassing checksum to test schema validators)
    raw_misalign = _copy_raw_to_tmp(tmp_path / "m4")
    lines = (raw_misalign / "secom_labels.data").read_text(encoding="utf-8").splitlines()
    (raw_misalign / "secom_labels.data").write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Row misalignment"):
        load_and_parse_raw_secom(raw_misalign, strict=False)

    # 5. Invalid target label
    raw_bad_lbl = _copy_raw_to_tmp(tmp_path / "m5")
    lines = (raw_bad_lbl / "secom_labels.data").read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace("-1 ", "99 ", 1)
    (raw_bad_lbl / "secom_labels.data").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid target_label"):
        load_and_parse_raw_secom(raw_bad_lbl, strict=False)

    # 6. Missing target label
    raw_miss_lbl = _copy_raw_to_tmp(tmp_path / "m6")
    lines = (raw_miss_lbl / "secom_labels.data").read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace("-1 ", "NaN ", 1)
    (raw_miss_lbl / "secom_labels.data").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing target_label"):
        load_and_parse_raw_secom(raw_miss_lbl, strict=False)

    # 7. Invalid timestamp
    raw_bad_ts = _copy_raw_to_tmp(tmp_path / "m7")
    lines = (raw_bad_ts / "secom_labels.data").read_text(encoding="utf-8").splitlines()
    lines[0] = '-1 "99/99/2008 99:99:99"'
    (raw_bad_ts / "secom_labels.data").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid/unparseable timestamp_raw"):
        load_and_parse_raw_secom(raw_bad_ts, strict=False)


def test_duplicate_column_verification_respects_nan_positions() -> None:
    df = pd.DataFrame(
        {
            "exact_1": [1.0, np.nan, 3.0, 4.0],
            "exact_2": [1.0, np.nan, 3.0, 4.0],
            "diff_nan_pos": [1.0, 3.0, np.nan, 4.0],  # same non-null values [1, 3, 4], different NaN position
            "no_nan": [1.0, 2.0, 3.0, 4.0],
        }
    )
    groups = find_duplicate_columns(df)
    assert groups == [["exact_1", "exact_2"]]


def test_clean_secom_data_dimensions_and_integrity() -> None:
    sensors_df, labels_df = load_and_parse_raw_secom(DATA_RAW_DIR, strict=True)
    cleaned_df, missing_report_df, summary = clean_secom_data(sensors_df, labels_df)

    assert sensors_df.shape == (1567, 590)
    assert cleaned_df.shape == (1567, 443)
    assert len(missing_report_df) == 590

    assert (cleaned_df["target_label"].values == labels_df["target_label"].values).all()
    assert (cleaned_df["timestamp_raw"].values == labels_df["timestamp_raw"].values).all()
    assert int((cleaned_df["target_label"] == -1).sum()) == 1463
    assert int((cleaned_df["target_label"] == 1).sum()) == 104

    sensor_cols = [c for c in cleaned_df.columns if c.startswith("sensor_")]
    assert len(sensor_cols) == 440
    assert int(cleaned_df[sensor_cols].isna().sum().sum()) == 0
    assert int(np.isinf(cleaned_df[sensor_cols].to_numpy(dtype=np.float64)).sum()) == 0
    assert all(cleaned_df[c].nunique() > 1 for c in sensor_cols)

    t = summary["transformations"]
    assert t["constant_features_removed"] == 116
    assert t["near_constant_features_removed"] == 6
    assert t["high_missing_features_removed"] == 28
    assert t["total_unique_features_removed"] == 150
    assert t["records_removed_excessive_missingness"] == 0


def test_reproducibility_and_no_test_or_target_leakage() -> None:
    sensors_df, labels_df = load_and_parse_raw_secom(DATA_RAW_DIR, strict=True)

    # 1. Exact reproducibility
    c1, _, _ = clean_secom_data(sensors_df, labels_df, CleaningConfig())
    c2, _, _ = clean_secom_data(sensors_df, labels_df, CleaningConfig())
    pd.testing.assert_frame_equal(c1, c2)

    # 2. Target-label invariance (unsupervised preprocessing ignores targets)
    flipped_labels = labels_df.copy()
    flipped_labels["target_label"] = -flipped_labels["target_label"]
    c_flipped, _, _ = clean_secom_data(sensors_df, flipped_labels, CleaningConfig())
    sensor_cols = [c for c in c1.columns if c.startswith("sensor_")]
    pd.testing.assert_frame_equal(c1[sensor_cols], c_flipped[sensor_cols])

    # 3. Genuine test-set isolation: substantial value shifts & injected missingness in test set
    train_x = sensors_df.iloc[:1000].copy()
    test_x = sensors_df.iloc[1000:].copy()
    test_y = labels_df.iloc[1000:].copy()

    plan = fit_cleaning_plan(train_x, CleaningConfig())
    test_perturbed = test_x.copy()
    # Shift non-null test values massively and inject >70% missingness into test_perturbed
    target_col = plan.kept_features[0]
    test_perturbed[target_col] = test_perturbed[target_col] + 1_000_000.0
    inject_idx = test_perturbed.index[: int(len(test_perturbed) * 0.75)]
    test_perturbed.loc[inject_idx, target_col] = np.nan

    # Re-fitting on train_x cannot change medians or selected features regardless of test corruption
    plan_check = fit_cleaning_plan(train_x, CleaningConfig())
    assert plan == plan_check
    assert target_col in plan.kept_features

    # Transforming perturbed test data fills injected NaNs using exact TRAINING median (not +1e6 test median)
    transformed_test = apply_cleaning_plan(test_perturbed, test_y, plan)
    imputed_vals = transformed_test.loc[: len(inject_idx) - 1, target_col]
    assert np.allclose(imputed_vals.to_numpy(), plan.imputation_medians[target_col])


def test_required_phase2_artifacts_exist() -> None:
    expected = [
        DATA_PROCESSED_DIR / "secom_cleaned.csv",
        DATA_PROCESSED_DIR / "secom_cleaning_summary.json",
        REPORTS_DIR / "phase2_data_quality_report.md",
        REPORTS_DIR / "phase2_statistical_analysis.md",
        REPORTS_DIR / "phase2_final_review.md",
        REPORTS_DIR / "phase2_statistical_summary.csv",
        REPORTS_DIR / "phase2_observed_vs_imputed_sensitivity.csv",
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
        assert path.exists(), f"Missing Phase 2 artifact: {path}"
        assert path.stat().st_size > 0, f"Empty Phase 2 artifact: {path}"

    stats_df = pd.read_csv(REPORTS_DIR / "phase2_statistical_summary.csv")
    assert len(stats_df) == 440
    for col in ("mannwhitney_p", "mannwhitney_p_fdr_bh", "is_raw_significant_0_05", "is_fdr_significant_0_05"):
        assert col in stats_df.columns

    sens_df = pd.read_csv(REPORTS_DIR / "phase2_observed_vs_imputed_sensitivity.csv")
    assert len(sens_df) == 440
    assert "obs_mannwhitney_p_fdr_bh" in sens_df.columns
    assert "fdr_conclusion_differs" in sens_df.columns
