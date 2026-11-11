"""Phase 4: Interactive Streamlit Dashboard — Smart Manufacturing Predictive Quality Analytics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from secom_project import MODELS_DIR, REPORTS_DIR
from secom_project.inference import (
    build_sample_sensor_csv_bytes,
    load_selected_model_and_metadata,
    validate_and_predict_dataframe,
)

st.set_page_config(
    page_title="Smart Manufacturing Quality Analytics | UCI SECOM",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Subtle industrial analytics styling
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 65%, #0369a1 100%);
        color: #f8fafc;
        padding: 1.25rem 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1.25rem;
        border-left: 6px solid #38bdf8;
    }
    .hero-banner h1 { margin: 0; font-size: 1.65rem; font-weight: 700; color: #ffffff; }
    .hero-banner p { margin: 0.35rem 0 0 0; font-size: 0.95rem; color: #cbd5e1; }
    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color, #1e293b);
        border: 1px solid rgba(148, 163, 184, 0.35);
        padding: 0.85rem 1rem;
        border-radius: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_cached_model_bundle() -> tuple[object | None, dict | None, str | None]:
    """Load the saved Phase 3 selected model pipeline once without retraining."""
    try:
        model, meta = load_selected_model_and_metadata(MODELS_DIR)
        return model, meta, None
    except Exception as exc:  # noqa: BLE001
        return None, None, str(exc)


@st.cache_data(show_spinner=False)
def load_json_safe(path_str: str) -> dict | None:
    p = Path(path_str)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_csv_safe(path_str: str) -> pd.DataFrame | None:
    p = Path(path_str)
    if not p.exists():
        return None
    return pd.read_csv(p)


@st.cache_data(show_spinner=False)
def load_text_safe(path_str: str) -> str | None:
    p = Path(path_str)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def show_image_safe(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")
    else:
        st.warning(f"Chart file not found: `{path}`")


def render_overview(
    audit_json: dict | None,
    split_json: dict | None,
    model_meta: dict | None,
) -> None:
    st.subheader("Section 1 — Project Overview")
    st.markdown(
        "**Research Question:** *Can inline semiconductor manufacturing sensor measurements predict "
        "wafer Pass/Fail yield excursions, and which anonymous sensor signals are most strongly associated "
        "with failure predictions?*"
    )

    if audit_json is None:
        st.warning("Phase 1 audit summary (`reports/secom_audit_summary.json`) was not found.")
        return

    q = audit_json["quality_and_structure"]
    dim = q["dimensions"]
    tgt = q["target_distribution"]
    miss = q["missing_values"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Wafer Records", f"{dim['sensor_rows']:,}")
    c2.metric("Raw Sensors", f"{dim['sensor_columns']}", "440 active after cleaning")
    c3.metric("Pass (-1)", f"{tgt['pass_count']:,}", f"{tgt['pass_pct']:.2f}%")
    c4.metric("Fail (1)", f"{tgt['fail_count']:,}", f"{tgt['fail_pct']:.2f}% (14.07:1)")
    c5.metric("Raw Missing Cells", f"{miss['sensor_missing_cells']:,}", f"{miss['sensor_missing_pct']:.2f}%")

    col_left, col_right = st.columns([1.05, 1.35])
    with col_left:
        fig_cls = px.pie(
            names=["Pass (-1)", "Fail (1)"],
            values=[tgt["pass_count"], tgt["fail_count"]],
            hole=0.52,
            color=["Pass (-1)", "Fail (1)"],
            color_discrete_map={"Pass (-1)": "#0284c7", "Fail (1)": "#dc2626"},
            title="Target Class Imbalance (1,567 Wafers)",
        )
        fig_cls.update_traces(textinfo="label+value+percent")
        fig_cls.update_layout(margin=dict(t=45, b=15, l=15, r=15), height=340)
        st.plotly_chart(fig_cls, width="stretch")

    with col_right:
        st.markdown("#### Dataset & Chronological Partitioning Summary")
        if split_json:
            split_rows = []
            for key, label in [("train", "Train"), ("validation", "Validation"), ("test", "Held-Out Test")]:
                s = split_json[key]
                split_rows.append(
                    {
                        "Partition": label,
                        "Time Window": f"{s['start_timestamp']} → {s['end_timestamp']}",
                        "Rows": s["rows"],
                        "Pass (-1)": s["passes_minus1"],
                        "Fail (1)": s["fails_1"],
                        "Fail Rate (%)": f"{s['fail_rate_pct']:.2f}%",
                    }
                )
            st.dataframe(pd.DataFrame(split_rows), width="stretch", hide_index=True)

        st.info(
            "**Key Research Findings:**\n"
            "- **100% Incomplete Rows:** Every wafer record has at least one missing sensor reading (`0.68%`–`25.76%`), making row deletion infeasible; unsupervised training-only median imputation is used after dropping `150` constant/near-constant/`>50%` missing columns.\n"
            "- **Strong Process Non-Stationarity:** Monthly defect rates shift nearly `8×` (`22.22%` Jul → `9.19%` Aug → `2.88%` Sep → `6.13%` Oct), requiring strict chronological splitting rather than random CV.\n"
            "- **Non-Causal Associations:** Anonymous sensors (`sensor_059`, `sensor_000`, `sensor_021`) carry genuine ranking signal, though covariate drift degrades fixed thresholds over multi-week horizons."
        )


def render_eda(
    audit_json: dict | None,
    eda_json: dict | None,
    stats_df: pd.DataFrame | None,
    missing_df: pd.DataFrame | None,
) -> None:
    st.subheader("Section 2 — Exploratory Data Analysis & Statistical Audit")

    col_a, col_b = st.columns(2)
    with col_a:
        if audit_json and "chronological_timestamp_analysis" in audit_json:
            monthly_df = pd.DataFrame(audit_json["chronological_timestamp_analysis"]["monthly_fail_distribution"])
            fig_m = px.line(
                monthly_df,
                x="year_month",
                y="fail_rate_pct",
                markers=True,
                text="fail_rate_pct",
                title="Monthly Failure-Rate Trend (Jul–Oct 2008)",
                labels={"year_month": "Production Month", "fail_rate_pct": "Fail Rate (%)"},
            )
            fig_m.update_traces(line=dict(color="#dc2626", width=3), marker=dict(size=9), textposition="top center", texttemplate="%{text:.2f}%")
            fig_m.update_layout(height=360, margin=dict(t=45, b=20, l=20, r=20), yaxis_range=[0, 27])
            st.plotly_chart(fig_m, width="stretch")
        else:
            st.warning("Monthly timestamp audit data unavailable.")

    with col_b:
        if missing_df is not None:
            top_miss = missing_df.sort_values("missing_pct", ascending=False).head(20)
            fig_miss = px.bar(
                top_miss.iloc[::-1],
                x="missing_pct",
                y="feature",
                orientation="h",
                color="cleaning_action",
                title="Top 20 Sensor Features by Missingness (%)",
                labels={"missing_pct": "Missing (%)", "feature": "Sensor", "cleaning_action": "Phase 2 Action"},
            )
            fig_miss.add_vline(x=50.0, line_dash="dash", line_color="#f59e0b", annotation_text="50% Cutoff")
            fig_miss.update_layout(height=360, margin=dict(t=45, b=20, l=20, r=20), legend=dict(orientation="h", y=-0.22))
            st.plotly_chart(fig_miss, width="stretch")
        else:
            st.warning("Missing-value report CSV unavailable.")

    st.markdown("#### Statistical Findings & Benjamini–Hochberg FDR Multiple-Testing Correction")
    if eda_json and stats_df is not None:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Sensors Tested (MW-U)", f"{len(stats_df)}")
        m2.metric("Raw p < 0.05", f"{eda_json.get('raw_significant_0_05_count', 'N/A')}")
        m3.metric("BH-FDR q < 0.05 (Imputed)", f"{eda_json.get('fdr_bh_significant_0_05_count', 'N/A')}")
        m4.metric("Collinear Pairs (|r| >= 0.99)", f"{eda_json['correlation_summary']['pearson_pairs_abs_ge_0_99']}")

        top_fdr = stats_df.sort_values("mannwhitney_p_fdr_bh").head(15)[
            [
                "feature",
                "pearson_r_with_fail",
                "spearman_rho_with_fail",
                "mannwhitney_p",
                "mannwhitney_p_fdr_bh",
                "is_fdr_significant_0_05",
                "pass_median",
                "fail_median",
                "skewness",
            ]
        ]
        st.dataframe(top_fdr, width="stretch", hide_index=True)

    st.markdown("#### Sensor Correlation Heatmap & Phase 2 Visualisations")
    fig_dir = REPORTS_DIR / "figures"
    c1, c2 = st.columns(2)
    with c1:
        show_image_safe(fig_dir / "correlation_heatmap.png", "Pearson Correlation Heatmap (Top 20 Target-Associated Sensors)")
    with c2:
        show_image_safe(fig_dir / "pass_fail_sensor_comparison.png", "Upper-Quantile Defect Escalation & sensor_059 Drift")

    with st.expander("View Additional Phase 2 Charts (Missingness Tiers, Distributions, Boxplots, Variability)"):
        g1, g2 = st.columns(2)
        with g1:
            show_image_safe(fig_dir / "missing_values.png", "Top 30 Missing Features & Missingness Tiers")
            show_image_safe(fig_dir / "sensor_distributions.png", "Representative Sensor Distributions")
        with g2:
            show_image_safe(fig_dir / "missing_percentage.png", "Feature & Record Missingness Distributions")
            show_image_safe(fig_dir / "pass_fail_boxplots.png", "Pass vs. Fail Boxplots (Top 6 Spearman Sensors)")
        show_image_safe(fig_dir / "feature_variability.png", "Feature Variability & Fail/Pass Dispersion Ratios")


def render_model_comparison(
    comp_df: pd.DataFrame | None,
    test_metrics: dict | None,
    cls_report: str | None,
) -> None:
    st.subheader("Section 3 — Predictive Model Comparison")
    if comp_df is None:
        st.warning("Phase 3 model comparison table (`reports/phase3/model_comparison.csv`) not found.")
        return

    if test_metrics:
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Selected Model", test_metrics["selected_model"])
        k2.metric("Validation Threshold t*", f"{test_metrics['selected_threshold']:.2f}")
        k3.metric("Held-Out Test PR-AUC", f"{test_metrics['pr_auc']:.4f}", "Base rate: 0.0613")
        k4.metric("Held-Out Test ROC-AUC", f"{test_metrics['roc_auc']:.4f}")
        k5.metric("Held-Out Fail Recall / F1", f"{test_metrics['fail_recall']:.4f}", f"F1: {test_metrics['fail_f1']:.4f}")
        st.info(
            "**Scientific Integrity Note:** `HistGradientBoosting` was selected solely on Validation PR-AUC (`0.2080`, `33.3%` recall at `t* = 0.19`). "
            "On the untouched October test set (`n=359`, `22` fails), ranking stayed above the `0.0613` base rate (`PR-AUC = 0.0828`, `ROC-AUC = 0.5968`), "
            "but temporal distribution shift pushed predicted scores below `t* = 0.19`, yielding `0 / 22` flagged detections (`TP = 0, FP = 13`)."
        )

    tab_val, tab_test = st.tabs(["Chronological Validation Metrics (Sep 2008, n=483)", "Held-Out Test Metrics (Oct 2008, n=359)"])
    with tab_val:
        val_cols = ["model", "val_threshold", "val_pr_auc", "val_roc_auc", "val_precision", "val_recall", "val_f1", "val_f2", "val_accuracy"]
        st.dataframe(comp_df[val_cols], width="stretch", hide_index=True)

    with tab_test:
        test_cols = ["model", "val_threshold", "test_pr_auc", "test_roc_auc", "test_precision", "test_recall", "test_f1", "test_f2", "test_accuracy", "test_tp", "test_fp", "test_fn", "test_tn"]
        st.dataframe(comp_df[test_cols], width="stretch", hide_index=True)

    melt_df = comp_df.melt(
        id_vars="model",
        value_vars=["val_pr_auc", "test_pr_auc", "val_f2", "test_f2"],
        var_name="Metric",
        value_name="Score",
    )
    fig_comp = px.bar(
        melt_df,
        x="model",
        y="Score",
        color="Metric",
        barmode="group",
        title="Validation vs. Held-Out Test PR-AUC & F2 Comparison",
    )
    fig_comp.update_layout(height=370, margin=dict(t=45, b=20, l=20, r=20))
    st.plotly_chart(fig_comp, width="stretch")

    p3_dir = REPORTS_DIR / "phase3"
    c1, c2, c3 = st.columns(3)
    with c1:
        show_image_safe(p3_dir / "confusion_matrix.png", "Validation & Test Confusion Matrices")
    with c2:
        show_image_safe(p3_dir / "precision_recall_curve.png", "Precision–Recall Curves")
    with c3:
        show_image_safe(p3_dir / "roc_curve.png", "ROC Curves")

    if cls_report:
        with st.expander("Held-Out Test Classification Report (Selected Model)"):
            st.code(cls_report, language="text")


def render_interactive_prediction(model: object | None, model_meta: dict | None, model_err: str | None) -> None:
    st.subheader("Section 4 — Interactive Wafer Failure Prediction")
    if model_err or model is None or model_meta is None:
        st.error(f"Could not load saved Phase 3 model: {model_err}")
        return

    threshold = float(model_meta["selected_threshold"])
    st.markdown(
        f"Loaded saved pipeline **`{model_meta['selected_model']}`** (`models/selected_model.joblib`, "
        f"fit exclusively on Pre-Oct 2008 training data; validation-selected threshold **`t* = {threshold:.2f}`**). "
        "Target labels (`target_label`) and timestamps are never used as predictors."
    )

    col_dl, col_info = st.columns([1.0, 2.0])
    with col_dl:
        try:
            sample_bytes = build_sample_sensor_csv_bytes(n_rows=10)
            st.download_button(
                label="Download Sample Sensor CSV (10 Real Rows)",
                data=sample_bytes,
                file_name="secom_sample_sensors_10rows.csv",
                mime="text/csv",
            )
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Sample CSV generator unavailable: {exc}")
    with col_info:
        st.caption(
            "Upload a CSV containing the active SECOM sensor columns (`sensor_000`–`sensor_589` subset). "
            "Missing sensor values (`NaN`) are automatically imputed using training-fitted medians inside the saved pipeline."
        )

    uploaded = st.file_uploader("Upload Sensor Measurements CSV", type=["csv"])
    if uploaded is None:
        st.info("Upload a sensor CSV above (or download the 10-row sample CSV and upload it) to generate live predictions.")
        return

    try:
        try:
            raw_df = pd.read_csv(uploaded)
        except pd.errors.EmptyDataError as exc:
            raise ValueError("Uploaded CSV file is empty (no header or sensor columns).") from exc
        pred_df, warn_msgs = validate_and_predict_dataframe(raw_df, model, threshold=threshold)
        for msg in warn_msgs:
            st.info(msg)

        n_total = len(pred_df)
        n_flagged = int((pred_df["predicted_label"] == 1).sum())
        max_prob = float(pred_df["fail_probability"].max())
        mean_prob = float(pred_df["fail_probability"].mean())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Records Scored", f"{n_total}")
        m2.metric("Flagged High Risk (Fail=1)", f"{n_flagged}", f"{n_flagged/n_total*100:.1f}%")
        m3.metric("Max Failure Probability", f"{max_prob:.4f}")
        m4.metric("Mean Failure Probability", f"{mean_prob:.4f}")

        fig_p = px.histogram(
            pred_df,
            x="fail_probability",
            color="predicted_outcome",
            nbins=20,
            title="Predicted Failure Probability Distribution for Uploaded Records",
            labels={"fail_probability": "Predicted P(Fail)", "predicted_outcome": "Classification"},
            color_discrete_map={"Pass (-1)": "#0284c7", "Fail (1)": "#dc2626"},
        )
        fig_p.add_vline(x=threshold, line_dash="dash", line_color="#f59e0b", annotation_text=f"t* = {threshold:.2f}")
        fig_p.update_layout(height=320, margin=dict(t=45, b=20, l=20, r=20))
        st.plotly_chart(fig_p, width="stretch")

        st.dataframe(pred_df, width="stretch", hide_index=True)
        st.download_button(
            label="Download Predictions CSV",
            data=pred_df.to_csv(index=False).encode("utf-8"),
            file_name="secom_predictions.csv",
            mime="text/csv",
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Input validation failed: {exc}")


def render_explainability_and_findings(imp_df: pd.DataFrame | None, audit_json: dict | None) -> None:
    st.subheader("Section 5 — Explainability, Temporal Drift & Recommendations")

    if imp_df is not None:
        top15 = imp_df.head(15).copy()
        fig_imp = px.bar(
            top15.iloc[::-1],
            x="combined_score",
            y="feature",
            orientation="h",
            color="rf_importance",
            color_continuous_scale="Teal",
            title="Top 15 Predictive Anonymous Sensors (Combined LogReg + RandomForest Rank)",
            labels={"combined_score": "Normalized Combined Importance", "feature": "Anonymous Sensor", "rf_importance": "RF Importance"},
        )
        fig_imp.update_layout(height=430, margin=dict(t=45, b=20, l=20, r=20))
        c1, c2 = st.columns([1.15, 1.0])
        with c1:
            st.plotly_chart(fig_imp, width="stretch")
        with c2:
            st.dataframe(
                top15[["combined_rank", "feature", "lr_coef_signed", "rf_importance", "lr_rank", "rf_rank"]],
                width="stretch",
                hide_index=True,
                height=430,
            )
        show_image_safe(REPORTS_DIR / "phase3" / "feature_importance.png", "LogisticRegression Coefficients vs. RandomForest Importance")
    else:
        st.warning("Feature importance CSV (`reports/phase3/feature_importance.csv`) not found.")

    st.warning(
        "**Causality & Anonymity Safeguard:** All sensors (`sensor_000`–`sensor_589`) are anonymous without engineering units or process-step metadata. "
        "Feature rankings indicate statistical predictive associations, **not** physical root causes."
    )

    col_lim, col_rec = st.columns(2)
    with col_lim:
        st.markdown(
            "#### Temporal Distribution Shift & Limitations\n"
            "- **Non-Stationary Yield:** Monthly fail rates shift from `22.22%` (Jul) → `2.88%` (Sep) → `6.13%` (Oct).\n"
            "- **Fixed-Threshold Degradation:** `HistGradientBoosting` achieved `0.2080` PR-AUC (`33.3%` recall, `23.8%` precision) on September validation at `t* = 0.19`, but October covariate drift depressed its predicted scores below `0.19` (`0/22` TP at fixed `t*`, `0.0828` PR-AUC).\n"
            "- **Small Positive Sample Size:** Only `104` Fail wafers overall (`15` validation, `22` test) yield wide metric variance."
        )
    with col_rec:
        st.markdown(
            "#### Manufacturing Quality Monitoring Recommendations\n"
            "1. **Rolling Window Retraining:** Retrain predictive models on sliding recent production windows (e.g., 30–45 days) rather than static historical snapshots.\n"
            "2. **Adaptive SPC & Threshold Recalibration:** Monitor monthly sensor baseline drift (e.g., `sensor_059`) and recalibrate alarm thresholds when flagged-wafer rates deviate from expected baseline bands.\n"
            "3. **Human-in-the-Loop Triage:** Use model failure probabilities for risk-ranked metrology inspection rather than autonomous wafer scrapping."
        )


def main() -> None:
    st.markdown(
        """
        <div class="hero-banner">
            <h1>Smart Manufacturing: Intelligent Process Quality Analysis & Predictive Defect Detection</h1>
            <p>UCI SECOM Semiconductor Manufacturing Dataset &bull; Leakage-Safe Chronological ML Pipeline (Phases 1–4)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    model, model_meta, model_err = get_cached_model_bundle()
    audit_json = load_json_safe(str(REPORTS_DIR / "secom_audit_summary.json"))
    eda_json = load_json_safe(str(REPORTS_DIR / "phase2_eda_summary.json"))
    split_json = load_json_safe(str(MODELS_DIR / "split_boundaries.json"))
    stats_df = load_csv_safe(str(REPORTS_DIR / "phase2_statistical_summary.csv"))
    missing_df = load_csv_safe(str(REPORTS_DIR / "phase2_missing_value_report.csv"))
    comp_df = load_csv_safe(str(REPORTS_DIR / "phase3" / "model_comparison.csv"))
    test_metrics = load_json_safe(str(REPORTS_DIR / "phase3" / "test_metrics.json"))
    cls_report = load_text_safe(str(REPORTS_DIR / "phase3" / "classification_report.txt"))
    imp_df = load_csv_safe(str(REPORTS_DIR / "phase3" / "feature_importance.csv"))

    with st.sidebar:
        st.title("Navigation")
        section = st.radio(
            "Dashboard Section",
            [
                "1. Project Overview",
                "2. Exploratory Data Analysis",
                "3. Predictive Model Comparison",
                "4. Interactive Prediction",
                "5. Explainability & Findings",
            ],
        )
        st.divider()
        st.markdown("### Saved Model Status")
        if model_meta:
            st.success(f"**Model:** `{model_meta['selected_model']}`")
            st.caption(
                f"Threshold: `t* = {model_meta['selected_threshold']:.2f}`  \n"
                f"Trained on Holdout: `{model_meta['trained_on_holdout']}`  \n"
                f"Seed: `{model_meta['random_seed']}`"
            )
        else:
            st.error("Saved model not loaded")

    if section == "1. Project Overview":
        render_overview(audit_json, split_json, model_meta)
    elif section == "2. Exploratory Data Analysis":
        render_eda(audit_json, eda_json, stats_df, missing_df)
    elif section == "3. Predictive Model Comparison":
        render_model_comparison(comp_df, test_metrics, cls_report)
    elif section == "4. Interactive Prediction":
        render_interactive_prediction(model, model_meta, model_err)
    else:
        render_explainability_and_findings(imp_df, audit_json)


if __name__ == "__main__":
    main()
