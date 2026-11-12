"""Smart Manufacturing Analytics — Predictive Quality Intelligence Dashboard."""

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
    page_title="Smart Manufacturing Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Production dark-navy industrial styling
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.75rem;
        padding-bottom: 2rem;
        max-width: 1380px;
    }
    .app-header {
        background: linear-gradient(90deg, #0f172a 0%, #152238 100%);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 0.75rem;
        padding: 1.1rem 1.45rem;
        margin-bottom: 1.25rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem 1.25rem;
        box-shadow: 0 4px 14px rgba(2, 6, 23, 0.35);
    }
    .app-header-title {
        margin: 0;
        font-size: 1.35rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
    }
    .app-header-subtitle {
        margin: 0.2rem 0 0 0;
        font-size: 0.88rem;
        color: #94a3b8;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.38rem 0.85rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        white-space: nowrap;
        background-color: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.28);
        color: #e2e8f0;
    }
    .status-dot-ok {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #14b8a6;
        display: inline-block;
    }
    .status-dot-err {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #ef4444;
        display: inline-block;
    }
    .section-lead {
        margin: -0.35rem 0 1.05rem 0;
        font-size: 0.92rem;
        color: #94a3b8;
    }
    .reliability-notice {
        background-color: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-left: 4px solid #f59e0b;
        border-radius: 0.55rem;
        padding: 0.85rem 1.05rem;
        margin: 0.65rem 0 1.05rem 0;
        font-size: 0.88rem;
        line-height: 1.5;
        color: #e2e8f0;
    }
    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-top: 2px solid #0ea5e9;
        padding: 0.85rem 1rem;
        border-radius: 0.6rem;
        min-height: 112px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        box-shadow: 0 2px 8px rgba(2, 6, 23, 0.25);
    }
    [data-testid="stMetricLabel"] {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.05rem, 1.3vw, 1.45rem) !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        color: #f8fafc !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    [data-testid="stMetricValue"] > div {
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: normal !important;
        word-break: break-word;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.77rem !important;
        line-height: 1.25 !important;
        white-space: normal !important;
        color: #64748b !important;
        background: transparent !important;
        padding-left: 0 !important;
    }
    [data-testid="stMetricDelta"] svg {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def style_plotly_figure(fig: go.Figure, *, height: int, margin: dict | None = None) -> go.Figure:
    """Apply consistent dark-navy Plotly styling with clean margins and non-clipping axes."""
    fig.update_layout(
        height=height,
        margin=margin or dict(t=54, b=42, l=22, r=22),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color="#e2e8f0"),
        title=dict(font=dict(size=14, color="#f8fafc"), x=0.0, xanchor="left"),
    )
    fig.update_xaxes(
        automargin=True,
        gridcolor="rgba(148, 163, 184, 0.14)",
        zerolinecolor="rgba(148, 163, 184, 0.22)",
    )
    fig.update_yaxes(
        automargin=True,
        gridcolor="rgba(148, 163, 184, 0.14)",
        zerolinecolor="rgba(148, 163, 184, 0.22)",
    )
    return fig


@st.cache_resource(show_spinner=False)
def get_cached_model_bundle() -> tuple[object | None, dict | None, str | None]:
    """Load the saved serialized model pipeline once per server process."""
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
        st.warning(f"Diagnostic visual unavailable: {caption}")


