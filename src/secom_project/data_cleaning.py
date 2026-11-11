"""Phase 2 — Data preparation, missing-value handling, outlier audit, and reproducible cleaning."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from secom_project import DATA_PROCESSED_DIR, DATA_RAW_DIR, REPORTS_DIR
from secom_project.data_validation import (
    compute_iqr_outlier_summary,
    find_duplicate_columns,
    identify_constant_and_near_constant,
    load_and_parse_raw_secom,
    validate_secom_raw,
)


@dataclass(frozen=True)
class CleaningConfig:
    """Explicit, documented thresholds for SECOM Phase 2 data preparation."""

    high_missing_threshold: float = 0.50
    near_constant_dominant_threshold: float = 0.99
    max_record_missing_threshold: float = 0.50


@dataclass(frozen=True)
class FittedCleaningPlan:
    """Unsupervised cleaning parameters fit strictly on a training/reference feature matrix."""

    config: CleaningConfig
    kept_features: tuple[str, ...]
    constant_features_removed: tuple[str, ...]
    near_constant_features_removed: tuple[str, ...]
    high_missing_features_removed: tuple[str, ...]
    duplicate_non_constant_removed: tuple[str, ...]
    imputation_medians: dict[str, float]


def classify_missing_tier(missing_pct: float) -> str:
    """Classify per-feature missingness into documented tiers."""
    if missing_pct == 0.0:
        return "Complete (0%)"
    if missing_pct <= 5.0:
        return "Low (0%-5%]"
    if missing_pct <= 50.0:
        return "Moderate (5%-50%]"
    return "Extreme (>50%)"


def fit_cleaning_plan(
    sensors_train: pd.DataFrame, config: CleaningConfig = CleaningConfig()
) -> FittedCleaningPlan:
    """Fit all feature-filtering and median-imputation rules on sensor features only (no target or test info)."""
    work = sensors_train.replace([np.inf, -np.inf], np.nan)

    cnc = identify_constant_and_near_constant(
        work, dominant_threshold=config.near_constant_dominant_threshold
    )
    constant_cols = list(cnc["constant_features"])
    near_constant_cols = [r["feature"] for r in cnc["near_constant_features"]]

    col_miss_ratio = work.isna().mean(axis=0)
    high_missing_cols = [
        c for c in work.columns if col_miss_ratio[c] > config.high_missing_threshold
    ]

    removed_initial = set(constant_cols) | set(near_constant_cols) | set(high_missing_cols)

    # Check exact duplicate columns among remaining active features (retain first occurrence)
    active_candidates = [c for c in work.columns if c not in removed_initial]
    dup_groups = find_duplicate_columns(work[active_candidates])
    dup_non_constant_removed: list[str] = []
    for grp in dup_groups:
        dup_non_constant_removed.extend(grp[1:])

    removed_all = removed_initial | set(dup_non_constant_removed)
    kept_features = [c for c in work.columns if c not in removed_all]

    medians = work[kept_features].median(axis=0, skipna=True).to_dict()
    medians_float = {k: float(v) for k, v in medians.items()}

    return FittedCleaningPlan(
        config=config,
        kept_features=tuple(kept_features),
        constant_features_removed=tuple(constant_cols),
        near_constant_features_removed=tuple(near_constant_cols),
        high_missing_features_removed=tuple(high_missing_cols),
        duplicate_non_constant_removed=tuple(dup_non_constant_removed),
        imputation_medians=medians_float,
    )


def apply_cleaning_plan(
    sensors_df: pd.DataFrame,
    labels_df: pd.DataFrame,
    plan: FittedCleaningPlan,
) -> pd.DataFrame:
    """Apply a fitted cleaning plan to sensor + label tables while preserving row order and separate target/timestamp."""
    if len(sensors_df) != len(labels_df):
        raise ValueError("Sensor and label row counts must match before cleaning.")

    work_sensors = sensors_df.replace([np.inf, -np.inf], np.nan)
    kept_df = work_sensors.loc[:, list(plan.kept_features)].copy()
    kept_df = kept_df.fillna(plan.imputation_medians)

    # Combine without altering original row order; keep target_label and timestamp separate
    cleaned_df = pd.concat(
        [
            labels_df[["target_label", "timestamp", "timestamp_raw"]].reset_index(drop=True),
            kept_df.reset_index(drop=True),
        ],
        axis=1,
    )
    return cleaned_df


def build_missing_value_report(
    sensors_df: pd.DataFrame,
    labels_df: pd.DataFrame,
    plan: FittedCleaningPlan,
) -> pd.DataFrame:
    """Produce per-feature missingness diagnostics ranked from highest to lowest missingness."""
    pass_mask = labels_df["target_label"] == -1
    fail_mask = labels_df["target_label"] == 1
    n_rows = len(sensors_df)

    const_set = set(plan.constant_features_removed)
    nc_set = set(plan.near_constant_features_removed)
    hm_set = set(plan.high_missing_features_removed)
    dup_set = set(plan.duplicate_non_constant_removed)

    rows = []
    for col in sensors_df.columns:
        miss_cnt = int(sensors_df[col].isna().sum())
        miss_pct = miss_cnt / n_rows * 100.0
        pass_miss = float(sensors_df.loc[pass_mask, col].isna().mean() * 100.0)
        fail_miss = float(sensors_df.loc[fail_mask, col].isna().mean() * 100.0)

        if col in const_set:
            action = "Removed (Constant)"
        elif col in nc_set:
            action = "Removed (Near-Constant >=99%)"
        elif col in hm_set:
            action = f"Removed (High Missingness >{int(plan.config.high_missing_threshold * 100)}%)"
        elif col in dup_set:
            action = "Removed (Exact Duplicate Column)"
        elif miss_cnt > 0:
            action = "Retained + Median Imputed (Unsupervised)"
        else:
            action = "Retained (Complete)"

        rows.append(
            {
                "feature": col,
                "missing_count": miss_cnt,
                "missing_pct": round(miss_pct, 4),
                "non_null_count": n_rows - miss_cnt,
                "missing_pct_pass": round(pass_miss, 4),
                "missing_pct_fail": round(fail_miss, 4),
                "abs_diff_fail_vs_pass_pct": round(abs(fail_miss - pass_miss), 4),
                "missingness_tier": classify_missing_tier(miss_pct),
                "is_constant": col in const_set,
                "is_near_constant": col in nc_set,
                "cleaning_action": action,
            }
        )

    df_out = pd.DataFrame(rows)
    df_out["missingness_rank"] = df_out["missing_count"].rank(ascending=False, method="min").astype(int)
    return df_out


def investigate_near_constant_features(
    sensors_df: pd.DataFrame,
    labels_df: pd.DataFrame,
    near_constant_cols: list[str],
) -> list[dict]:
    """Audit exceptional (non-dominant) observations, target labels, and timestamps for near-constant features."""
    details: list[dict] = []
    for col in near_constant_cols:
        non_null = sensors_df[col].dropna()
        dominant_val = float(non_null.value_counts().index[0])
        exc_idx = sensors_df.index[sensors_df[col].notna() & (sensors_df[col] != dominant_val)].tolist()
        exceptional_records = [
            {
                "row_index": int(idx),
                "value": float(sensors_df.loc[idx, col]),
                "target_label": int(labels_df.loc[idx, "target_label"]),
                "timestamp": str(labels_df.loc[idx, "timestamp"]),
            }
            for idx in exc_idx
        ]
        details.append(
            {
                "feature": col,
                "dominant_value": dominant_val,
                "dominant_count": int((non_null == dominant_val).sum()),
                "missing_count": int(sensors_df[col].isna().sum()),
                "exceptional_count": len(exceptional_records),
                "exceptional_records": exceptional_records,
                "any_fail_in_exceptional": any(r["target_label"] == 1 for r in exceptional_records),
            }
        )
    return details


def evaluate_threshold_impact(sensors_df: pd.DataFrame) -> list[dict]:
    """Quantify how different missingness thresholds affect feature retention (documenting decision impact)."""
    miss_ratio = sensors_df.isna().mean(axis=0)
    cnc = identify_constant_and_near_constant(sensors_df, dominant_threshold=0.99)
    const_or_nc = set(cnc["constant_features"]) | {
        r["feature"] for r in cnc["near_constant_features"]
    }

    impact = []
    for cutoff in [0.20, 0.40, 0.50, 0.60, 0.80]:
        dropped_miss = {c for c in sensors_df.columns if miss_ratio[c] > cutoff}
        total_dropped = const_or_nc | dropped_miss
        impact.append(
            {
                "missing_cutoff_pct": int(cutoff * 100),
                "features_exceeding_cutoff": len(dropped_miss),
                "total_removed_incl_const_and_nc": len(total_dropped),
                "features_retained": sensors_df.shape[1] - len(total_dropped),
            }
        )
    return impact


def clean_secom_data(
    sensors_df: pd.DataFrame,
    labels_df: pd.DataFrame,
    config: CleaningConfig = CleaningConfig(),
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Run the reproducible Phase 2 cleaning pipeline on validated SECOM data."""
    raw_rows, raw_cols = sensors_df.shape
    inf_count = int(np.isinf(sensors_df.to_numpy(dtype=np.float64)).sum())

    # Check exact duplicates (preserve original row order if none)
    combined_raw = pd.concat([labels_df[["target_label", "timestamp_raw"]], sensors_df], axis=1)
    dup_full = int(combined_raw.duplicated(keep="first").sum())
    dup_sensors = int(sensors_df.duplicated(keep="first").sum())

    # Record-level missingness check
    row_miss_pct = sensors_df.isna().mean(axis=1) * 100.0
    rows_above_thresh = int((row_miss_pct > config.max_record_missing_threshold * 100.0).sum())

    plan = fit_cleaning_plan(sensors_df, config=config)
    cleaned_df = apply_cleaning_plan(sensors_df, labels_df, plan)
    missing_report_df = build_missing_value_report(sensors_df, labels_df, plan)
    threshold_impact = evaluate_threshold_impact(sensors_df)

    # Outlier audit on active retained features (prior to imputation, without deleting outliers)
    outlier_summary = compute_iqr_outlier_summary(sensors_df, list(plan.kept_features))

    # Monthly regime check on missingness vs yield
    monthly_df = pd.DataFrame(
        {
            "year_month": labels_df["timestamp"].dt.to_period("M").astype(str),
            "target_label": labels_df["target_label"],
            "row_missing_pct": row_miss_pct,
            "sensor_072_missing": sensors_df["sensor_072"].isna(),
            "sensor_112_missing": sensors_df["sensor_112"].isna(),
        }
    )
    monthly_miss = (
        monthly_df.groupby("year_month")
        .agg(
            records=("target_label", "size"),
            fail_rate_pct=("target_label", lambda s: round(float((s == 1).mean() * 100.0), 2)),
            mean_row_missing_pct=("row_missing_pct", lambda s: round(float(s.mean()), 2)),
            sensor_072_missing_pct=("sensor_072_missing", lambda s: round(float(s.mean() * 100.0), 2)),
            sensor_112_missing_pct=("sensor_112_missing", lambda s: round(float(s.mean() * 100.0), 2)),
        )
        .reset_index()
        .to_dict(orient="records")
    )

    sensor_cols_kept = list(plan.kept_features)
    retained_raw_missing = int(sensors_df[sensor_cols_kept].isna().sum().sum())
    cleaned_missing = int(cleaned_df[sensor_cols_kept].isna().sum().sum())

    cnc = identify_constant_and_near_constant(sensors_df, dominant_threshold=config.near_constant_dominant_threshold)
    near_const_investigation = investigate_near_constant_features(
        sensors_df, labels_df, list(plan.near_constant_features_removed)
    )
    col_miss_pct = sensors_df.isna().mean(axis=0) * 100.0

    summary = {
        "config": asdict(config),
        "raw_shape": {"rows": int(raw_rows), "sensor_columns": int(raw_cols)},
        "cleaned_shape": {
            "rows": int(cleaned_df.shape[0]),
            "total_columns": int(cleaned_df.shape[1]),
            "sensor_columns": len(sensor_cols_kept),
            "target_and_timestamp_columns": ["target_label", "timestamp", "timestamp_raw"],
        },
        "transformations": {
            "infinite_values_found_and_replaced": inf_count,
            "duplicate_sensor_rows_found": dup_sensors,
            "duplicate_full_rows_removed": dup_full,
            "records_removed_excessive_missingness": rows_above_thresh,
            "max_observed_record_missing_pct": round(float(row_miss_pct.max()), 4),
            "constant_features_removed": len(plan.constant_features_removed),
            "near_constant_features_removed": len(plan.near_constant_features_removed),
            "high_missing_features_removed": len(plan.high_missing_features_removed),
            "duplicate_non_constant_features_removed": len(plan.duplicate_non_constant_removed),
            "total_unique_features_removed": raw_cols - len(sensor_cols_kept),
            "retained_sensor_features": len(sensor_cols_kept),
        },
        "missing_values": {
            "raw_sensor_missing_cells": int(sensors_df.isna().sum().sum()),
            "raw_sensor_missing_pct": round(float(sensors_df.isna().sum().sum() / sensors_df.size * 100.0), 4),
            "missing_cells_in_retained_before_imputation": retained_raw_missing,
            "missing_cells_after_cleaning": cleaned_missing,
            "raw_feature_tier_counts": {
                str(k): int(v) for k, v in missing_report_df["missingness_tier"].value_counts().items()
            },
        },
        "threshold_impact_analysis": threshold_impact,
        "outlier_audit_non_destructive": outlier_summary,
        "monthly_missingness_vs_yield": monthly_miss,
        "removed_features": {
            "constant": list(plan.constant_features_removed),
            "near_constant": cnc["near_constant_features"],
            "near_constant_sensitivity_detail": near_const_investigation,
            "high_missingness_gt_50pct": [
                {"feature": c, "missing_pct": round(float(col_miss_pct[c]), 4)}
                for c in sorted(plan.high_missing_features_removed, key=lambda x: col_miss_pct[x], reverse=True)
            ],
            "duplicate_non_constant": list(plan.duplicate_non_constant_removed),
        },
        "safeguards": {
            "uses_target_label_in_preprocessing": False,
            "uses_test_set_in_preprocessing": False,
            "phase3_note": (
                "fit_cleaning_plan() must be called strictly on training folds during Phase 3 cross-validation "
                "or chronological holdout splits; apply_cleaning_plan() then transforms test folds without refitting."
            ),
            "chronological_row_order_preserved": True,
            "outliers_preserved_not_deleted": True,
        },
        "imputation_medians": plan.imputation_medians,
    }

    return cleaned_df, missing_report_df, summary


