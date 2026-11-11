"""Phase 3 — Fast, leakage-safe SECOM predictive quality modeling pipeline.

Reuses Phase 1 `load_raw_secom()` (via `prepare_chronological_dataset`) and Phase 2
`fit_cleaning_plan()` inside a scikit-learn Pipeline so all cleaning, scaling,
class-imbalance handling, model selection, and threshold tuning strictly avoid
test-set or target leakage.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from secom_project import DATA_RAW_DIR, MODELS_DIR, REPORTS_DIR
from secom_project.evaluation import (
    compute_binary_metrics,
    curve_coordinates,
    sweep_thresholds,
)
from secom_project.transformers import SecomTrainingPreprocessor
from secom_project.validation import (
    TrainValTestSplit,
    build_train_val_test_splits,
    prepare_chronological_dataset,
)

RANDOM_SEED = 42
sns.set_theme(style="whitegrid", context="notebook")


def build_phase3_models() -> dict[str, Pipeline]:
    """Construct the Dummy baseline and 3 practical, leakage-safe Phase 3 classifiers."""
    return {
        "Dummy_Majority": Pipeline(
            [
                ("prep", SecomTrainingPreprocessor(0.50, True, 0.99, False)),
                ("clf", DummyClassifier(strategy="most_frequent")),
            ]
        ),
        "LogisticRegression": Pipeline(
            [
                ("prep", SecomTrainingPreprocessor(0.50, True, 0.99, False)),
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.05,
                        l1_ratio=0.0,
                        solver="liblinear",
                        class_weight="balanced",
                        max_iter=2000,
                        random_state=RANDOM_SEED,
                    ),
                ),
            ]
        ),
        "RandomForest": Pipeline(
            [
                ("prep", SecomTrainingPreprocessor(0.50, True, 0.99, False)),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=6,
                        min_samples_leaf=3,
                        class_weight="balanced_subsample",
                        random_state=RANDOM_SEED,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "HistGradientBoosting": Pipeline(
            [
                ("prep", SecomTrainingPreprocessor(0.50, True, 0.99, False)),
                (
                    "clf",
                    HistGradientBoostingClassifier(
                        learning_rate=0.05,
                        max_iter=150,
                        max_depth=4,
                        min_samples_leaf=20,
                        l2_regularization=1.0,
                        class_weight="balanced",
                        early_stopping=False,
                        random_state=RANDOM_SEED,
                    ),
                ),
            ]
        ),
    }


def compute_lightweight_feature_importance(
    fitted_models: dict[str, Pipeline],
    reports_p3_dir: Path,
) -> pd.DataFrame:
    """Rank anonymous sensors using LogisticRegression coefficients and RandomForest importances."""
    lr_pipe = fitted_models["LogisticRegression"]
    rf_pipe = fitted_models["RandomForest"]

    features = list(lr_pipe.named_steps["prep"].kept_features_)
    lr_coefs = lr_pipe.named_steps["clf"].coef_[0]
    rf_imp = rf_pipe.named_steps["clf"].feature_importances_

    imp_df = pd.DataFrame(
        {
            "feature": features,
            "lr_coef_signed": np.round(lr_coefs, 6),
            "lr_abs_coef": np.round(np.abs(lr_coefs), 6),
            "rf_importance": np.round(rf_imp, 6),
        }
    )
    imp_df["lr_rank"] = imp_df["lr_abs_coef"].rank(ascending=False, method="min").astype(int)
    imp_df["rf_rank"] = imp_df["rf_importance"].rank(ascending=False, method="min").astype(int)
    # Combined rank using normalized LR |coef| and RF importance
    lr_norm = imp_df["lr_abs_coef"] / max(imp_df["lr_abs_coef"].max(), 1e-12)
    rf_norm = imp_df["rf_importance"] / max(imp_df["rf_importance"].max(), 1e-12)
    imp_df["combined_score"] = np.round(0.5 * lr_norm + 0.5 * rf_norm, 6)
    imp_df = imp_df.sort_values("combined_score", ascending=False).reset_index(drop=True)
    imp_df["combined_rank"] = np.arange(1, len(imp_df) + 1)

    imp_df.to_csv(reports_p3_dir / "feature_importance.csv", index=False)
    return imp_df


def generate_phase3_plots(
    selected_name: str,
    selected_t: float,
    y_val: np.ndarray,
    y_test: np.ndarray,
    val_probs: dict[str, np.ndarray],
    test_probs: dict[str, np.ndarray],
    comp_df: pd.DataFrame,
    imp_df: pd.DataFrame,
    reports_p3_dir: Path,
) -> list[Path]:
    """Generate the 4 required Phase 3 plots under `reports/phase3/`."""
    reports_p3_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    # 1. confusion_matrix.png (Validation vs Held-out Test for selected model)
    sel_val_pred = (val_probs[selected_name] >= selected_t).astype(int)
    sel_test_pred = (test_probs[selected_name] >= selected_t).astype(int)
    from sklearn.metrics import confusion_matrix

    cm_val = confusion_matrix(y_val, sel_val_pred, labels=[0, 1])
    cm_test = confusion_matrix(y_test, sel_test_pred, labels=[0, 1])

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    for ax, cm, title in [
        (axes[0], cm_val, f"{selected_name} — Chronological Validation (t*={selected_t:.2f})"),
        (axes[1], cm_test, f"{selected_name} — Held-Out October Test (t*={selected_t:.2f})"),
    ]:
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            xticklabels=["Pred Pass (-1)", "Pred Fail (1)"],
            yticklabels=["Actual Pass (-1)", "Actual Fail (1)"],
            annot_kws={"size": 13, "weight": "bold"},
            ax=ax,
        )
        ax.set_title(title)
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("Actual Label")
    fig.tight_layout()
    p_cm = reports_p3_dir / "confusion_matrix.png"
    fig.savefig(p_cm, dpi=150)
    plt.close(fig)
    saved.append(p_cm)

    # 2. precision_recall_curve.png
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0))
    for name in ["LogisticRegression", "RandomForest", "HistGradientBoosting"]:
        vc = curve_coordinates(y_val, val_probs[name])
        tc = curve_coordinates(y_test, test_probs[name])
        v_ap = float(comp_df.loc[comp_df["model"] == name, "val_pr_auc"].iloc[0])
        t_ap = float(comp_df.loc[comp_df["model"] == name, "test_pr_auc"].iloc[0])
        axes[0].plot(vc["pr_recall"], vc["pr_precision"], linewidth=2.0, label=f"{name} (AP={v_ap:.3f})")
        axes[1].plot(tc["pr_recall"], tc["pr_precision"], linewidth=2.0, label=f"{name} (AP={t_ap:.3f})")

    axes[0].axhline(float(y_val.mean()), color="black", linestyle="--", linewidth=1.1, label=f"Val Base ({y_val.mean():.3f})")
    axes[0].set_title("Validation Precision–Recall Curves")
    axes[0].set_xlabel("Fail Recall")
    axes[0].set_ylabel("Fail Precision")
    axes[0].legend(loc="upper right", fontsize=8.5)

    axes[1].axhline(float(y_test.mean()), color="black", linestyle="--", linewidth=1.1, label=f"Test Base ({y_test.mean():.3f})")
    axes[1].set_title("Held-Out Test Precision–Recall Curves")
    axes[1].set_xlabel("Fail Recall")
    axes[1].set_ylabel("Fail Precision")
    axes[1].legend(loc="upper right", fontsize=8.5)
    fig.tight_layout()
    p_pr = reports_p3_dir / "precision_recall_curve.png"
    fig.savefig(p_pr, dpi=150)
    plt.close(fig)
    saved.append(p_pr)

    # 3. roc_curve.png
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0))
    for name in ["LogisticRegression", "RandomForest", "HistGradientBoosting"]:
        vc = curve_coordinates(y_val, val_probs[name])
        tc = curve_coordinates(y_test, test_probs[name])
        v_auc = float(comp_df.loc[comp_df["model"] == name, "val_roc_auc"].iloc[0])
        t_auc = float(comp_df.loc[comp_df["model"] == name, "test_roc_auc"].iloc[0])
        axes[0].plot(vc["roc_fpr"], vc["roc_tpr"], linewidth=2.0, label=f"{name} (AUC={v_auc:.3f})")
        axes[1].plot(tc["roc_fpr"], tc["roc_tpr"], linewidth=2.0, label=f"{name} (AUC={t_auc:.3f})")

    for ax, title in [(axes[0], "Validation ROC Curves"), (axes[1], "Held-Out Test ROC Curves")]:
        ax.plot([0, 1], [0, 1], "k--", linewidth=1.0, label="Random (0.500)")
        ax.set_title(title)
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate (Fail Recall)")
        ax.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()
    p_roc = reports_p3_dir / "roc_curve.png"
    fig.savefig(p_roc, dpi=150)
    plt.close(fig)
    saved.append(p_roc)

    # 4. feature_importance.png (Top 15 by LogisticRegression |coef| and RandomForest importance)
    top15_lr = imp_df.sort_values("lr_abs_coef", ascending=False).head(15).iloc[::-1]
    top15_rf = imp_df.sort_values("rf_importance", ascending=False).head(15).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.8))
    colors_lr = ["#d64541" if c > 0 else "#2b7bba" for c in top15_lr["lr_coef_signed"]]
    axes[0].barh(top15_lr["feature"], top15_lr["lr_abs_coef"], color=colors_lr, edgecolor="black", linewidth=0.4)
    axes[0].set_title("Top 15 Sensors — LogisticRegression |Coef| (Red=+, Blue=-)")
    axes[0].set_xlabel("Absolute Standardized Coefficient")
    axes[0].set_ylabel("Anonymous Sensor Feature")

    axes[1].barh(top15_rf["feature"], top15_rf["rf_importance"], color="#16a085", edgecolor="black", linewidth=0.4)
    axes[1].set_title("Top 15 Sensors — RandomForest Feature Importance")
    axes[1].set_xlabel("Mean Decrease in Impurity")
    axes[1].set_ylabel("Anonymous Sensor Feature")
    fig.tight_layout()
    p_fi = reports_p3_dir / "feature_importance.png"
    fig.savefig(p_fi, dpi=150)
    plt.close(fig)
    saved.append(p_fi)

    return saved


def write_phase3_modeling_report(
    split_plan: TrainValTestSplit,
    comp_df: pd.DataFrame,
    selected_name: str,
    selected_t: float,
    test_metrics: dict,
    imp_df: pd.DataFrame,
    out_path: Path,
) -> None:
    """Write concise, evidence-grounded `reports/phase3/phase3_modeling_report.md`."""
    meta = split_plan.to_metadata_dict()
    comp_rows = "\n".join(
        f"| `{r['model']}` | {r['val_threshold']:.2f} | {r['val_pr_auc']:.4f} | {r['val_roc_auc']:.4f} | "
        f"{r['val_precision']:.4f} | {r['val_recall']:.4f} | {r['val_f1']:.4f} | {r['val_f2']:.4f} | "
        f"{r['test_pr_auc']:.4f} | {r['test_roc_auc']:.4f} | {r['test_precision']:.4f} | "
        f"{r['test_recall']:.4f} | {r['test_f1']:.4f} | {r['test_f2']:.4f} |"
        for _, r in comp_df.iterrows()
    )
    top15_rows = "\n".join(
        f"| {int(r['combined_rank'])} | `{r['feature']}` | {r['lr_coef_signed']:+.4f} | {r['rf_importance']:.5f} |"
        for _, r in imp_df.head(15).iterrows()
    )

    content = f"""# Phase 3 Predictive Quality Modeling Report — UCI SECOM