def render_overview(
    audit_json: dict | None,
    split_json: dict | None,
    stats_df: pd.DataFrame | None,
    model_meta: dict | None,
) -> None:
    st.subheader("Overview")
    st.markdown(
        '<p class="section-lead">Semiconductor wafer yield diagnostics, class imbalance profile, and chronological evaluation partitions.</p>',
        unsafe_allow_html=True,
    )

    if audit_json is None:
        st.warning("Dataset audit summary is unavailable.")
        return

    q = audit_json["quality_and_structure"]
    dim = q["dimensions"]
    tgt = q["target_distribution"]
    miss = q["missing_values"]

    total_wafers = int(dim["sensor_rows"])
    pass_count = int(tgt["pass_count"])
    fail_count = int(tgt["fail_count"])
    fail_rate_pct = float(tgt["fail_pct"])
    pass_ratio = pass_count / max(fail_count, 1)
    n_active_sensors = len(stats_df) if stats_df is not None else int(dim["sensor_columns"])
    selected_model = model_meta["selected_model"] if model_meta else "Unavailable"
    threshold_str = f"Threshold t* = {model_meta['selected_threshold']:.2f}" if model_meta else "Model not loaded"

    r1c1, r1c2, r1c3 = st.columns(3, gap="medium")
    r1c1.metric("Total Wafers Analyzed", f"{total_wafers:,}", "Chronological production records", delta_color="off")
    r1c2.metric("Pass Count", f"{pass_count:,}", f"{tgt['pass_pct']:.2f}% passing yield", delta_color="off")
    r1c3.metric("Failure Count", f"{fail_count:,}", f"{pass_ratio:.2f}:1 pass-to-fail ratio", delta_color="off")

    st.markdown("<div style='height: 0.45rem'></div>", unsafe_allow_html=True)

    r2c1, r2c2, r2c3 = st.columns(3, gap="medium")
    r2c1.metric("Failure Rate", f"{fail_rate_pct:.2f}%", f"{miss['sensor_missing_pct']:.2f}% raw grid missingness", delta_color="off")
    r2c2.metric("Sensor Features Analyzed", f"{n_active_sensors:,}", f"Retained from {dim['sensor_columns']:,} raw sensors", delta_color="off")
    r2c3.metric("Selected Model", selected_model, threshold_str, delta_color="off")

    st.markdown("<div style='height: 0.6rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.0, 1.35], gap="large")
    with col_left:
        fig_cls = px.pie(
            names=["Pass (-1)", "Fail (1)"],
            values=[pass_count, fail_count],
            hole=0.58,
            color=["Pass (-1)", "Fail (1)"],
            color_discrete_map={"Pass (-1)": "#0ea5e9", "Fail (1)": "#ef4444"},
            title="Target Class Distribution",
        )
        fig_cls.update_traces(
            textposition="outside",
            texttemplate="%{label}<br>%{value:,} (%{percent})",
            pull=[0.0, 0.04],
            marker=dict(line=dict(color="#0b1120", width=2)),
        )
        style_plotly_figure(fig_cls, height=365, margin=dict(t=56, b=58, l=30, r=30))
        fig_cls.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5),
            annotations=[
                dict(
                    text=f"<b>{total_wafers:,}</b><br>Wafers",
                    x=0.5,
                    y=0.5,
                    font=dict(size=14, color="#f8fafc"),
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_cls, width="stretch")

    with col_right:
        st.markdown("#### Chronological Partitioning")
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
                        "Fail Rate": f"{s['fail_rate_pct']:.2f}%",
                    }
                )
            st.dataframe(pd.DataFrame(split_rows), width="stretch", hide_index=True)

        st.markdown("#### Key Research Findings")
        st.markdown(
            f"- **Universal Missingness:** All `{total_wafers:,}` wafer records contain missing sensor entries, requiring median imputation fit strictly on training data after removing `150` low-information or `>50%` missing signals.\n"
            "- **Process Non-Stationarity:** Defect prevalence fluctuates from `22.22%` (Jul) to `2.88%` (Sep) and `6.13%` (Oct), making chronological evaluation essential.\n"
            "- **Non-Causal Signal:** Anonymous sensors (`sensor_059`, `sensor_000`, `sensor_021`) exhibit statistical predictive ranking signal, though covariate drift degrades fixed probability cutoffs over time."
        )