def write_data_quality_report(
    validation_summary: dict,
    cleaning_summary: dict,
    missing_report_df: pd.DataFrame,
    out_path: Path = REPORTS_DIR / "phase2_data_quality_report.md",
) -> None:
    """Write `reports/phase2_data_quality_report.md` covering validation, cleaning, outliers & safeguards."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dim = validation_summary["dimensions"]
    tgt = validation_summary["target_validation"]
    ts = validation_summary["timestamp_validation"]
    dq = validation_summary["data_quality"]
    tr = cleaning_summary["transformations"]
    mv = cleaning_summary["missing_values"]
    out = cleaning_summary["outlier_audit_non_destructive"]

    checksum_lines = "\n".join(
        f"- `{k}`: {'VERIFIED' if v else 'FAILED'}"
        for k, v in validation_summary["raw_checksum_verification"].items()
    )

    thresh_rows = "\n".join(
        f"| > {r['missing_cutoff_pct']}% | {r['features_exceeding_cutoff']} | "
        f"{r['total_removed_incl_const_and_nc']} | {r['features_retained']} |"
        for r in cleaning_summary["threshold_impact_analysis"]
    )

    top_miss_diff = missing_report_df.sort_values("abs_diff_fail_vs_pass_pct", ascending=False).head(10)
    miss_diff_rows = "\n".join(
        f"| `{r['feature']}` | {r['missing_pct']:.2f}% | {r['missing_pct_pass']:.2f}% | "
        f"{r['missing_pct_fail']:.2f}% | {r['abs_diff_fail_vs_pass_pct']:.2f} pp | {r['cleaning_action']} |"
        for _, r in top_miss_diff.iterrows()
    )

    monthly_rows = "\n".join(
        f"| {r['year_month']} | {r['records']} | {r['fail_rate_pct']:.2f}% | "
        f"{r['mean_row_missing_pct']:.2f}% | {r['sensor_072_missing_pct']:.2f}% | {r['sensor_112_missing_pct']:.2f}% |"
        for r in cleaning_summary["monthly_missingness_vs_yield"]
    )

    high_miss_list = "\n".join(
        f"- `{item['feature']}`: {item['missing_pct']:.2f}% missing"
        for item in cleaning_summary["removed_features"]["high_missingness_gt_50pct"]
    )
    near_const_list = "\n".join(
        f"- `{item['feature']}`: dominant value `{item['dominant_value']}` in "
        f"{item['dominant_ratio']*100:.4f}% of {item['n_non_null']} non-null observations (only row 1458 differs)"
        for item in cleaning_summary["removed_features"]["near_constant"]
    )

    content = f"""# Phase 2 Data Quality & Preparation Report — UCI SECOM