## 1. Chronological Split & Leakage Prevention
- **Method:** Reused Phase 1 `load_raw_secom()` and Phase 2 `fit_cleaning_plan()` inside `SecomTrainingPreprocessor`, fitting all feature filtering (`constant`, `>=99% near-constant`, `>50% missing`), median imputation, and `StandardScaler` strictly on the Training partition (`y` ignored). Raw `timestamp` and `target_label` were never used as predictors, and repeated-timestamp groups were kept intact across boundaries.
- **Train (`{meta['train']['start_timestamp']}` → `{meta['train']['end_timestamp']}`):** `{meta['train']['rows']}` records (`{meta['train']['passes_minus1']}` Pass, `{meta['train']['fails_1']}` Fail / `{meta['train']['fail_rate_pct']:.2f}%`)
- **Validation (`{meta['validation']['start_timestamp']}` → `{meta['validation']['end_timestamp']}`):** `{meta['validation']['rows']}` records (`{meta['validation']['passes_minus1']}` Pass, `{meta['validation']['fails_1']}` Fail / `{meta['validation']['fail_rate_pct']:.2f}%`)
- **Held-out Test (`{meta['test']['start_timestamp']}` → `{meta['test']['end_timestamp']}`):** `{meta['test']['rows']}` records (`{meta['test']['passes_minus1']}` Pass, `{meta['test']['fails_1']}` Fail / `{meta['test']['fail_rate_pct']:.2f}%`)

