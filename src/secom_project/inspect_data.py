"""Comprehensive Phase 1 inspection, audit, and data dictionary generator for UCI SECOM."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from secom_project import DATA_PROCESSED_DIR, DATA_RAW_DIR, DOCS_DIR, REPORTS_DIR


def load_raw_secom(raw_dir: Path = DATA_RAW_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw secom.data and secom_labels.data without altering raw values."""
    data_path = raw_dir / "secom.data"
    labels_path = raw_dir / "secom_labels.data"

    if not data_path.exists() or not labels_path.exists():
        raise FileNotFoundError(
            f"Missing raw SECOM files in {raw_dir}. Run `python -m secom_project.download_data` first."
        )

    # Space-separated values; MATLAB 'NaN' strings parsed as float NaN
    sensors_df = pd.read_csv(
        data_path,
        sep=r"\s+",
        header=None,
        na_values=["NaN", "nan", "NA", ""],
    )
    sensors_df.columns = [f"sensor_{i:03d}" for i in range(sensors_df.shape[1])]

    labels_df = pd.read_csv(
        labels_path,
        sep=r"\s+",
        header=None,
        names=["target_label", "timestamp_raw"],
        quotechar='"',
    )
    return sensors_df, labels_df


def analyze_structure_and_quality(
    sensors_df: pd.DataFrame, labels_df: pd.DataFrame
) -> dict:
    """Compute structural, missingness, duplicate, and target statistics."""
    n_rows_sensors, n_sensor_cols = sensors_df.shape
    n_rows_labels, n_label_cols = labels_df.shape

    # Target label distribution
    label_counts = labels_df["target_label"].value_counts(dropna=False).to_dict()
    label_counts = {str(k): int(v) for k, v in label_counts.items()}
    pass_count = int((labels_df["target_label"] == -1).sum())
    fail_count = int((labels_df["target_label"] == 1).sum())
    other_count = int(len(labels_df) - pass_count - fail_count)

    # Missingness
    total_cells = int(sensors_df.size)
    total_missing = int(sensors_df.isna().sum().sum())
    col_missing_counts = sensors_df.isna().sum(axis=0)
    col_missing_pct = (col_missing_counts / n_rows_sensors) * 100.0
    row_missing_counts = sensors_df.isna().sum(axis=1)
    row_missing_pct = (row_missing_counts / n_sensor_cols) * 100.0

    # Constant / all-NaN / duplicate columns
    nunique_non_null = sensors_df.nunique(dropna=True)
    all_nan_cols = col_missing_counts[col_missing_counts == n_rows_sensors].index.tolist()
    constant_cols = nunique_non_null[nunique_non_null <= 1].index.tolist()

    # Exact duplicate columns (including NaN positions)
    # Transpose hashable representation to find identical columns
    col_sigs: dict[bytes, list[str]] = {}
    for col in sensors_df.columns:
        sig = pd.util.hash_array(sensors_df[col].to_numpy()).tobytes()
        col_sigs.setdefault(sig, []).append(col)
    duplicate_col_groups = [cols for cols in col_sigs.values() if len(cols) > 1]
    # Also separate constant columns from non-constant duplicate column groups
    non_constant_dup_groups = [
        grp for grp in duplicate_col_groups if grp[0] not in constant_cols
    ]

    # Duplicate rows
    dup_sensor_rows = int(sensors_df.duplicated(keep="first").sum())
    combined_df = pd.concat([labels_df, sensors_df], axis=1)
    dup_full_rows = int(combined_df.duplicated(keep="first").sum())
    dup_sensor_and_label = int(
        pd.concat([labels_df[["target_label"]], sensors_df], axis=1)
        .duplicated(keep="first")
        .sum()
    )

    # Missingness by target class
    pass_mask = labels_df["target_label"] == -1
    fail_mask = labels_df["target_label"] == 1
    row_miss_pass = row_missing_pct[pass_mask]
    row_miss_fail = row_missing_pct[fail_mask]

    return {
        "dimensions": {
            "sensor_rows": int(n_rows_sensors),
            "sensor_columns": int(n_sensor_cols),
            "label_rows": int(n_rows_labels),
            "label_columns": int(n_label_cols),
            "row_alignment_matches": bool(n_rows_sensors == n_rows_labels),
            "uci_documented_attributes_note": (
                "UCI documentation states '591 attributes' (590 sensor columns in secom.data + 1 target/timestamp or 1-indexed count); "
                f"actual secom.data has {n_sensor_cols} columns and secom_labels.data has {n_label_cols} columns."
            ),
        },
        "target_distribution": {
            "raw_value_counts": label_counts,
            "encoding_verified": {
                "-1": "Pass (in-house line testing)",
                "1": "Fail (yield excursion / defect)",
            },
            "pass_count": pass_count,
            "pass_pct": round(pass_count / n_rows_labels * 100, 4),
            "fail_count": fail_count,
            "fail_pct": round(fail_count / n_rows_labels * 100, 4),
            "other_label_count": other_count,
            "imbalance_ratio_pass_to_fail": round(pass_count / fail_count, 4) if fail_count else None,
            "missing_labels": int(labels_df["target_label"].isna().sum()),
        },
        "missing_values": {
            "sensor_total_cells": total_cells,
            "sensor_missing_cells": total_missing,
            "sensor_missing_pct": round(total_missing / total_cells * 100, 4),
            "label_missing_cells": int(labels_df.isna().sum().sum()),
            "columns_with_any_missing": int((col_missing_counts > 0).sum()),
            "columns_complete_no_missing": int((col_missing_counts == 0).sum()),
            "columns_gt_50pct_missing": int((col_missing_pct > 50).sum()),
            "columns_gt_80pct_missing": int((col_missing_pct > 80).sum()),
            "columns_gt_90pct_missing": int((col_missing_pct > 90).sum()),
            "max_col_missing_pct": round(float(col_missing_pct.max()), 4),
            "max_col_missing_count": int(col_missing_counts.max()),
            "rows_with_any_missing": int((row_missing_counts > 0).sum()),
            "rows_complete_no_missing": int((row_missing_counts == 0).sum()),
            "row_missing_min_pct": round(float(row_missing_pct.min()), 4),
            "row_missing_median_pct": round(float(row_missing_pct.median()), 4),
            "row_missing_max_pct": round(float(row_missing_pct.max()), 4),
            "mean_row_missing_pct_pass": round(float(row_miss_pass.mean()), 4),
            "mean_row_missing_pct_fail": round(float(row_miss_fail.mean()), 4),
        },
        "feature_redundancy_and_duplicates": {
            "all_nan_columns_count": len(all_nan_cols),
            "all_nan_columns": all_nan_cols,
            "constant_columns_count": len(constant_cols),
            "constant_columns_sample": constant_cols[:20],
            "constant_columns_all": constant_cols,
            "duplicate_column_groups_total": len(duplicate_col_groups),
            "non_constant_duplicate_column_groups": non_constant_dup_groups,
            "duplicate_sensor_rows": dup_sensor_rows,
            "duplicate_sensor_plus_label_rows": dup_sensor_and_label,
            "duplicate_full_rows_incl_timestamp": dup_full_rows,
        },
    }


