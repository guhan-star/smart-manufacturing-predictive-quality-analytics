"""Phase 3 — Evaluation metrics, threshold optimization, calibration, and temporal diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    fbeta_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def compute_binary_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.50,
) -> dict[str, float | int | None]:
    """Compute the full Phase 3 classification and probability metric suite."""
    y_true_arr = np.asarray(y_true, dtype=int)
    y_prob_arr = np.asarray(y_prob, dtype=float)
    y_pred = (y_prob_arr >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred, labels=[0, 1]).ravel()
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    n_pos = int((y_true_arr == 1).sum())
    n_neg = int((y_true_arr == 0).sum())
    has_both_classes = n_pos > 0 and n_neg > 0

    return {
        "threshold": round(float(threshold), 4),
        "n_samples": int(len(y_true_arr)),
        "n_fails": n_pos,
        "n_passes": n_neg,
        "fail_precision": round(float(precision_score(y_true_arr, y_pred, zero_division=0)), 6),
        "fail_recall": round(float(recall_score(y_true_arr, y_pred, zero_division=0)), 6),
        "fail_f1": round(float(f1_score(y_true_arr, y_pred, zero_division=0)), 6),
        "fail_f2": round(float(fbeta_score(y_true_arr, y_pred, beta=2.0, zero_division=0)), 6),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_true_arr, y_pred)), 6)
        if has_both_classes
        else None,
        "pr_auc": round(float(average_precision_score(y_true_arr, y_prob_arr)), 6)
        if n_pos > 0
        else None,
        "roc_auc": round(float(roc_auc_score(y_true_arr, y_prob_arr)), 6)
        if has_both_classes
        else None,
        "mcc": round(float(matthews_corrcoef(y_true_arr, y_pred)), 6)
        if has_both_classes
        else 0.0,
        "accuracy": round(float(accuracy_score(y_true_arr, y_pred)), 6),
        "specificity": round(specificity, 6),
        "fpr": round(fpr, 6),
        "fnr": round(fnr, 6),
        "brier_score": round(float(brier_score_loss(y_true_arr, np.clip(y_prob_arr, 0.0, 1.0))), 6),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "flagged_pct": round(float((tp + fp) / len(y_true_arr) * 100.0), 4),
    }


def sweep_thresholds(
    y_val: np.ndarray,
    y_prob_val: np.ndarray,
    thresholds: np.ndarray | None = None,
) -> tuple[pd.DataFrame, float]:
    """Evaluate thresholds strictly on chronological validation predictions and pick optimal F2 threshold.

    Operational objective:
        Maximize F2-score (beta=2, weighting Fail recall 2x more than precision) across thresholds
        that flag at least 1% and at most 40% of wafers (preventing degenerate all-positive alarms).
        Falls back to unconstrained max-F2 if no threshold lies in the guard band.
    """
    if thresholds is None:
        thresholds = np.round(np.linspace(0.05, 0.95, 91), 4)

    rows = [compute_binary_metrics(y_val, y_prob_val, float(t)) for t in thresholds]
    sweep_df = pd.DataFrame(rows)

    feasible = sweep_df[
        (sweep_df["flagged_pct"] >= 1.0)
        & (sweep_df["flagged_pct"] <= 40.0)
        & (sweep_df["fail_recall"] > 0.0)
    ]
    if feasible.empty:
        feasible = sweep_df[sweep_df["fail_recall"] > 0.0]
    if feasible.empty:
        selected_t = 0.50
    else:
        best_row = feasible.sort_values(
            ["fail_f2", "mcc", "fail_precision"], ascending=[False, False, False]
        ).iloc[0]
        selected_t = float(best_row["threshold"])

    return sweep_df, selected_t


def compute_calibration_diagnostics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 5,
) -> dict:
    """Compute Brier score and quantile-binned calibration curve coordinates."""
    y_arr = np.asarray(y_true, dtype=int)
    p_arr = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    brier = float(brier_score_loss(y_arr, p_arr))
    prob_true, prob_pred = calibration_curve(
        y_arr, p_arr, n_bins=n_bins, strategy="quantile"
    )
    return {
        "brier_score": round(brier, 6),
        "base_fail_rate": round(float(y_arr.mean()), 6),
        "n_fails": int((y_arr == 1).sum()),
        "n_bins_returned": int(len(prob_true)),
        "prob_true": [round(float(x), 6) for x in prob_true],
        "prob_pred": [round(float(x), 6) for x in prob_pred],
    }


def evaluate_chronological_subperiods(
    labels_df: pd.DataFrame,
    indices: np.ndarray,
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
    period_labels: np.ndarray | None = None,
) -> pd.DataFrame:
    """Break down model performance across chronological periods."""
    sub_labels = labels_df.iloc[indices].copy().reset_index(drop=True)
    if period_labels is None:
        # Split into calendar half-month windows for granular temporal drift tracking
        ts = pd.to_datetime(sub_labels["timestamp"])
        half = np.where(ts.dt.day <= 15, "H1", "H2")
        period_series = ts.dt.to_period("M").astype(str) + "-" + half
    else:
        period_series = pd.Series(period_labels)

    rows = []
    for period_name in period_series.drop_duplicates():
        mask = (period_series == period_name).to_numpy()
        m = compute_binary_metrics(y_true[mask], y_prob[mask], threshold=threshold)
        m["period"] = str(period_name)
        m["start_timestamp"] = str(sub_labels.loc[mask, "timestamp"].min())
        m["end_timestamp"] = str(sub_labels.loc[mask, "timestamp"].max())
        m["actual_fail_rate_pct"] = round(float(y_true[mask].mean() * 100.0), 2)
        rows.append(m)
    return pd.DataFrame(rows)


def curve_coordinates(y_true: np.ndarray, y_prob: np.ndarray) -> dict[str, list[float]]:
    """Return PR and ROC curve arrays for plotting."""
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    return {
        "pr_precision": prec.tolist(),
        "pr_recall": rec.tolist(),
        "roc_fpr": fpr.tolist(),
        "roc_tpr": tpr.tolist(),
    }
