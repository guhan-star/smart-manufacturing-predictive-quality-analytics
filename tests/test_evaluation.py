"""Tests for Phase 3 evaluation metrics, threshold optimization, and required deliverables."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from secom_project import REPORTS_DIR
from secom_project.evaluation import compute_binary_metrics, sweep_thresholds


def test_compute_binary_metrics_exact_confusion_values() -> None:
    y_true = np.array([0, 0, 0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.6, 0.3, 0.8, 0.4])
    m = compute_binary_metrics(y_true, y_prob, threshold=0.50)

    assert m["tp"] == 1
    assert m["fp"] == 1
    assert m["fn"] == 1
    assert m["tn"] == 3
    assert m["tp"] + m["fp"] + m["fn"] + m["tn"] == len(y_true)
    assert m["fail_precision"] == 0.5
    assert m["fail_recall"] == 0.5
    assert m["fail_f1"] == 0.5
    assert m["specificity"] == 0.75
    assert m["fpr"] == 0.25
    assert m["fnr"] == 0.5


def test_threshold_sweep_selects_valid_threshold() -> None:
    rng = np.random.default_rng(42)
    y_val = np.array([0] * 180 + [1] * 20)
    y_prob = np.concatenate([rng.uniform(0.02, 0.25, 180), rng.uniform(0.20, 0.80, 20)])
    sweep_df, selected_t = sweep_thresholds(y_val, y_prob)
    assert not sweep_df.empty
    assert 0.05 <= selected_t <= 0.95


def test_required_phase3_deliverables_exist_and_finite() -> None:
    p3_dir = REPORTS_DIR / "phase3"
    required_files = [
        p3_dir / "model_comparison.csv",
        p3_dir / "test_metrics.json",
        p3_dir / "classification_report.txt",
        p3_dir / "confusion_matrix.png",
        p3_dir / "precision_recall_curve.png",
        p3_dir / "roc_curve.png",
        p3_dir / "feature_importance.csv",
        p3_dir / "feature_importance.png",
        p3_dir / "phase3_modeling_report.md",
    ]
    for path in required_files:
        assert path.exists(), f"Missing Phase 3 deliverable: {path}"
        assert path.stat().st_size > 0, f"Empty Phase 3 deliverable: {path}"

    comp_df = pd.read_csv(p3_dir / "model_comparison.csv")
    assert len(comp_df) == 4
    numeric_cols = comp_df.select_dtypes(include=[np.number]).columns
    assert np.isfinite(comp_df[numeric_cols].to_numpy()).all()

    test_metrics = json.loads((p3_dir / "test_metrics.json").read_text(encoding="utf-8"))
    assert test_metrics["trained_on_test_set"] is False
    assert test_metrics["n_samples"] == 359
    assert test_metrics["n_fails"] == 22

    imp_df = pd.read_csv(p3_dir / "feature_importance.csv")
    assert not imp_df.empty
    assert all(str(f).startswith("sensor_") for f in imp_df["feature"])