*Small-Sample Limitation:* The chronological validation window (`2008-09`) contains `{meta['validation']['fails_1']}` Fail examples (`{meta['validation']['fail_rate_pct']:.2f}%`) and the October held-out test set contains `{meta['test']['fails_1']}` Fail examples (`{meta['test']['fail_rate_pct']:.2f}%`). Per project safeguards, we preserve chronological ordering rather than switching to random splits.

## 2. Model Comparison (Validation-Only Selection & Thresholding)
| Model | Val t* | Val PR-AUC | Val ROC-AUC | Val Prec | Val Rec | Val F1 | Val F2 | Test PR-AUC | Test ROC-AUC | Test Prec | Test Rec | Test F1 | Test F2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{comp_rows}

- **Selected Model:** **`{selected_name}`** (selected solely from Validation performance: highest Validation PR-AUC `={comp_df.loc[comp_df['model']==selected_name, 'val_pr_auc'].iloc[0]:.4f}` with strong Fail Recall `={comp_df.loc[comp_df['model']==selected_name, 'val_recall'].iloc[0]:.4f}`).
- **Selected Decision Threshold (Validation-Only):** **`t* = {selected_t:.2f}`** (maximizing Validation `F2` within a `1%–40%` flag rate).
- **Final Held-Out Test Evaluation (`{selected_name}` at `t* = {selected_t:.2f}`):**
  - PR-AUC: `{test_metrics['pr_auc']:.4f}` | ROC-AUC: `{test_metrics['roc_auc']:.4f}`
  - Fail Precision: `{test_metrics['fail_precision']:.4f}` | Fail Recall: `{test_metrics['fail_recall']:.4f}` | F1: `{test_metrics['fail_f1']:.4f}` | F2: `{test_metrics['fail_f2']:.4f}`
  - Confusion Matrix: `TN={test_metrics['tn']}`, `FP={test_metrics['fp']}`, `FN={test_metrics['fn']}`, `TP={test_metrics['tp']}`