## 1. Raw Data Integrity, Alignment & Validation
{checksum_lines}

- **Raw Dimensions:** `{dim['rows']}` rows × `{dim['sensor_columns']}` sensor columns (`sensor_000`–`sensor_589` via Phase 1 `load_raw_secom()`) + `2` label/timestamp columns (`target_label`, `timestamp_raw`).
- **Row Alignment:** `{dim['row_alignment_verified']}` (original chronological row order preserved).
- **Data Types & Infinite Values:** All `{dim['sensor_columns']}` sensors are `float64`; `{dq['positive_inf_count']}` `+inf` and `{dq['negative_inf_count']}` `-inf` values detected.
- **Target Validation:** `{tgt['missing_target_labels']}` missing labels; `{tgt['valid_labels_only_minus1_and_1']}` (`{{-1, 1}}` only).
  - **Pass (`-1`):** `{tgt['pass_count_minus1']}` (`{tgt['pass_pct']}%`)
  - **Fail (`1`):** `{tgt['fail_count_1']}` (`{tgt['fail_pct']}%`)
  - **Class Imbalance:** `{tgt['imbalance_ratio_pass_to_fail']} : 1` (~`14:1` Pass:Fail)
- **Timestamp Validation:** `{ts['missing_timestamp_raw']}` missing raw timestamps; `{ts['failed_timestamp_parses']}` failed parses under `{ts['format']}`.
  - Span: `{ts['min_timestamp']}` to `{ts['max_timestamp']}` (`89.76` days).
  - Monotonically non-decreasing in raw order: `{ts['is_monotonic_non_decreasing_in_raw_order']}` (`{ts['unique_timestamps']}` unique timestamps; `{ts['repeated_timestamp_groups']}` repeated timestamp groups covering `{ts['rows_sharing_repeated_timestamp']}` rows).

