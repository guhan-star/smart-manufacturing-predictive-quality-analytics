"""Phase 2 — Data loading and validation reusing Phase 1 `load_raw_secom()`."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from secom_project import DATA_RAW_DIR
from secom_project.inspect_data import load_raw_secom


def verify_raw_checksums(raw_dir: Path = DATA_RAW_DIR) -> dict[str, bool]:
    """Verify raw files remain identical to Phase 1 DOWNLOAD_MANIFEST.json checksums."""
    manifest_path = raw_dir / "DOWNLOAD_MANIFEST.json"
    if not manifest_path.exists():
        return {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results: dict[str, bool] = {}
    for fname, meta in manifest.get("files", {}).items():
        fpath = raw_dir / fname
        if fpath.exists():
            actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
            results[fname] = actual == meta["sha256"]
        else:
            results[fname] = False
    return results


def load_and_parse_raw_secom(raw_dir: Path = DATA_RAW_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reuse Phase 1 `load_raw_secom()` and parse test timestamps without altering raw order."""
    sensors_df, labels_df = load_raw_secom(raw_dir)
    if len(sensors_df) != len(labels_df):
        raise ValueError(
            f"Row count mismatch: sensors={len(sensors_df)}, labels={len(labels_df)}"
        )
    parsed_labels = labels_df.copy()
    parsed_labels["timestamp"] = pd.to_datetime(
        parsed_labels["timestamp_raw"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    )
    return sensors_df, parsed_labels


def find_duplicate_columns(sensors_df: pd.DataFrame) -> list[list[str]]:
    """Detect exact duplicate columns (matching values and NaN mask)."""
    col_sigs: dict[bytes, list[str]] = {}
    for col in sensors_df.columns:
        sig = pd.util.hash_array(sensors_df[col].to_numpy()).tobytes()
        col_sigs.setdefault(sig, []).append(col)
    return [cols for cols in col_sigs.values() if len(cols) > 1]


def identify_constant_and_near_constant(
    sensors_df: pd.DataFrame, dominant_threshold: float = 0.99
) -> dict:
    """Identify strictly constant (nunique <= 1) and near-constant (>= threshold dominant value) features."""
    constant_cols: list[str] = []
    near_constant_records: list[dict] = []

    for col in sensors_df.columns:
        non_null = sensors_df[col].dropna()
        n_non_null = int(len(non_null))
        n_unique = int(non_null.nunique())
        if n_unique <= 1:
            constant_cols.append(col)
            continue
        vc = non_null.value_counts()
        top_count = int(vc.iloc[0])
        top_ratio = top_count / n_non_null if n_non_null > 0 else 0.0
        if top_ratio >= dominant_threshold:
            near_constant_records.append(
                {
                    "feature": col,
                    "n_non_null": n_non_null,
                    "n_unique": n_unique,
                    "dominant_value": float(vc.index[0]),
                    "dominant_ratio": round(float(top_ratio), 6),
                }
            )

    return {
        "constant_count": len(constant_cols),
        "constant_features": constant_cols,
        "near_constant_threshold": dominant_threshold,
        "near_constant_count": len(near_constant_records),
        "near_constant_features": near_constant_records,
    }


def compute_iqr_outlier_summary(sensors_df: pd.DataFrame, active_cols: list[str]) -> dict:
    """Quantify IQR-based (1.5*IQR and 3.0*IQR) outliers across active numeric sensors without removing them."""
    x = sensors_df[active_cols]
    q1 = x.quantile(0.25)
    q3 = x.quantile(0.75)
    iqr = q3 - q1

    # Only evaluate IQR fence where IQR > 0 to avoid flagging discrete spikes on zero-IQR columns
    positive_iqr_cols = iqr[iqr > 0].index.tolist()
    x_pos = x[positive_iqr_cols]
    q1_pos = q1[positive_iqr_cols]
    q3_pos = q3[positive_iqr_cols]
    iqr_pos = iqr[positive_iqr_cols]

    mild_mask = (x_pos < (q1_pos - 1.5 * iqr_pos)) | (x_pos > (q3_pos + 1.5 * iqr_pos))
    extreme_mask = (x_pos < (q1_pos - 3.0 * iqr_pos)) | (x_pos > (q3_pos + 3.0 * iqr_pos))

    non_null_cells = int(x_pos.notna().sum().sum())
    mild_cells = int(mild_mask.sum().sum())
    extreme_cells = int(extreme_mask.sum().sum())

    per_feature_extreme_pct = (extreme_mask.sum(axis=0) / x_pos.notna().sum(axis=0) * 100.0).sort_values(ascending=False)
    top_outlier_features = [
        {"feature": col, "extreme_outlier_pct": round(float(pct), 4)}
        for col, pct in per_feature_extreme_pct.head(10).items()
    ]

    return {
        "evaluated_active_features_with_positive_iqr": len(positive_iqr_cols),
        "zero_iqr_active_features": len(active_cols) - len(positive_iqr_cols),
        "non_null_cells_evaluated": non_null_cells,
        "iqr_1_5_outlier_cells": mild_cells,
        "iqr_1_5_outlier_pct": round(mild_cells / non_null_cells * 100.0, 4) if non_null_cells else 0.0,
        "iqr_3_0_extreme_outlier_cells": extreme_cells,
        "iqr_3_0_extreme_outlier_pct": round(extreme_cells / non_null_cells * 100.0, 4) if non_null_cells else 0.0,
        "records_with_any_extreme_outlier": int(extreme_mask.any(axis=1).sum()),
        "top_extreme_outlier_features": top_outlier_features,
    }


def validate_secom_raw(raw_dir: Path = DATA_RAW_DIR) -> dict:
    """Run all Step B validation checks on raw SECOM tables."""
    checksums = verify_raw_checksums(raw_dir)
    sensors_df, labels_df = load_and_parse_raw_secom(raw_dir)

    numeric_vals = sensors_df.to_numpy(dtype=np.float64)
    pos_inf = int(np.isposinf(numeric_vals).sum())
    neg_inf = int(np.isneginf(numeric_vals).sum())

    dup_sensor_rows = int(sensors_df.duplicated(keep="first").sum())
    dup_full_rows = int(
        pd.concat([labels_df[["target_label", "timestamp_raw"]], sensors_df], axis=1)
        .duplicated(keep="first")
        .sum()
    )
    dup_col_groups = find_duplicate_columns(sensors_df)
    cnc = identify_constant_and_near_constant(sensors_df, dominant_threshold=0.99)
    non_const_dup_groups = [
        grp for grp in dup_col_groups if grp[0] not in set(cnc["constant_features"])
    ]

    ts = labels_df["timestamp"]
    missing_ts_raw = int(labels_df["timestamp_raw"].isna().sum())
    failed_ts_parse = int(ts.isna().sum())
    is_monotonic_non_decreasing = bool(ts.is_monotonic_increasing)
    dup_ts_groups = int((ts.value_counts() > 1).sum())
    rows_sharing_ts = int(ts.duplicated(keep=False).sum())

    pass_cnt = int((labels_df["target_label"] == -1).sum())
    fail_cnt = int((labels_df["target_label"] == 1).sum())

    return {
        "raw_checksum_verification": checksums,
        "dimensions": {
            "rows": int(len(sensors_df)),
            "sensor_columns": int(sensors_df.shape[1]),
            "label_columns": 2,
            "row_alignment_verified": bool(len(sensors_df) == len(labels_df)),
        },
        "target_validation": {
            "missing_target_labels": int(labels_df["target_label"].isna().sum()),
            "valid_labels_only_minus1_and_1": bool(
                set(labels_df["target_label"].dropna().unique()).issubset({-1, 1})
            ),
            "pass_count_minus1": pass_cnt,
            "fail_count_1": fail_cnt,
            "pass_pct": round(pass_cnt / len(labels_df) * 100.0, 4),
            "fail_pct": round(fail_cnt / len(labels_df) * 100.0, 4),
            "imbalance_ratio_pass_to_fail": round(pass_cnt / fail_cnt, 4) if fail_cnt else None,
        },
        "timestamp_validation": {
            "missing_timestamp_raw": missing_ts_raw,
            "failed_timestamp_parses": failed_ts_parse,
            "format": "%d/%m/%Y %H:%M:%S",
            "min_timestamp": str(ts.min()),
            "max_timestamp": str(ts.max()),
            "is_monotonic_non_decreasing_in_raw_order": is_monotonic_non_decreasing,
            "unique_timestamps": int(ts.nunique()),
            "repeated_timestamp_groups": dup_ts_groups,
            "rows_sharing_repeated_timestamp": rows_sharing_ts,
        },
        "data_quality": {
            "sensor_dtypes": {str(k): int(v) for k, v in sensors_df.dtypes.value_counts().items()},
            "positive_inf_count": pos_inf,
            "negative_inf_count": neg_inf,
            "total_missing_sensor_cells": int(sensors_df.isna().sum().sum()),
            "overall_missing_pct": round(float(sensors_df.isna().sum().sum() / sensors_df.size * 100.0), 4),
            "features_with_any_missing": int((sensors_df.isna().sum(axis=0) > 0).sum()),
            "records_with_any_missing": int((sensors_df.isna().sum(axis=1) > 0).sum()),
            "duplicate_sensor_rows": dup_sensor_rows,
            "duplicate_full_rows": dup_full_rows,
            "duplicate_column_groups_total": len(dup_col_groups),
            "non_constant_duplicate_column_groups": non_const_dup_groups,
            "constant_and_near_constant": cnc,
        },
    }