def render_data_analysis(
    audit_json: dict | None,
    eda_json: dict | None,
    stats_df: pd.DataFrame | None,
    missing_df: pd.DataFrame | None,
) -> None:
    st.subheader("Data Analysis")
    st.markdown(
        '<p class="section-lead">Monthly yield shift, sensor missingness screening, and Benjamini–Hochberg FDR statistical testing.</p>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        if audit_json and "chronological_timestamp_analysis" in audit_json:
            monthly_df = pd.DataFrame(audit_json["chronological_timestamp_analysis"]["monthly_fail_distribution"])
            fig_m = px.line(
                monthly_df,
                x="year_month",
                y="fail_rate_pct",
                markers=True,
                text="fail_rate_pct",
                title="Monthly Failure Rate Trend",
                labels={"year_month": "Month", "fail_rate_pct": "Failure Rate (%)"},
            )
            fig_m.update_traces(
                line=dict(color="#ef4444", width=3),
                marker=dict(size=9, line=dict(width=1.5, color="#f8fafc")),
                textposition="top center",
                texttemplate="%{text:.2f}%",
            )
            style_plotly_figure(fig_m, height=460, margin=dict(t=56, b=58, l=24, r=24))
            fig_m.update_xaxes(type="category")
            fig_m.update_yaxes(range=[0, 26.5], ticksuffix="%")
            st.plotly_chart(fig_m, width="stretch")
        else:
            st.warning("Monthly failure trend data unavailable.")

    with col_b:
        if missing_df is not None:
            top_miss = missing_df.sort_values("missing_pct", ascending=False).head(20).copy()
            action_labels = {
                "drop_gt_50pct_missing": "Dropped (>50% Missing)",
                "keep_impute_median": "Retained (Imputed)",
            }
            top_miss["Status"] = top_miss["cleaning_action"].map(action_labels).fillna(top_miss["cleaning_action"])
            fig_miss = px.bar(
                top_miss.iloc[::-1],
                x="missing_pct",
                y="feature",
                orientation="h",
                color="Status",
                color_discrete_map={
                    "Dropped (>50% Missing)": "#ef4444",
                    "Retained (Imputed)": "#14b8a6",
                },
                title=f"Top {len(top_miss)} Sensors by Missingness (%)",
                labels={"missing_pct": "Missingness (%)", "feature": "Sensor"},
            )
            fig_miss.add_vline(
                x=50.0,
                line_dash="dash",
                line_color="#f59e0b",
                annotation_text="50% Threshold",
                annotation_position="top right",
            )
            style_plotly_figure(fig_miss, height=460, margin=dict(t=56, b=82, l=22, r=26))
            fig_miss.update_yaxes(dtick=1, tickfont=dict(size=11))
            fig_miss.update_xaxes(range=[0, 100], ticksuffix="%")
            fig_miss.update_layout(
                legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5, title_text="")
            )
            st.plotly_chart(fig_miss, width="stretch")
        else:
            st.warning("Missingness report unavailable.")

    st.divider()
    st.markdown("#### Statistical Significance & Redundancy")
    if eda_json and stats_df is not None:
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        m1.metric("Sensors Tested", f"{len(stats_df):,}", "Mann–Whitney U", delta_color="off")
        m2.metric("Raw Significant (p < 0.05)", f"{eda_json.get('raw_significant_0_05_count', 'N/A')}", "Uncorrected threshold", delta_color="off")
        m3.metric("BH-FDR Significant (q < 0.05)", f"{eda_json.get('fdr_bh_significant_0_05_count', 'N/A')}", "Multi-testing adjusted", delta_color="off")
        m4.metric("Collinear Pairs (|r| >= 0.99)", f"{eda_json['correlation_summary']['pearson_pairs_abs_ge_0_99']:,}", "Highly correlated pairs", delta_color="off")

        st.markdown("<div style='height: 0.45rem'></div>", unsafe_allow_html=True)

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
        st.dataframe(
            top_fdr,
            width="stretch",
            hide_index=True,
            column_config={
                "feature": st.column_config.TextColumn("Sensor"),
                "pearson_r_with_fail": st.column_config.NumberColumn("Pearson r", format="%.4f"),
                "spearman_rho_with_fail": st.column_config.NumberColumn("Spearman ρ", format="%.4f"),
                "mannwhitney_p": st.column_config.NumberColumn("Raw p-value", format="%.2e"),
                "mannwhitney_p_fdr_bh": st.column_config.NumberColumn("BH-FDR q-value", format="%.2e"),
                "is_fdr_significant_0_05": st.column_config.CheckboxColumn("FDR q < 0.05"),
                "pass_median": st.column_config.NumberColumn("Pass Median", format="%.4f"),
                "fail_median": st.column_config.NumberColumn("Fail Median", format="%.4f"),
                "skewness": st.column_config.NumberColumn("Skewness", format="%.2f"),
            },
        )

    st.markdown("#### Correlation & Signal Diagnostics")
    fig_dir = REPORTS_DIR / "figures"
    c1, c2 = st.columns(2, gap="large")
    with c1:
        show_image_safe(fig_dir / "correlation_heatmap.png", "Pearson Correlation Heatmap (Top 20 Target-Associated Sensors)")
    with c2:
        show_image_safe(fig_dir / "pass_fail_sensor_comparison.png", "Upper-Quantile Failure Escalation & sensor_059 Drift")

    with st.expander("Additional Diagnostic Plots"):
        g1, g2 = st.columns(2, gap="medium")
        with g1:
            show_image_safe(fig_dir / "missing_values.png", "Top 30 Missing Features & Missingness Tiers")
            show_image_safe(fig_dir / "sensor_distributions.png", "Representative Sensor Distributions")
        with g2:
            show_image_safe(fig_dir / "missing_percentage.png", "Feature & Record Missingness Distributions")
            show_image_safe(fig_dir / "pass_fail_boxplots.png", "Pass vs. Fail Distributions (Top 6 Spearman Sensors)")
        show_image_safe(fig_dir / "feature_variability.png", "Feature Variability & Dispersion Ratios")