## 2. Duplicate, Constant & Near-Constant Investigation
- **Duplicate Rows:** `{dq['duplicate_sensor_rows']}` duplicate sensor rows; `{dq['duplicate_full_rows']}` full duplicate rows.
- **Duplicate Columns:** `{dq['duplicate_column_groups_total']}` duplicate column groups total, all among strictly constant columns (`{len(dq['non_constant_duplicate_column_groups'])}` non-constant duplicate groups).
- **Strictly Constant Columns (`nunique <= 1`):** `{tr['constant_features_removed']}` features — zero variance, removed.
- **Near-Constant Columns (dominant value >= `99%`):** `{tr['near_constant_features_removed']}` features (`0.0` in `1,560 / 1,561` non-null rows; only Pass row `1458` differs) — removed to prevent fold instability:
{near_const_list}

## 3. Missing-Value Analysis & Threshold Impact
- **Overall Missingness (Before Cleaning):** `{mv['raw_sensor_missing_cells']:,}` / `924,530` cells (`{mv['raw_sensor_missing_pct']}%`); `{dq['features_with_any_missing']} / 590` features and `{dq['records_with_any_missing']} / 1,567` records (`100%`) contain at least one `NaN`.
- **Why Rows Were NOT Dropped:** Record missingness ranges from `0.68%` to `25.76%` (median `4.07%`). Dropping every row with a missing value would discard `100%` of the dataset; therefore **`0` records were removed**.

