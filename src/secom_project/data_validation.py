"""Phase 2 — Strict data loading, checksum verification, duplicate verification, and outlier audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from secom_project import DATA_RAW_DIR
from secom_project.inspect_data import load_raw_secom

EXPECTED_RAW_FILES = ("secom.zip", "secom.data", "secom.names", "secom_labels.data")
EXPECTED_SENSOR_COLUMNS = 590


def verify_raw_checksums(raw_dir: Path = DATA_RAW_DIR, strict: bool = False) -> dict[str, bool]:
    """Verify raw files against Phase 1 DOWNLOAD_MANIFEST.json checksums.

    When `strict=True`, raises FileNotFoundError if the manifest or any expected raw file is
    missing, and raises ValueError on any SHA-256 mismatch.
    """
    manifest_path = raw_dir / "DOWNLOAD_MANIFEST.json"
    if not manifest_path.exists():
        if strict:
            raise FileNotFoundError(
                f"Missing checksum manifest: {manifest_path}. Run `python -m secom_project.download_data`."
            )
        return {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files_meta = manifest.get("files", {})
    results: dict[str, bool] = {}
    mismatched: list[str] = []

    for fname in EXPECTED_RAW_FILES:
        fpath = raw_dir / fname
        if not fpath.exists():
            if strict:
                raise FileNotFoundError(f"Missing required raw dataset file: {fpath}")
            results[fname] = False
            continue
        if fname not in files_meta or "sha256" not in files_meta[fname]:
            if strict:
                raise ValueError(f"Checksum entry for `{fname}` missing in {manifest_path}")
            results[fname] = False
            continue
        actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
        matched = actual == files_meta[fname]["sha256"]
        results[fname] = matched
        if not matched:
            mismatched.append(fname)

    if strict and mismatched:
        raise ValueError(
            f"SHA-256 checksum verification failed for raw file(s): {', '.join(mismatched)}"
        )
    return results


def load_and_parse_raw_secom(
    raw_dir: Path = DATA_RAW_DIR,
    strict: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reuse Phase 1 `load_raw_secom()` and enforce strict structural/schema validation."""
    if strict:
        verify_raw_checksums(raw_dir, strict=True)

    sensors_df, labels_df = load_raw_secom(raw_dir)

    if sensors_df.empty or labels_df.empty:
        raise ValueError("Loaded raw SECOM table is empty.")
    if len(sensors_df) != len(labels_df):
        raise ValueError(
            f"Row misalignment between secom.data ({len(sensors_df)}) and secom_labels.data ({len(labels_df)})."
        )
    if strict and sensors_df.shape[1] != EXPECTED_SENSOR_COLUMNS:
        raise ValueError(
            f"Unexpected sensor column count: expected {EXPECTED_SENSOR_COLUMNS}, got {sensors_df.shape[1]}."
        )
    if labels_df.shape[1] < 2:
        raise ValueError(
            f"Unexpected labels column count: expected >= 2, got {labels_df.shape[1]}."
        )

    # Validate sensor matrix is strictly numeric and finite (allowing NaN)
    non_numeric = [c for c in sensors_df.columns if not pd.api.types.is_numeric_dtype(sensors_df[c])]
    if non_numeric:
        raise ValueError(f"Corrupted non-numeric sensor column(s) detected: {non_numeric[:5]}")
    arr = sensors_df.to_numpy(dtype=np.float64)
    if np.isinf(arr).any():
        raise ValueError("Corrupted data: +/- infinity values detected in raw sensor matrix.")

    # Validate target labels strictly
    if labels_df["target_label"].isna().any():
        n_miss = int(labels_df["target_label"].isna().sum())
        raise ValueError(f"Missing target_label values detected: {n_miss} row(s).")
    unique_labels = set(labels_df["target_label"].unique().tolist())
    if not unique_labels.issubset({-1, 1}):
        invalid_vals = sorted(unique_labels - {-1, 1})
        raise ValueError(f"Invalid target_label value(s) detected: {invalid_vals}. Expected only {{-1, 1}}.")

    # Validate timestamps strictly
    if labels_df["timestamp_raw"].isna().any():
        n_miss_ts = int(labels_df["timestamp_raw"].isna().sum())
        raise ValueError(f"Missing timestamp_raw values detected: {n_miss_ts} row(s).")

    parsed_labels = labels_df.copy()
    parsed_labels["timestamp"] = pd.to_datetime(
        parsed_labels["timestamp_raw"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    )
    if parsed_labels["timestamp"].isna().any():
        bad_idx = parsed_labels.index[parsed_labels["timestamp"].isna()].tolist()[:5]
        raise ValueError(
            f"Invalid/unparseable timestamp_raw values at row index(es) {bad_idx}. "
            "Expected format DD/MM/YYYY HH:MM:SS."
        )

    return sensors_df, parsed_labels


def find_duplicate_columns(sensors_df: pd.DataFrame) -> list[list[str]]:
    """Identify exact duplicate columns using hashes for candidate grouping, then exact equality checks.

    Two columns are considered duplicates if and only if:
    1. Their missing-value (NaN) masks are identical (`s_a.isna().equals(s_b.isna())`), AND
    2. All observed non-null values are strictly equal (`np.array_equal`).
    """
    hash_buckets: dict[bytes, list[str]] = {}
    for col in sensors_df.columns:
        sig = pd.util.hash_array(sensors_df[col].to_numpy()).tobytes()
        hash_buckets.setdefault(sig, []).append(col)

    verified_groups: list[list[str]] = []
    for candidate_cols in hash_buckets.values():
        if len(candidate_cols) < 2:
            continue
        # Partition bucket by exact value & NaN-mask equality (protects against hash collisions)
        subgroups: list[list[str]] = []
        for col in candidate_cols:
            s_cur = sensors_df[col]
            cur_na = s_cur.isna().to_numpy()
            cur_vals = s_cur.dropna().to_numpy()
            placed = False
            for grp in subgroups:
                s_ref = sensors_df[grp[0]]
                if np.array_equal(cur_na, s_ref.isna().to_numpy()) and np.array_equal(
                    cur_vals, s_ref.dropna().to_numpy()
                ):
                    grp.append(col)
                    placed = True
                    break
            if not placed:
                subgroups.append([col])
        for grp in subgroups:
            if len(grp) > 1:
                verified_groups.append(grp)

    return verified_groups


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

    per_feature_extreme_pct = (
        extreme_mask.sum(axis=0) / x_pos.notna().sum(axis=0) * 100.0
    ).sort_values(ascending=False)
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


def validate_secom_raw(raw_dir: Path = DATA_RAW_DIR, strict: bool = True) -> dict:
    """Run all strict validation checks on raw SECOM tables and return a structured summary."""
    checksums = verify_raw_checksums(raw_dir, strict=strict)
    sensors_df, labels_df = load_and_parse_raw_secom(raw_dir, strict=strict)

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