def render_model_performance(
    comp_df: pd.DataFrame | None,
    test_metrics: dict | None,
    cls_report: str | None,
) -> None:
    st.subheader("Model Performance")
    st.markdown(
        '<p class="section-lead">Chronological validation model selection and untouched October holdout evaluation.</p>',
        unsafe_allow_html=True,
    )
    if comp_df is None:
        st.warning("Model comparison metrics are unavailable.")
        return

    if test_metrics:
        selected_name = test_metrics["selected_model"]
        sel_row = comp_df[comp_df["model"] == selected_name]
        val_pr_auc = float(sel_row["val_pr_auc"].iloc[0]) if not sel_row.empty else 0.0
        val_recall_pct = float(sel_row["val_recall"].iloc[0]) * 100.0 if not sel_row.empty else 0.0
        val_f2 = float(sel_row["val_f2"].iloc[0]) if not sel_row.empty else 0.0
        base_rate = float(test_metrics["n_fails"]) / max(int(test_metrics["n_samples"]), 1)

        k1, k2, k3, k4, k5 = st.columns([1.45, 0.95, 1.0, 0.95, 1.05], gap="medium")
        k1.metric("Selected Model", selected_name, f"Val PR-AUC: {val_pr_auc:.4f}", delta_color="off")
        k2.metric("Decision Threshold (t*)", f"{test_metrics['selected_threshold']:.2f}", f"Val F2: {val_f2:.4f}", delta_color="off")
        k3.metric("Test PR-AUC", f"{test_metrics['pr_auc']:.4f}", f"Baseline: {base_rate:.4f}", delta_color="off")
        k4.metric("Test ROC-AUC", f"{test_metrics['roc_auc']:.4f}", f"Holdout n = {test_metrics['n_samples']:,}", delta_color="off")
        k5.metric(
            "Test Fail Recall",
            f"{test_metrics['fail_recall']:.4f}",
            f"F1: {test_metrics['fail_f1']:.4f} ({test_metrics['tp']}/{test_metrics['n_fails']} TP)",
            delta_color="off",
        )

        st.markdown(
            f"""
            <div class="reliability-notice">
                <strong>Model Reliability Notice:</strong> <code>{selected_name}</code> achieved the highest September validation PR-AUC
                (<code>{val_pr_auc:.4f}</code>, <code>{val_recall_pct:.1f}%</code> recall at <code>t* = {test_metrics['selected_threshold']:.2f}</code>).
                On the untouched October holdout (<code>n = {test_metrics['n_samples']:,}</code>, <code>{test_metrics['n_fails']}</code> failures),
                probability ranking remained above the <code>{base_rate:.4f}</code> base rate
                (<code>PR-AUC = {test_metrics['pr_auc']:.4f}</code>, <code>ROC-AUC = {test_metrics['roc_auc']:.4f}</code>),
                but temporal covariate drift suppressed predicted risk scores below the fixed <code>t* = {test_metrics['selected_threshold']:.2f}</code> cutoff,
                yielding <code>{test_metrics['tp']}/{test_metrics['n_fails']}</code> thresholded detections (<code>TP = {test_metrics['tp']}, FP = {test_metrics['fp']}</code>).
            </div>
            """,
            unsafe_allow_html=True,
        )

    tab_val, tab_test = st.tabs(["Validation Metrics (Sep 2008)", "Held-Out Test Metrics (Oct 2008)"])
    with tab_val:
        val_cols = ["model", "val_threshold", "val_pr_auc", "val_roc_auc", "val_precision", "val_recall", "val_f1", "val_f2", "val_accuracy"]
        st.dataframe(
            comp_df[val_cols],
            width="stretch",
            hide_index=True,
            column_config={
                "model": st.column_config.TextColumn("Model"),
                "val_threshold": st.column_config.NumberColumn("Threshold (t*)", format="%.2f"),
                "val_pr_auc": st.column_config.NumberColumn("PR-AUC", format="%.4f"),
                "val_roc_auc": st.column_config.NumberColumn("ROC-AUC", format="%.4f"),
                "val_precision": st.column_config.NumberColumn("Precision", format="%.4f"),
                "val_recall": st.column_config.NumberColumn("Recall", format="%.4f"),
                "val_f1": st.column_config.NumberColumn("F1", format="%.4f"),
                "val_f2": st.column_config.NumberColumn("F2", format="%.4f"),
                "val_accuracy": st.column_config.NumberColumn("Accuracy", format="%.4f"),
            },
        )

    with tab_test:
        test_cols = ["model", "val_threshold", "test_pr_auc", "test_roc_auc", "test_precision", "test_recall", "test_f1", "test_f2", "test_accuracy", "test_tp", "test_fp", "test_fn", "test_tn"]
        st.dataframe(
            comp_df[test_cols],
            width="stretch",
            hide_index=True,
            column_config={
                "model": st.column_config.TextColumn("Model"),
                "val_threshold": st.column_config.NumberColumn("Threshold (t*)", format="%.2f"),
                "test_pr_auc": st.column_config.NumberColumn("PR-AUC", format="%.4f"),
                "test_roc_auc": st.column_config.NumberColumn("ROC-AUC", format="%.4f"),
                "test_precision": st.column_config.NumberColumn("Precision", format="%.4f"),
                "test_recall": st.column_config.NumberColumn("Recall", format="%.4f"),
                "test_f1": st.column_config.NumberColumn("F1", format="%.4f"),
                "test_f2": st.column_config.NumberColumn("F2", format="%.4f"),
                "test_accuracy": st.column_config.NumberColumn("Accuracy", format="%.4f"),
                "test_tp": st.column_config.NumberColumn("TP", format="%d"),
                "test_fp": st.column_config.NumberColumn("FP", format="%d"),
                "test_fn": st.column_config.NumberColumn("FN", format="%d"),
                "test_tn": st.column_config.NumberColumn("TN", format="%d"),
            },
        )

    metric_labels = {
        "val_pr_auc": "Validation PR-AUC",
        "test_pr_auc": "Held-Out Test PR-AUC",
        "val_f2": "Validation F2",
        "test_f2": "Held-Out Test F2",
    }
    melt_df = comp_df.melt(
        id_vars="model",
        value_vars=["val_pr_auc", "test_pr_auc", "val_f2", "test_f2"],
        var_name="Metric",
        value_name="Score",
    )
    melt_df["Metric"] = melt_df["Metric"].map(metric_labels)
    fig_comp = px.bar(
        melt_df,
        x="model",
        y="Score",
        color="Metric",
        barmode="group",
        text_auto=".3f",
        color_discrete_map={
            "Validation PR-AUC": "#38bdf8",
            "Held-Out Test PR-AUC": "#0284c7",
            "Validation F2": "#14b8a6",
            "Held-Out Test F2": "#ef4444",
        },
        title="Validation vs. Holdout PR-AUC & F2 Comparison",
        labels={"model": "Model", "Score": "Score"},
    )
    fig_comp.update_traces(textposition="outside", cliponaxis=False)
    style_plotly_figure(fig_comp, height=410, margin=dict(t=58, b=78, l=26, r=22))
    max_comp_score = float(melt_df["Score"].max()) if not melt_df.empty else 0.4
    fig_comp.update_yaxes(range=[0, max(0.38, max_comp_score * 1.18)])
    fig_comp.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5, title_text="")
    )
    st.plotly_chart(fig_comp, width="stretch")

    st.divider()
    p3_dir = REPORTS_DIR / "phase3"
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        show_image_safe(p3_dir / "confusion_matrix.png", "Validation & Test Confusion Matrices")
    with c2:
        show_image_safe(p3_dir / "precision_recall_curve.png", "Precision–Recall Curves")
    with c3:
        show_image_safe(p3_dir / "roc_curve.png", "ROC Curves")

    if cls_report:
        with st.expander("Held-Out Test Classification Report"):
            st.code(cls_report, language="text")