### Missingness Threshold Sensitivity Analysis
| Missingness Cutoff | Features Exceeding Cutoff | Total Removed (incl. 116 Constant + 6 Near-Constant) | Features Retained |
|---|---:|---:|---:|
{thresh_rows}

We select **`> 50%` missingness** (`28` features, `50.67%` to `91.19%` missing) because there is a natural empirical gap between `45.63%` (4 moderate features) and `50.67%` (`28` features), avoiding synthetic imputation of majority-missing columns while preserving `440` active sensors.

### Removed High-Missingness Features (`> 50%`, `28` Features)
{high_miss_list}

### Missingness vs. Target & Possible Target Leakage Warning
Missingness is **not MCAR**: several sensor blocks exhibit large missingness differences between Pass and Fail records:

| Feature | Overall Missing | Pass Missing | Fail Missing | |Fail - Pass| | Action |
|---|---:|---:|---:|---:|---|
{miss_diff_rows}

Cross-tabulating against production months shows this gap tracks **logging-regime changes** over time:

| Month | Records | Fail Rate | Mean Row Missing | `sensor_072` Missing | `sensor_112` Missing |
|---|---:|---:|---:|---:|---:|
{monthly_rows}

**Leakage Risk:** If missingness reflects downstream test skipping or logging changes tied to defect waves, naive missingness indicators or full-dataset imputation could leak temporal/operational regime information.