## 3. Visualisations
- `confusion_matrix.png`: Compares Validation vs. Held-out Test confusion matrices at `t* = {selected_t:.2f}`.
- `precision_recall_curve.png`: Shows Precision–Recall trade-offs against the `{meta['validation']['fail_rate_pct']:.2f}%` validation and `{meta['test']['fail_rate_pct']:.2f}%` test base rates.
- `roc_curve.png`: Shows TPR vs. FPR across thresholds for all three ML models.
- `feature_importance.png`: Displays the top 15 sensors from `LogisticRegression` standardized coefficients and `RandomForest` impurity importance.

## 4. Top 15 Predictive Anonymous Sensors (Association Only — Not Causation)
| Rank | Sensor | LogReg Signed Coef | RandomForest Importance |
|---:|---|---:|---:|
{top15_rows}

*Causality Safeguard:* All sensors are anonymous; coefficients and tree importances reflect statistical predictive associations in historical data, not physical root causes.
"""
    out_path.write_text(content, encoding="utf-8")


def run_phase3_pipeline(
    raw_dir: Path = DATA_RAW_DIR,
    models_dir: Path = MODELS_DIR,
    reports_p3_dir: Path = REPORTS_DIR / "phase3",
) -> dict:
    """Execute the fast, reproducible Phase 3 modeling pipeline and write all required deliverables."""
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_p3_dir.mkdir(parents=True, exist_ok=True)

    sensors_df, labels_df, y_series = prepare_chronological_dataset(raw_dir)
    y = y_series.to_numpy(dtype=int)
    split_plan = build_train_val_test_splits(labels_df, pre_test_train_frac=0.60, test_cutoff="2008-10-01 00:00:00")

    X_train = sensors_df.iloc[split_plan.train_indices]
    y_train = y[split_plan.train_indices]
    X_val = sensors_df.iloc[split_plan.val_indices]
    y_val = y[split_plan.val_indices]
    X_test = sensors_df.iloc[split_plan.test_indices]
    y_test = y[split_plan.test_indices]

    models = build_phase3_models()
    fitted_models: dict[str, Pipeline] = {}
    val_probs: dict[str, np.ndarray] = {}
    test_probs: dict[str, np.ndarray] = {}
    comp_rows: list[dict] = []

    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        fitted_models[name] = pipe

        p_val = pipe.predict_proba(X_val)[:, 1]
        p_test = pipe.predict_proba(X_test)[:, 1]
        val_probs[name] = p_val
        test_probs[name] = p_test

        if name == "Dummy_Majority":
            t_star = 0.50
        else:
            _, t_star = sweep_thresholds(y_val, p_val)

        vm = compute_binary_metrics(y_val, p_val, threshold=t_star)
        tm = compute_binary_metrics(y_test, p_test, threshold=t_star)

        comp_rows.append(
            {
                "model": name,
                "val_threshold": t_star,
                "val_pr_auc": vm["pr_auc"],
                "val_roc_auc": vm["roc_auc"],
                "val_precision": vm["fail_precision"],
                "val_recall": vm["fail_recall"],
                "val_f1": vm["fail_f1"],
                "val_f2": vm["fail_f2"],
                "val_accuracy": vm["accuracy"],
                "test_pr_auc": tm["pr_auc"],
                "test_roc_auc": tm["roc_auc"],
                "test_precision": tm["fail_precision"],
                "test_recall": tm["fail_recall"],
                "test_f1": tm["fail_f1"],
                "test_f2": tm["fail_f2"],
                "test_accuracy": tm["accuracy"],
                "test_tp": tm["tp"],
                "test_fp": tm["fp"],
                "test_fn": tm["fn"],
                "test_tn": tm["tn"],
            }
        )

    comp_df = pd.DataFrame(comp_rows)
    comp_df.to_csv(reports_p3_dir / "model_comparison.csv", index=False)

    # Select best ML model strictly by Validation PR-AUC (tie-break: Validation F2 & Recall)
    ml_candidates = comp_df[comp_df["model"] != "Dummy_Majority"].sort_values(
        ["val_pr_auc", "val_f2", "val_recall"], ascending=[False, False, False]
    )
    selected_name = str(ml_candidates.iloc[0]["model"])
    selected_t = float(ml_candidates.iloc[0]["val_threshold"])
    selected_pipe = fitted_models[selected_name]

    # Single final evaluation outputs on held-out test set for selected model
    sel_test_prob = test_probs[selected_name]
    sel_test_pred = (sel_test_prob >= selected_t).astype(int)
    sel_test_pred_labels = np.where(sel_test_pred == 1, 1, -1)
    y_test_raw_labels = np.where(y_test == 1, 1, -1)

    test_metrics = compute_binary_metrics(y_test, sel_test_prob, threshold=selected_t)
    test_metrics["selected_model"] = selected_name
    test_metrics["selected_threshold"] = selected_t
    test_metrics["trained_on_test_set"] = False
    (reports_p3_dir / "test_metrics.json").write_text(
        json.dumps(test_metrics, indent=2), encoding="utf-8"
    )

    cls_report = classification_report(
        y_test_raw_labels,
        sel_test_pred_labels,
        labels=[-1, 1],
        target_names=["Pass (-1)", "Fail (1)"],
        digits=4,
        zero_division=0,
    )
    (reports_p3_dir / "classification_report.txt").write_text(
        f"Selected Model: {selected_name} (threshold={selected_t:.2f})\n"
        f"Held-out Test Set: {split_plan.test_start} to {split_plan.test_end} (n={len(y_test)})\n\n"
        + cls_report,
        encoding="utf-8",
    )

    imp_df = compute_lightweight_feature_importance(fitted_models, reports_p3_dir)
    generate_phase3_plots(
        selected_name=selected_name,
        selected_t=selected_t,
        y_val=y_val,
        y_test=y_test,
        val_probs=val_probs,
        test_probs=test_probs,
        comp_df=comp_df,
        imp_df=imp_df,
        reports_p3_dir=reports_p3_dir,
    )
    write_phase3_modeling_report(
        split_plan=split_plan,
        comp_df=comp_df,
        selected_name=selected_name,
        selected_t=selected_t,
        test_metrics=test_metrics,
        imp_df=imp_df,
        out_path=reports_p3_dir / "phase3_modeling_report.md",
    )

    # Save trained pipeline & metadata under models/
    joblib.dump(selected_pipe, models_dir / "selected_model.joblib")
    for name, pipe in fitted_models.items():
        joblib.dump(pipe, models_dir / f"{name.lower()}_model.joblib")

    prep_step = selected_pipe.named_steps["prep"]
    (models_dir / "split_boundaries.json").write_text(
        json.dumps(split_plan.to_metadata_dict(), indent=2), encoding="utf-8"
    )
    (models_dir / "feature_lists.json").write_text(
        json.dumps(
            {
                "input_raw_features_count": len(prep_step.input_features_),
                "kept_features_count": len(prep_step.kept_features_),
                "removed_features_count": len(prep_step.removed_features_),
                "kept_features": prep_step.kept_features_,
                "removed_features": prep_step.removed_features_,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (models_dir / "preprocessing_config.json").write_text(
        json.dumps(
            {
                "random_seed": RANDOM_SEED,
                "preprocessor": "SecomTrainingPreprocessor (wraps Phase 2 fit_cleaning_plan)",
                "missing_cutoff": prep_step.missing_cutoff,
                "near_constant_threshold": prep_step.near_constant_threshold,
                "fit_exclusively_on": "chronological Train partition",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (models_dir / "model_metadata.json").write_text(
        json.dumps(
            {
                "random_seed": RANDOM_SEED,
                "selected_model": selected_name,
                "selected_threshold": selected_t,
                "selection_basis": "Validation PR-AUC (tie-break Validation F2 and Recall)",
                "trained_on_holdout": False,
                "test_metrics": test_metrics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "split_plan": split_plan,
        "comparison_df": comp_df,
        "selected_model_name": selected_name,
        "selected_threshold": selected_t,
        "test_metrics": test_metrics,
        "feature_importance_df": imp_df,
    }


def main() -> None:
    res = run_phase3_pipeline()
    print("Selected model:", res["selected_model_name"], "| Threshold:", res["selected_threshold"])
    cols = ["model", "val_threshold", "val_pr_auc", "val_recall", "val_precision", "val_f2", "test_pr_auc", "test_roc_auc", "test_precision", "test_recall", "test_f1", "test_f2"]
    print(res["comparison_df"][cols].to_string(index=False))


if __name__ == "__main__":
    main()