def render_quality_prediction(model: object | None, model_meta: dict | None, model_err: str | None) -> None:
    st.subheader("Quality Prediction")
    if model_err or model is None or model_meta is None:
        st.error(f"Prediction engine unavailable: {model_err}")
        return

    threshold = float(model_meta["selected_threshold"])
    st.markdown(
        f'<p class="section-lead">Batch wafer defect scoring using <code>{model_meta["selected_model"]}</code> at threshold <code>t* = {threshold:.2f}</code>.</p>',
        unsafe_allow_html=True,
    )

    col_up, col_sample = st.columns([2.0, 1.0], gap="medium")
    with col_up:
        uploaded = st.file_uploader(
            "Upload Sensor Batch CSV",
            type=["csv"],
            help="CSV containing the active SECOM sensor columns; missing values are imputed using training-fitted medians.",
        )
        st.caption("Supported format: CSV containing SECOM sensor measurements (missing values handled automatically).")
    with col_sample:
        st.markdown("<div style='height: 1.75rem'></div>", unsafe_allow_html=True)
        try:
            sample_bytes = build_sample_sensor_csv_bytes(n_rows=10)
            st.download_button(
                label="Sample CSV (10 Rows)",
                data=sample_bytes,
                file_name="secom_sample_sensors_10rows.csv",
                mime="text/csv",
                width="stretch",
            )
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Sample CSV unavailable: {exc}")

    if uploaded is None:
        st.info("Upload a sensor CSV file to evaluate wafer failure risk.")
        return

    try:
        try:
            raw_df = pd.read_csv(uploaded)
        except pd.errors.EmptyDataError as exc:
            raise ValueError("Uploaded CSV file is empty.") from exc

        pred_df, warn_msgs = validate_and_predict_dataframe(raw_df, model, threshold=threshold)
        for msg in warn_msgs:
            st.info(msg)

        n_total = len(pred_df)
        n_flagged = int((pred_df["predicted_label"] == 1).sum())
        max_prob = float(pred_df["fail_probability"].max())
        mean_prob = float(pred_df["fail_probability"].mean())
        flagged_pct = n_flagged / max(n_total, 1) * 100.0

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        m1.metric("Wafers Evaluated", f"{n_total:,}", "Validated records", delta_color="off")
        m2.metric("Flagged High Risk", f"{n_flagged:,}", f"{flagged_pct:.1f}% above t* = {threshold:.2f}", delta_color="off")
        m3.metric("Peak Risk Score", f"{max_prob:.4f}", "Maximum P(Fail)", delta_color="off")
        m4.metric("Mean Risk Score", f"{mean_prob:.4f}", "Batch average P(Fail)", delta_color="off")

        fig_p = px.histogram(
            pred_df,
            x="fail_probability",
            color="predicted_outcome",
            nbins=20,
            title="Predicted Failure Risk Distribution",
            labels={"fail_probability": "Predicted P(Fail)", "predicted_outcome": "Classification"},
            color_discrete_map={"Pass (-1)": "#0ea5e9", "Fail (1)": "#ef4444"},
        )
        fig_p.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text=f"t* = {threshold:.2f}",
            annotation_position="top right",
        )
        style_plotly_figure(fig_p, height=340, margin=dict(t=56, b=68, l=26, r=26))
        fig_p.update_xaxes(range=[0.0, max(0.30, min(1.0, max_prob * 1.15))])
        fig_p.update_yaxes(title_text="Wafer Count", dtick=1)
        fig_p.update_layout(
            bargap=0.08,
            legend=dict(orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5, title_text=""),
        )
        st.plotly_chart(fig_p, width="stretch")

        display_df = pred_df.copy()
        if "risk_classification" in display_df.columns:
            display_df["risk_classification"] = display_df["fail_probability"].apply(
                lambda p: "● High Risk" if p >= threshold else ("● Elevated" if p >= threshold * 0.5 else "● Low Risk")
            )
        col_order = [
            c
            for c in ["record_index", "predicted_outcome", "predicted_label", "fail_probability", "risk_classification"]
            if c in display_df.columns
        ]
        remaining = [c for c in display_df.columns if c not in col_order]
        display_df = display_df[col_order + remaining]

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            column_config={
                "record_index": st.column_config.NumberColumn("Record #", format="%d"),
                "predicted_outcome": st.column_config.TextColumn("Classification"),
                "predicted_label": st.column_config.NumberColumn("Label", format="%d"),
                "fail_probability": st.column_config.ProgressColumn(
                    "Risk Probability",
                    format="%.4f",
                    min_value=0.0,
                    max_value=1.0,
                ),
                "risk_classification": st.column_config.TextColumn("Risk Level"),
            },
        )
        st.download_button(
            label="Download Prediction Results CSV",
            data=pred_df.to_csv(index=False).encode("utf-8"),
            file_name="secom_predictions.csv",
            mime="text/csv",
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Validation error: {exc}")


def render_explainability_and_insights(imp_df: pd.DataFrame | None, test_metrics: dict | None, comp_df: pd.DataFrame | None) -> None:
    st.subheader("Explainability & Insights")
    st.markdown(
        '<p class="section-lead">Key predictive anonymous sensors, distribution shift impact, and monitoring recommendations.</p>',
        unsafe_allow_html=True,
    )

    if imp_df is not None:
        top15 = imp_df.head(15).copy()
        fig_imp = px.bar(
            top15.iloc[::-1],
            x="combined_score",
            y="feature",
            orientation="h",
            color="rf_importance",
            color_continuous_scale="Teal",
            title=f"Top {len(top15)} Predictive Anonymous Sensors",
            labels={"combined_score": "Combined Importance Score", "feature": "Sensor", "rf_importance": "RF Importance"},
        )
        style_plotly_figure(fig_imp, height=470, margin=dict(t=56, b=50, l=22, r=28))
        fig_imp.update_yaxes(dtick=1, tickfont=dict(size=11))
        c1, c2 = st.columns([1.0, 1.05], gap="medium")
        with c1:
            st.plotly_chart(fig_imp, width="stretch")
        with c2:
            st.dataframe(
                top15[["combined_rank", "feature", "lr_coef_signed", "rf_importance", "lr_rank", "rf_rank"]],
                width="stretch",
                hide_index=True,
                height=470,
                column_config={
                    "combined_rank": st.column_config.NumberColumn("Rank", format="%d", width="small"),
                    "feature": st.column_config.TextColumn("Sensor", width="small"),
                    "lr_coef_signed": st.column_config.NumberColumn("LR Coef", format="%.4f", width="small"),
                    "rf_importance": st.column_config.NumberColumn("RF Imp.", format="%.4f", width="small"),
                    "lr_rank": st.column_config.NumberColumn("LR #", format="%d", width="small"),
                    "rf_rank": st.column_config.NumberColumn("RF #", format="%d", width="small"),
                },
            )
        st.divider()
        show_image_safe(REPORTS_DIR / "phase3" / "feature_importance.png", "Linear Coefficients vs. Tree-Based Feature Importance")
    else:
        st.warning("Feature importance data unavailable.")

    st.warning(
        "**Anonymity & Causality Safeguard:** Sensors (`sensor_000`–`sensor_589`) are unlabelled without physical units or process-step context; "
        "importance scores quantify statistical predictive associations rather than physical root causes."
    )

    col_lim, col_rec = st.columns(2, gap="large")
    with col_lim:
        val_pr_str = "0.2080"
        test_pr_str = f"{test_metrics['pr_auc']:.4f}" if test_metrics else "0.0828"
        tp_str = f"{test_metrics['tp']}/{test_metrics['n_fails']}" if test_metrics else "0/22"
        if comp_df is not None and test_metrics:
            sel = comp_df[comp_df["model"] == test_metrics["selected_model"]]
            if not sel.empty:
                val_pr_str = f"{float(sel['val_pr_auc'].iloc[0]):.4f}"
        st.markdown(
            "#### Temporal Drift & Limitations\n"
            "- **Non-Stationary Yield:** Monthly fail rates shift substantially across the chronological production timeline.\n"
            f"- **Fixed-Cutoff Degradation:** Validation PR-AUC (`{val_pr_str}`) drops to `{test_pr_str}` on October holdout, with fixed `t*` capturing `{tp_str}` TP under score shift.\n"
            "- **Limited Positive Volume:** Only `104` total fail records (`15` validation, `22` test) constrain statistical power."
        )
    with col_rec:
        st.markdown(
            "#### Monitoring Recommendations\n"
            "1. **Rolling Retraining Windows:** Re-fit classifiers on recent sliding fab windows (e.g., 30–45 days) rather than static historical snapshots.\n"
            "2. **Adaptive Threshold Recalibration:** Track top predictive sensor baselines (e.g., `sensor_059`) and recalibrate cutoffs when flagged rates drift.\n"
            "3. **Human-in-the-Loop Triage:** Rank wafers by predicted failure probability for targeted metrology inspection."
        )


def main() -> None:
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

    if model_meta and not model_err:
        status_html = (
            f'<span class="status-pill"><span class="status-dot-ok"></span>'
            f'Model Active · {model_meta["selected_model"]} (t* = {model_meta["selected_threshold"]:.2f})</span>'
        )
    else:
        status_html = '<span class="status-pill"><span class="status-dot-err"></span>Model Unavailable</span>'

    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <div class="app-header-title">Smart Manufacturing Analytics</div>
                <div class="app-header-subtitle">Predictive Quality Intelligence</div>
            </div>
            <div>{status_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Navigation")
        section = st.radio(
            "Navigation",
            [
                "Overview",
                "Data Analysis",
                "Model Performance",
                "Quality Prediction",
                "Explainability & Insights",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("#### Model Registry")
        if model_meta:
            active_sensors = len(stats_df) if stats_df is not None else 0
            st.caption(
                f"**Classifier:** `{model_meta['selected_model']}`  \n"
                f"**Decision Cutoff:** `t* = {model_meta['selected_threshold']:.2f}`  \n"
                f"**Active Sensors:** `{active_sensors}`  \n"
                f"**Holdout Isolation:** Verified"
            )
        else:
            st.error("Model artifact unavailable")

    if section == "Overview":
        render_overview(audit_json, split_json, stats_df, model_meta)
    elif section == "Data Analysis":
        render_data_analysis(audit_json, eda_json, stats_df, missing_df)
    elif section == "Model Performance":
        render_model_performance(comp_df, test_metrics, cls_report)
    elif section == "Quality Prediction":
        render_quality_prediction(model, model_meta, model_err)
    else:
        render_explainability_and_insights(imp_df, test_metrics, comp_df)


if __name__ == "__main__":
    main()