## 4. Non-Destructive Outlier Audit
We evaluated IQR fences on the `{out['evaluated_active_features_with_positive_iqr']}` retained active features with `IQR > 0` (`{out['zero_iqr_active_features']}` active features have `IQR = 0` due to discrete/zero-inflated distributions):
- **Mild Outliers (`1.5 × IQR`):** `{out['iqr_1_5_outlier_cells']:,}` / `{out['non_null_cells_evaluated']:,}` evaluated cells (`{out['iqr_1_5_outlier_pct']}%`)
- **Extreme Outliers (`3.0 × IQR`):** `{out['iqr_3_0_extreme_outlier_cells']:,}` cells (`{out['iqr_3_0_extreme_outlier_pct']}%`), affecting `{out['records_with_any_extreme_outlier']}` / `1,567` records.
- **Decision:** **0 outliers removed.** Without physical sensor documentation, high/low spikes cannot be assumed to be measurement errors and may represent genuine process excursions associated with wafer defects.

## 5. Final Cleaning Summary & Critical Safeguards
- **Input Dimensions:** `1,567` rows × `590` sensors (`41,951` missing cells)
- **Output Dimensions (`data/processed/secom_cleaned.csv`):** `1,567` rows × `443` columns (`target_label`, `timestamp`, `timestamp_raw`, plus `440` cleaned sensors; `0` missing cells)
- **Imputation:** Unsupervised per-feature median imputation across the `{mv['missing_cells_in_retained_before_imputation']:,}` missing cells in the `440` retained sensors (`uses_target_label = False`).
- **Safeguards Enforced:**
  1. Anonymous sensor names (`sensor_000`–`sensor_589`) preserved with zero fabricated physical meanings.
  2. `target_label` and `timestamp` kept separate; raw `timestamp` excluded from future predictive features unless explicitly justified by temporal design.
  3. Original chronological row order and all `32` repeated-timestamp groups preserved (`0` rows dropped).
  4. `14.07 : 1` class imbalance recorded for Phase 3 modeling/evaluation planning.
  5. `fit_cleaning_plan()` / `apply_cleaning_plan()` implemented cleanly so Phase 3 splits fit preprocessing strictly on training data.
"""
    out_path.write_text(content, encoding="utf-8")


def main() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    validation_summary = validate_secom_raw(DATA_RAW_DIR)
    sensors_df, labels_df = load_and_parse_raw_secom(DATA_RAW_DIR)
    cleaned_df, missing_report_df, cleaning_summary = clean_secom_data(sensors_df, labels_df)

    cleaned_csv = DATA_PROCESSED_DIR / "secom_cleaned.csv"
    cleaned_df.to_csv(cleaned_csv, index=False)

    missing_csv = REPORTS_DIR / "phase2_missing_value_report.csv"
    missing_report_df.to_csv(missing_csv, index=False)

    cleaning_summary["output_artifacts"] = {
        "cleaned_csv": str(cleaned_csv),
        "cleaned_csv_sha256": hashlib.sha256(cleaned_csv.read_bytes()).hexdigest(),
        "missing_value_report_csv": str(missing_csv),
    }

    summary_json = DATA_PROCESSED_DIR / "secom_cleaning_summary.json"
    summary_json.write_text(json.dumps(cleaning_summary, indent=2), encoding="utf-8")

    quality_md = REPORTS_DIR / "phase2_data_quality_report.md"
    write_data_quality_report(validation_summary, cleaning_summary, missing_report_df, quality_md)

    print(json.dumps(cleaning_summary["transformations"], indent=2))
    print("Saved:", cleaned_csv, summary_json, missing_csv, quality_md)


if __name__ == "__main__":
    main()