def analyze_timestamps(labels_df: pd.DataFrame) -> dict:
    """Inspect timestamp parsing, chronological order, duplicates, gaps, and temporal fail clustering."""
    parsed = pd.to_datetime(
        labels_df["timestamp_raw"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    )
    failed_parse = int(parsed.isna().sum())

    df_time = labels_df.copy()
    df_time["timestamp"] = parsed
    df_time["row_idx"] = np.arange(len(df_time))

    is_monotonic_non_decreasing = bool(parsed.is_monotonic_increasing)
    is_strictly_increasing = bool(parsed.is_unique and parsed.is_monotonic_increasing)

    # Check out-of-order steps
    diffs_raw_order = parsed.diff()
    negative_steps = int((diffs_raw_order < pd.Timedelta(0)).sum())
    zero_steps = int((diffs_raw_order == pd.Timedelta(0)).sum())

    # Duplicate timestamps
    dup_ts_counts = parsed.value_counts()
    dup_ts_values = dup_ts_counts[dup_ts_counts > 1]
    rows_sharing_timestamp = int(parsed.duplicated(keep=False).sum())

    # Check if shared timestamps share same label or have conflicting labels
    shared_ts_label_conflicts = 0
    if rows_sharing_timestamp > 0:
        grouped = df_time[parsed.duplicated(keep=False)].groupby("timestamp")["target_label"].nunique()
        shared_ts_label_conflicts = int((grouped > 1).sum())

    # Sort chronologically to inspect true time gaps & monthly fail rates
    df_sorted = df_time.sort_values(["timestamp", "row_idx"]).reset_index(drop=True)
    sorted_diffs = df_sorted["timestamp"].diff().dropna()

    df_sorted["year_month"] = df_sorted["timestamp"].dt.to_period("M").astype(str)
    monthly = (
        df_sorted.groupby("year_month")
        .agg(
            total=("target_label", "size"),
            fails=("target_label", lambda s: int((s == 1).sum())),
        )
        .reset_index()
    )
    monthly["fail_rate_pct"] = (monthly["fails"] / monthly["total"] * 100.0).round(2)

    # Out-of-order details (first 10 inversions if any)
    inversion_examples = []
    if negative_steps > 0:
        neg_idx = np.where(diffs_raw_order < pd.Timedelta(0))[0]
        for idx in neg_idx[:10]:
            inversion_examples.append(
                {
                    "row_index": int(idx),
                    "prev_timestamp": str(parsed.iloc[idx - 1]),
                    "curr_timestamp": str(parsed.iloc[idx]),
                    "delta_seconds": float((parsed.iloc[idx] - parsed.iloc[idx - 1]).total_seconds()),
                }
            )

    return {
        "format": "%d/%m/%Y %H:%M:%S (DD/MM/YYYY HH:MM:SS)",
        "total_rows": int(len(parsed)),
        "parsed_successfully": int(len(parsed) - failed_parse),
        "failed_to_parse": failed_parse,
        "min_timestamp": str(parsed.min()),
        "max_timestamp": str(parsed.max()),
        "total_span_days": round(float((parsed.max() - parsed.min()).total_seconds() / 86400.0), 2),
        "unique_timestamps": int(parsed.nunique()),
        "duplicate_timestamp_values": int(len(dup_ts_values)),
        "rows_sharing_a_timestamp": rows_sharing_timestamp,
        "shared_timestamp_label_conflicts": shared_ts_label_conflicts,
        "is_monotonic_increasing_in_raw_order": is_monotonic_non_decreasing,
        "is_strictly_increasing_in_raw_order": is_strictly_increasing,
        "negative_time_steps_in_raw_order": negative_steps,
        "zero_time_steps_in_raw_order": zero_steps,
        "inversion_examples": inversion_examples,
        "sorted_gap_stats_minutes": {
            "min": round(float(sorted_diffs.min().total_seconds() / 60.0), 2),
            "median": round(float(sorted_diffs.median().total_seconds() / 60.0), 2),
            "mean": round(float(sorted_diffs.mean().total_seconds() / 60.0), 2),
            "p95": round(float(sorted_diffs.quantile(0.95).total_seconds() / 60.0), 2),
            "max": round(float(sorted_diffs.max().total_seconds() / 60.0), 2),
            "max_gap_days": round(float(sorted_diffs.max().total_seconds() / 86400.0), 2),
        },
        "monthly_fail_distribution": monthly.to_dict(orient="records"),
    }


def build_data_dictionary(
    sensors_df: pd.DataFrame, labels_df: pd.DataFrame
) -> pd.DataFrame:
    """Create a complete field-level data dictionary for documented and anonymous fields."""
    n_rows = len(sensors_df)
    records = [
        {
            "field_name": "target_label",
            "source_file": "secom_labels.data",
            "source_column_index_0based": 0,
            "source_column_number_1based": 1,
            "field_category": "Documented Target Label",
            "documentation_status": "Documented in UCI SECOM metadata",
            "data_type": "int64 (categorical binary)",
            "allowed_values_or_units": "-1 = Pass, 1 = Fail (in-house line testing)",
            "missing_count": int(labels_df["target_label"].isna().sum()),
            "missing_pct": round(float(labels_df["target_label"].isna().mean() * 100), 4),
            "non_null_count": int(labels_df["target_label"].notna().sum()),
            "unique_non_null_count": int(labels_df["target_label"].nunique(dropna=True)),
            "min_value": float(labels_df["target_label"].min()),
            "max_value": float(labels_df["target_label"].max()),
            "mean_value": round(float(labels_df["target_label"].mean()), 6),
            "std_value": round(float(labels_df["target_label"].std()), 6),
            "is_constant": False,
            "notes": (
                "Official UCI API/web summary defines -1 = Pass and 1 = Fail (104 fails, 1463 passes). "
                "Note: secom.names line 46 has a known '.1' typo for '-1'."
            ),
        },
        {
            "field_name": "timestamp_raw",
            "source_file": "secom_labels.data",
            "source_column_index_0based": 1,
            "source_column_number_1based": 2,
            "field_category": "Documented Metadata Timestamp",
            "documentation_status": "Documented in UCI SECOM metadata",
            "data_type": "string -> datetime64[ns]",
            "allowed_values_or_units": "DD/MM/YYYY HH:MM:SS (test point timestamp; no timezone specified)",
            "missing_count": int(labels_df["timestamp_raw"].isna().sum()),
            "missing_pct": round(float(labels_df["timestamp_raw"].isna().mean() * 100), 4),
            "non_null_count": int(labels_df["timestamp_raw"].notna().sum()),
            "unique_non_null_count": int(labels_df["timestamp_raw"].nunique(dropna=True)),
            "min_value": None,
            "max_value": None,
            "mean_value": None,
            "std_value": None,
            "is_constant": False,
            "notes": "Timestamp associated with the specific in-house line test point; raw file is monotonically non-decreasing (0 backward steps) but has 32 repeated timestamps.",
        },
    ]

    for idx, col in enumerate(sensors_df.columns):
        series = sensors_df[col]
        miss_cnt = int(series.isna().sum())
        non_null_cnt = int(series.notna().sum())
        uniq_cnt = int(series.nunique(dropna=True))
        is_const = uniq_cnt <= 1
        records.append(
            {
                "field_name": col,
                "source_file": "secom.data",
                "source_column_index_0based": idx,
                "source_column_number_1based": idx + 1,
                "field_category": "Anonymous Process Sensor Signal",
                "documentation_status": "Anonymous (no physical name, unit, or process step in UCI release)",
                "data_type": "float64",
                "allowed_values_or_units": "Real-valued; units undisclosed; MATLAB 'NaN' denotes missing",
                "missing_count": miss_cnt,
                "missing_pct": round(miss_cnt / n_rows * 100.0, 4),
                "non_null_count": non_null_cnt,
                "unique_non_null_count": uniq_cnt,
                "min_value": round(float(series.min()), 6) if non_null_cnt > 0 else None,
                "max_value": round(float(series.max()), 6) if non_null_cnt > 0 else None,
                "mean_value": round(float(series.mean()), 6) if non_null_cnt > 0 else None,
                "std_value": round(float(series.std()), 6) if non_null_cnt > 1 else (0.0 if non_null_cnt == 1 else None),
                "is_constant": bool(is_const),
                "notes": (
                    "Constant signal (zero variance; candidate for removal inside CV)"
                    if is_const
                    else (
                        "High missingness (>50% NaN)"
                        if (miss_cnt / n_rows) > 0.5
                        else "Active anonymous numeric sensor/signal"
                    )
                ),
            }
        )

    return pd.DataFrame(records)


def write_dictionary_markdown(dict_df: pd.DataFrame, out_path: Path) -> None:
    """Write a readable Markdown data dictionary summarizing documented fields and all 590 anonymous sensors."""
    doc_rows = dict_df[dict_df["field_category"] != "Anonymous Process Sensor Signal"]
    sensor_rows = dict_df[dict_df["field_category"] == "Anonymous Process Sensor Signal"]

    lines = [
        "# UCI SECOM Data Dictionary",
        "",
        "## 1. Documented Fields (`secom_labels.data`)",
        "",
        "| Field Name | Source File | Col (1-based) | Type | Values / Format | Missing | Unique | Notes |",
        "|---|---|---:|---|---|---:|---:|---|",
    ]
    for _, r in doc_rows.iterrows():
        lines.append(
            f"| `{r['field_name']}` | `{r['source_file']}` | {r['source_column_number_1based']} | "
            f"{r['data_type']} | {r['allowed_values_or_units']} | {r['missing_count']} ({r['missing_pct']}%) | "
            f"{r['unique_non_null_count']} | {r['notes']} |"
        )

    lines.extend(
        [
            "",
            "## 2. Anonymous Sensor / Process Signal Fields (`secom.data`)",
            "",
            f"- **Total anonymous sensor columns:** {len(sensor_rows)} (`sensor_000` to `sensor_{len(sensor_rows)-1:03d}`)",
            "- **Provenance & Naming Status:** The original UCI SECOM release provides **no physical sensor names, engineering units, tool IDs, or process-stage descriptions** for the 590 columns in `secom.data`. All columns are strictly anonymous real-valued process signals/measurement points (`NaN` for missing).",
            f"- **Constant (zero-variance) sensors:** {int(sensor_rows['is_constant'].sum())}",
            f"- **Sensors with >50% missing values:** {int((sensor_rows['missing_pct'] > 50).sum())}",
            "",
            "The full machine-readable dictionary for all 592 fields (`2` documented + `590` anonymous) is saved in [`docs/data_dictionary.csv`](data_dictionary.csv).",
            "",
            "### Full Anonymous Sensor Table (`sensor_000` – `sensor_589`)",
            "",
            "| Field Name | 0-Based Idx | 1-Based Col | Status | Missing Count (%) | Unique Non-Null | Min | Max | Mean | Std | Notes |",
            "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )

    for _, r in sensor_rows.iterrows():
        min_v = f"{r['min_value']:.4g}" if pd.notna(r["min_value"]) else "NaN"
        max_v = f"{r['max_value']:.4g}" if pd.notna(r["max_value"]) else "NaN"
        mean_v = f"{r['mean_value']:.4g}" if pd.notna(r["mean_value"]) else "NaN"
        std_v = f"{r['std_value']:.4g}" if pd.notna(r["std_value"]) else "NaN"
        lines.append(
            f"| `{r['field_name']}` | {r['source_column_index_0based']} | {r['source_column_number_1based']} | "
            f"Anonymous | {r['missing_count']} ({r['missing_pct']}%) | {r['unique_non_null_count']} | "
            f"{min_v} | {max_v} | {mean_v} | {std_v} | {r['notes']} |"
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    sensors_df, labels_df = load_raw_secom()
    quality_summary = analyze_structure_and_quality(sensors_df, labels_df)
    timestamp_summary = analyze_timestamps(labels_df)

    audit_summary = {
        "quality_and_structure": quality_summary,
        "chronological_timestamp_analysis": timestamp_summary,
    }

    summary_path = REPORTS_DIR / "secom_audit_summary.json"
    summary_path.write_text(json.dumps(audit_summary, indent=2), encoding="utf-8")

    dict_df = build_data_dictionary(sensors_df, labels_df)
    dict_csv_path = DOCS_DIR / "data_dictionary.csv"
    dict_df.to_csv(dict_csv_path, index=False)

    dict_md_path = DOCS_DIR / "data_dictionary.md"
    write_dictionary_markdown(dict_df, dict_md_path)

    print(json.dumps(audit_summary, indent=2))


if __name__ == "__main__":
    main()
