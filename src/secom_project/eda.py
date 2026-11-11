"""Phase 2 — Statistical analysis, feature rankings, correlation, and visualisations."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from secom_project import DATA_PROCESSED_DIR, DATA_RAW_DIR, REPORTS_DIR
from secom_project.data_validation import load_and_parse_raw_secom

sns.set_theme(style="whitegrid", context="notebook")


def compute_descriptive_statistics(
    cleaned_df: pd.DataFrame,
    raw_sensors_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute overall and Pass/Fail descriptive stats plus missingness, variance, and uniqueness rankings."""
    sensor_cols = [c for c in cleaned_df.columns if c.startswith("sensor_")]
    x_all = cleaned_df[sensor_cols]
    is_fail = (cleaned_df["target_label"] == 1).astype(int)
    x_pass = x_all.loc[is_fail == 0]
    x_fail = x_all.loc[is_fail == 1]

    pearson_target = x_all.corrwith(is_fail, method="pearson")
    spearman_target = x_all.corrwith(is_fail, method="spearman")

    records = []
    for col in sensor_cols:
        s = x_all[col]
        sp = x_pass[col]
        sf = x_fail[col]
        raw_s = raw_sensors_df[col]

        mean_val = float(s.mean())
        std_val = float(s.std(ddof=1))
        var_val = float(s.var(ddof=1))
        min_val = float(s.min())
        max_val = float(s.max())
        q25, q50, q75 = (float(v) for v in s.quantile([0.25, 0.50, 0.75]))

        vc = s.value_counts(dropna=True)
        mode_val = float(vc.index[0]) if len(vc) > 0 else np.nan
        mode_cnt = int(vc.iloc[0]) if len(vc) > 0 else 0
        mode_pct = mode_cnt / len(s) * 100.0

        raw_miss_cnt = int(raw_s.isna().sum())
        raw_miss_pct = raw_miss_cnt / len(raw_s) * 100.0
        n_unique_raw = int(raw_s.nunique(dropna=True))
        n_unique_clean = int(s.nunique(dropna=True))

        cv_val = abs(std_val / mean_val) if abs(mean_val) > 1e-12 else np.nan
        mw_stat, mw_p = stats.mannwhitneyu(sp, sf, alternative="two-sided")

        pass_std = float(sp.std(ddof=1))
        fail_std = float(sf.std(ddof=1))
        std_ratio = (fail_std / pass_std) if pass_std > 1e-12 else np.nan

        records.append(
            {
                "feature": col,
                "count": int(len(s)),
                "raw_missing_count": raw_miss_cnt,
                "raw_missing_pct": round(raw_miss_pct, 4),
                "n_unique_non_null_raw": n_unique_raw,
                "n_unique_cleaned": n_unique_clean,
                "mean": round(mean_val, 6),
                "median": round(q50, 6),
                "mode": round(mode_val, 6),
                "mode_count": mode_cnt,
                "mode_pct": round(mode_pct, 4),
                "std": round(std_val, 6),
                "variance": round(var_val, 6),
                "min": round(min_val, 6),
                "max": round(max_val, 6),
                "range": round(max_val - min_val, 6),
                "q25": round(q25, 6),
                "q50": round(q50, 6),
                "q75": round(q75, 6),
                "iqr": round(q75 - q25, 6),
                "skewness": round(float(s.skew()), 6),
                "kurtosis": round(float(s.kurtosis()), 6),
                "cv_abs": round(float(cv_val), 6) if pd.notna(cv_val) else np.nan,
                "pass_mean": round(float(sp.mean()), 6),
                "pass_median": round(float(sp.median()), 6),
                "pass_std": round(pass_std, 6),
                "pass_iqr": round(float(sp.quantile(0.75) - sp.quantile(0.25)), 6),
                "fail_mean": round(float(sf.mean()), 6),
                "fail_median": round(float(sf.median()), 6),
                "fail_std": round(fail_std, 6),
                "fail_iqr": round(float(sf.quantile(0.75) - sf.quantile(0.25)), 6),
                "fail_to_pass_std_ratio": round(float(std_ratio), 6) if pd.notna(std_ratio) else np.nan,
                "pearson_r_with_fail": round(float(pearson_target[col]), 6),
                "spearman_rho_with_fail": round(float(spearman_target[col]), 6),
                "mannwhitney_u": float(mw_stat),
                "mannwhitney_p": float(mw_p),
            }
        )

    df_stats = pd.DataFrame(records)
    df_stats["missingness_rank"] = df_stats["raw_missing_count"].rank(ascending=False, method="min").astype(int)
    df_stats["variance_rank"] = df_stats["variance"].rank(ascending=False, method="min").astype(int)
    df_stats["unique_values_rank"] = df_stats["n_unique_non_null_raw"].rank(ascending=False, method="min").astype(int)
    return df_stats


def compute_correlation_summary(cleaned_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Compute Pearson and Spearman correlation matrices across cleaned sensors."""
    sensor_cols = [c for c in cleaned_df.columns if c.startswith("sensor_")]
    x_all = cleaned_df[sensor_cols]

    pearson_mat = x_all.corr(method="pearson")
    spearman_mat = x_all.corr(method="spearman")

    upper_mask = np.triu(np.ones(pearson_mat.shape, dtype=bool), k=1)
    p_upper = pearson_mat.where(upper_mask)
    s_upper = spearman_mat.where(upper_mask)

    stacked = p_upper.stack().rename("pearson_r").reset_index()
    stacked.columns = ["feature_a", "feature_b", "pearson_r"]
    stacked["abs_r"] = stacked["pearson_r"].abs()
    top_pairs = stacked.nlargest(25, "abs_r").drop(columns=["abs_r"]).round(6)

    p_abs = p_upper.abs()
    s_abs = s_upper.abs()

    summary = {
        "total_unique_sensor_pairs": int(upper_mask.sum()),
        "pearson_pairs_abs_ge_0_99": int((p_abs >= 0.99).sum().sum()),
        "pearson_pairs_abs_ge_0_95": int((p_abs >= 0.95).sum().sum()),
        "pearson_pairs_abs_ge_0_90": int((p_abs >= 0.90).sum().sum()),
        "pearson_pairs_abs_ge_0_80": int((p_abs >= 0.80).sum().sum()),
        "spearman_pairs_abs_ge_0_90": int((s_abs >= 0.90).sum().sum()),
        "spearman_pairs_abs_ge_0_80": int((s_abs >= 0.80).sum().sum()),
        "top_correlated_pairs": top_pairs.to_dict(orient="records"),
    }
    return pearson_mat, spearman_mat, summary


def generate_visualisations(
    cleaned_df: pd.DataFrame,
    missing_report_df: pd.DataFrame,
    raw_row_missing_pct: pd.Series,
    stats_df: pd.DataFrame,
    pearson_mat: pd.DataFrame,
    figures_dir: Path,
) -> list[Path]:
    """Generate and save all 8 Phase 2 visualisations with `sensor_XXX` naming."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    work_df = cleaned_df.copy()
    work_df["class_name"] = work_df["target_label"].map({-1: "Pass (-1)", 1: "Fail (1)"})
    work_df["year_month"] = pd.to_datetime(work_df["timestamp"]).dt.to_period("M").astype(str)

    # 1. class_distribution.png
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    counts = work_df["class_name"].value_counts().reindex(["Pass (-1)", "Fail (1)"])
    bars = axes[0].bar(counts.index, counts.values, color=["#2b7bba", "#d64541"], edgecolor="black", linewidth=0.6)
    for bar, cnt in zip(bars, counts.values):
        pct = cnt / len(work_df) * 100.0
        axes[0].text(bar.get_x() + bar.get_width() / 2, cnt + 25, f"{cnt:,}\n({pct:.2f}%)", ha="center", va="bottom", fontweight="bold")
    axes[0].set_title("Overall Pass vs. Fail Class Distribution (n = 1,567)")
    axes[0].set_xlabel("In-House Line Test Outcome")
    axes[0].set_ylabel("Number of Wafer Records")
    axes[0].set_ylim(0, max(counts.values) * 1.18)

    monthly = (
        work_df.groupby("year_month")
        .agg(total=("target_label", "size"), fails=("target_label", lambda s: int((s == 1).sum())))
        .reset_index()
    )
    monthly["fail_pct"] = monthly["fails"] / monthly["total"] * 100.0
    axes[1].plot(monthly["year_month"], monthly["fail_pct"], marker="o", linewidth=2.4, color="#d64541", label="Monthly Fail Rate (%)")
    for _, row in monthly.iterrows():
        axes[1].annotate(f"{row['fail_pct']:.2f}%\n({int(row['fails'])}/{int(row['total'])})", (row["year_month"], row["fail_pct"]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    axes[1].set_title("Monthly Defect (Fail) Rate Over Time (Jul–Oct 2008)")
    axes[1].set_xlabel("Production Test Month")
    axes[1].set_ylabel("Fail Rate (%)")
    axes[1].set_ylim(0, monthly["fail_pct"].max() * 1.28)
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    p1 = figures_dir / "class_distribution.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    saved_paths.append(p1)

    # 2. missing_values.png
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5), gridspec_kw={"width_ratios": [1.5, 1.0]})
    top30 = missing_report_df.sort_values("missing_pct", ascending=False).head(30).iloc[::-1]
    bar_colors = ["#d64541" if pct > 50.0 else "#f39c12" for pct in top30["missing_pct"]]
    axes[0].barh(top30["feature"], top30["missing_pct"], color=bar_colors, edgecolor="black", linewidth=0.4)
    axes[0].axvline(50.0, color="#222222", linestyle="--", linewidth=1.3, label="50% Removal Cutoff")
    axes[0].set_title("Top 30 Sensor Features by Missingness (%)")
    axes[0].set_xlabel("Missing Values (%)")
    axes[0].set_ylabel("Anonymous Sensor Feature")
    axes[0].set_xlim(0, 100)
    axes[0].tick_params(axis="y", labelsize=8)
    axes[0].legend(loc="lower right")

    tier_order = ["Complete (0%)", "Low (0%-5%]", "Moderate (5%-50%]", "Extreme (>50%)"]
    tier_counts = missing_report_df["missingness_tier"].value_counts().reindex(tier_order, fill_value=0)
    bars2 = axes[1].bar(range(len(tier_order)), tier_counts.values, color=["#2ecc71", "#2b7bba", "#f39c12", "#d64541"], edgecolor="black", linewidth=0.6)
    axes[1].set_xticks(range(len(tier_order)))
    axes[1].set_xticklabels(["0%\n(Complete)", "0%–5%\n(Low)", "5%–50%\n(Moderate)", ">50%\n(Extreme)"])
    for b, v in zip(bars2, tier_counts.values):
        axes[1].text(b.get_x() + b.get_width() / 2, v + 8, f"{v}", ha="center", va="bottom", fontweight="bold")
    axes[1].set_title("Raw Sensor Features by Missingness Tier (590 Total)")
    axes[1].set_xlabel("Missingness Tier")
    axes[1].set_ylabel("Number of Sensor Features")
    axes[1].set_ylim(0, max(tier_counts.values) * 1.15)
    fig.tight_layout()
    p2 = figures_dir / "missing_values.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    saved_paths.append(p2)

    # 3. missing_percentage.png
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    axes[0].hist(missing_report_df["missing_pct"], bins=30, color="#2b7bba", edgecolor="black", alpha=0.85)
    axes[0].axvline(50.0, color="#d64541", linestyle="--", linewidth=1.6, label="50% Cutoff (28 features >50%)")
    axes[0].set_title("Distribution of Feature-Level Missing Percentage (590 Sensors)")
    axes[0].set_xlabel("Missing Percentage per Feature (%)")
    axes[0].set_ylabel("Number of Features")
    axes[0].legend(loc="upper right")

    axes[1].hist(raw_row_missing_pct, bins=25, color="#16a085", edgecolor="black", alpha=0.85)
    axes[1].axvline(raw_row_missing_pct.median(), color="#222222", linestyle="-", linewidth=1.5, label=f"Median: {raw_row_missing_pct.median():.2f}%")
    axes[1].axvline(raw_row_missing_pct.max(), color="#d64541", linestyle="--", linewidth=1.5, label=f"Max: {raw_row_missing_pct.max():.2f}%")
    axes[1].set_title("Distribution of Record-Level Missing Percentage (1,567 Wafers)")
    axes[1].set_xlabel("Missing Percentage per Record (%)")
    axes[1].set_ylabel("Number of Records")
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    p3 = figures_dir / "missing_percentage.png"
    fig.savefig(p3, dpi=150)
    plt.close(fig)
    saved_paths.append(p3)

    # 4. sensor_distributions.png
    dist_sensors = ["sensor_028", "sensor_103", "sensor_059", "sensor_510", "sensor_021", "sensor_431"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, col in zip(axes.ravel(), dist_sensors):
        vals = work_df[col]
        skew_v = float(vals.skew())
        med_v = float(vals.median())
        mean_v = float(vals.mean())
        ax.hist(vals, bins=35, color="#3b7eb9", edgecolor="white", alpha=0.85)
        ax.axvline(med_v, color="#e67e22", linestyle="-", linewidth=1.6, label=f"Median: {med_v:.3g}")
        ax.axvline(mean_v, color="#d64541", linestyle="--", linewidth=1.6, label=f"Mean: {mean_v:.3g}")
        ax.set_title(f"{col} (skew = {skew_v:.2f})")
        ax.set_xlabel("Measured Sensor Value")
        ax.set_ylabel("Record Count")
        ax.legend(fontsize=8, loc="best")
    fig.suptitle("Representative Cleaned Sensor Distributions (Symmetric vs. Heavy-Tailed)", fontsize=13, y=1.01)
    fig.tight_layout()
    p4 = figures_dir / "sensor_distributions.png"
    fig.savefig(p4, dpi=150, bbox_inches="tight")
    plt.close(fig)
    saved_paths.append(p4)

    # 5. pass_fail_boxplots.png
    top6_sensors = stats_df.reindex(stats_df["spearman_rho_with_fail"].abs().nlargest(6).index)["feature"].tolist()
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, col in zip(axes.ravel(), top6_sensors):
        sns.boxplot(
            data=work_df,
            x="class_name",
            y=col,
            hue="class_name",
            order=["Pass (-1)", "Fail (1)"],
            palette={"Pass (-1)": "#2b7bba", "Fail (1)": "#d64541"},
            legend=False,
            showfliers=True,
            flierprops={"marker": "o", "markersize": 3, "alpha": 0.45},
            ax=ax,
        )
        row_stat = stats_df.loc[stats_df["feature"] == col].iloc[0]
        ax.set_title(f"{col}\n(rho={row_stat['spearman_rho_with_fail']:+.3f}, MW p={row_stat['mannwhitney_p']:.1e})")
        ax.set_xlabel("Test Outcome")
        ax.set_ylabel("Sensor Reading")
    fig.suptitle("Pass vs. Fail Boxplots for Top 6 Candidate Sensors (by |Spearman rho|)", fontsize=13, y=1.01)
    fig.tight_layout()
    p5 = figures_dir / "pass_fail_boxplots.png"
    fig.savefig(p5, dpi=150, bbox_inches="tight")
    plt.close(fig)
    saved_paths.append(p5)

    # 6. correlation_heatmap.png
    top20_features = stats_df.reindex(stats_df["pearson_r_with_fail"].abs().nlargest(20).index)["feature"].tolist()
    sub_corr = pearson_mat.loc[top20_features, top20_features]
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        sub_corr,
        cmap="coolwarm",
        center=0.0,
        vmin=-1.0,
        vmax=1.0,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 7},
        square=True,
        cbar_kws={"label": "Pearson Correlation (r)"},
        ax=ax,
    )
    ax.set_title("Pearson Correlation Heatmap — Top 20 Target-Associated Cleaned Sensors")
    ax.set_xlabel("Sensor Feature")
    ax.set_ylabel("Sensor Feature")
    fig.tight_layout()
    p6 = figures_dir / "correlation_heatmap.png"
    fig.savefig(p6, dpi=150)
    plt.close(fig)
    saved_paths.append(p6)

    # 7. feature_variability.png
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))
    valid_cv = stats_df["cv_abs"].dropna()
    valid_cv_pos = valid_cv[valid_cv > 0]
    axes[0].hist(np.log10(valid_cv_pos), bins=35, color="#8e44ad", edgecolor="white", alpha=0.85)
    axes[0].axvline(0.0, color="#d64541", linestyle="--", linewidth=1.5, label="CV = 1.0 (std == |mean|)")
    axes[0].set_title("Distribution of Log10 Coefficient of Variation Across 440 Cleaned Sensors")
    axes[0].set_xlabel("log10(|std / mean|)")
    axes[0].set_ylabel("Number of Sensors")
    axes[0].legend(loc="upper left")

    top_disp = (
        stats_df.dropna(subset=["fail_to_pass_std_ratio"])
        .sort_values("fail_to_pass_std_ratio", ascending=False)
        .head(15)
        .iloc[::-1]
    )
    axes[1].barh(top_disp["feature"], top_disp["fail_to_pass_std_ratio"], color="#e67e22", edgecolor="black", linewidth=0.4)
    axes[1].axvline(1.0, color="#222222", linestyle="--", linewidth=1.2, label="Equal Std (Ratio = 1.0)")
    axes[1].set_title("Top 15 Sensors by Fail-to-Pass Standard Deviation Ratio")
    axes[1].set_xlabel("Fail Std / Pass Std")
    axes[1].set_ylabel("Sensor Feature")
    axes[1].legend(loc="lower right")
    fig.tight_layout()
    p7 = figures_dir / "feature_variability.png"
    fig.savefig(p7, dpi=150)
    plt.close(fig)
    saved_paths.append(p7)

    # 8. pass_fail_sensor_comparison.png
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))
    cand_cols = ["sensor_059", "sensor_103", "sensor_510", "sensor_033", "sensor_021"]
    x_idx = np.arange(len(cand_cols))
    width = 0.26
    rates_le75, rates_gt75, rates_gt90 = [], [], []
    y_fail = (work_df["target_label"] == 1).astype(int)
    for col in cand_cols:
        q75 = work_df[col].quantile(0.75)
        q90 = work_df[col].quantile(0.90)
        rates_le75.append(float(y_fail[work_df[col] <= q75].mean() * 100.0))
        rates_gt75.append(float(y_fail[work_df[col] > q75].mean() * 100.0))
        rates_gt90.append(float(y_fail[work_df[col] > q90].mean() * 100.0))

    b1 = axes[0].bar(x_idx - width, rates_le75, width, label="<= Q75", color="#2b7bba", edgecolor="black", linewidth=0.5)
    b2 = axes[0].bar(x_idx, rates_gt75, width, label="> Q75 (Top 25%)", color="#f39c12", edgecolor="black", linewidth=0.5)
    b3 = axes[0].bar(x_idx + width, rates_gt90, width, label="> Q90 (Top 10%)", color="#d64541", edgecolor="black", linewidth=0.5)
    for bars_grp in (b1, b2, b3):
        for b in bars_grp:
            h = b.get_height()
            axes[0].text(b.get_x() + b.get_width() / 2, h + 0.3, f"{h:.1f}%", ha="center", va="bottom", fontsize=7.5)
    axes[0].axhline(y_fail.mean() * 100.0, color="#222222", linestyle="--", linewidth=1.2, label=f"Baseline ({y_fail.mean()*100:.2f}%)")
    axes[0].set_xticks(x_idx)
    axes[0].set_xticklabels(cand_cols)
    axes[0].set_title("Defect Rate Escalation Across Upper Sensor Quantiles")
    axes[0].set_xlabel("Candidate Sensor Feature")
    axes[0].set_ylabel("Observed Fail Rate (%)")
    axes[0].set_ylim(0, max(rates_gt90) * 1.25)
    axes[0].legend(loc="upper right", fontsize=8.5)

    s59_monthly = (
        work_df.groupby(["year_month", "class_name"])["sensor_059"]
        .median()
        .unstack("class_name")
        .reindex(sorted(work_df["year_month"].unique()))
    )
    axes[1].plot(s59_monthly.index, s59_monthly["Pass (-1)"], marker="o", linewidth=2.2, color="#2b7bba", label="Pass (-1) Median")
    axes[1].plot(s59_monthly.index, s59_monthly["Fail (1)"], marker="s", linewidth=2.2, color="#d64541", label="Fail (1) Median")
    for ym in s59_monthly.index:
        axes[1].annotate(f"{s59_monthly.loc[ym, 'Pass (-1)']:.2f}", (ym, s59_monthly.loc[ym, "Pass (-1)"]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8.5, color="#1f5a8a")
        axes[1].annotate(f"{s59_monthly.loc[ym, 'Fail (1)']:.2f}", (ym, s59_monthly.loc[ym, "Fail (1)"]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5, color="#a82c29")
    axes[1].axhline(0.0, color="gray", linestyle=":", linewidth=1.0)
    axes[1].set_title("Temporal Drift & Separation Collapse in Top Sensor (sensor_059)")
    axes[1].set_xlabel("Production Test Month")
    axes[1].set_ylabel("Monthly Median of sensor_059")
    axes[1].set_ylim(min(s59_monthly.min()) - 4, max(s59_monthly.max()) + 4)
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    p8 = figures_dir / "pass_fail_sensor_comparison.png"
    fig.savefig(p8, dpi=150)
    plt.close(fig)
    saved_paths.append(p8)

    return saved_paths


def write_statistical_analysis_report(
    cleaned_df: pd.DataFrame,
    missing_report_df: pd.DataFrame,
    stats_df: pd.DataFrame,
    corr_summary: dict,
    monthly_miss_summary: list[dict],
    out_path: Path = REPORTS_DIR / "phase2_statistical_analysis.md",
) -> None:
    """Write `reports/phase2_statistical_analysis.md` with rankings, stats, and chart interpretations."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_rows = len(cleaned_df)
    n_pass = int((cleaned_df["target_label"] == -1).sum())
    n_fail = int((cleaned_df["target_label"] == 1).sum())
    n_sensors = len(stats_df)

    # Rankings tables
    top_missing = missing_report_df.sort_values(["missing_count", "feature"], ascending=[False, True]).head(15)
    miss_rank_rows = "\n".join(
        f"| {r['missingness_rank']} | `{r['feature']}` | {r['missing_count']} | {r['missing_pct']:.2f}% | {r['cleaning_action']} |"
        for _, r in top_missing.iterrows()
    )

    top_var = stats_df.sort_values("variance", ascending=False).head(15)
    var_rank_rows = "\n".join(
        f"| {r['variance_rank']} | `{r['feature']}` | {r['variance']:.4g} | {r['std']:.4g} | {r['range']:.4g} | {r['skewness']:.2f} |"
        for _, r in top_var.iterrows()
    )

    top_uniq = stats_df.sort_values("n_unique_non_null_raw", ascending=False).head(10)
    low_uniq = stats_df.sort_values("n_unique_non_null_raw", ascending=True).head(10)
    uniq_top_rows = "\n".join(
        f"| {r['unique_values_rank']} | `{r['feature']}` | {r['n_unique_non_null_raw']} | {r['mode']:.4g} ({r['mode_count']}x) |"
        for _, r in top_uniq.iterrows()
    )
    uniq_low_rows = "\n".join(
        f"| {r['unique_values_rank']} | `{r['feature']}` | {r['n_unique_non_null_raw']} | {r['mode']:.4g} ({r['mode_count']}x, {r['mode_pct']:.1f}%) |"
        for _, r in low_uniq.iterrows()
    )

    top10_cand = stats_df.reindex(stats_df["pearson_r_with_fail"].abs().nlargest(10).index)
    cand_rows = "\n".join(
        f"| `{r['feature']}` | {r['pearson_r_with_fail']:+.4f} | {r['spearman_rho_with_fail']:+.4f} | "
        f"{r['mannwhitney_p']:.2e} | {r['pass_median']:.4f} | {r['fail_median']:.4f} | "
        f"{r['pass_iqr']:.4f} | {r['fail_iqr']:.4f} |"
        for _, r in top10_cand.iterrows()
    )

    top10_pairs = "\n".join(
        f"| `{p['feature_a']}` | `{p['feature_b']}` | {p['pearson_r']:+.6f} |"
        for p in corr_summary["top_correlated_pairs"][:10]
    )

    work = cleaned_df.copy()
    work["ym"] = pd.to_datetime(work["timestamp"]).dt.to_period("M").astype(str)
    s59_m = work.groupby(["ym", "target_label"])["sensor_059"].median().unstack("target_label")
    s103_m = work.groupby(["ym", "target_label"])["sensor_103"].median().unstack("target_label")
    monthly_lookup = {r["year_month"]: r for r in monthly_miss_summary}
    drift_rows = "\n".join(
        f"| {ym} | {monthly_lookup[ym]['records']} | {monthly_lookup[ym]['fail_rate_pct']:.2f}% | "
        f"{s59_m.loc[ym, -1]:.3f} | {s59_m.loc[ym, 1]:.3f} | "
        f"{s103_m.loc[ym, -1]:.4f} | {s103_m.loc[ym, 1]:.4f} |"
        for ym in sorted(work["ym"].unique())
    )

    skew_gt2 = int((stats_df["skewness"].abs() > 2).sum())
    skew_gt10 = int((stats_df["skewness"].abs() > 10).sum())

    content = f"""# Phase 2 Statistical Analysis & EDA Report — UCI SECOM

## 1. Overview & Descriptive Statistics (`reports/phase2_statistical_summary.csv`)
- **Dataset Scope:** `{n_rows}` records (`{n_pass}` Pass `-1` / `{n_pass/n_rows*100:.2f}%`, `{n_fail}` Fail `1` / `{n_fail/n_rows*100:.2f}%`, **`14.07 : 1` class imbalance**) across `{n_sensors}` cleaned anonymous sensor features (`sensor_000`–`sensor_589` subset).
- **Metrics Computed for All 440 Cleaned Sensors:** `mean`, `median`, `mode` (with mode frequency & share), `std`, `variance`, `min`, `max`, `range`, `q25`, `q50`, `q75`, `iqr`, `skewness`, `kurtosis`, `raw_missing_count`, `raw_missing_pct`, and `n_unique_non_null_raw`.
- **Distribution Shape:** `{skew_gt2}` / `{n_sensors}` sensors (`{skew_gt2/n_sensors*100:.1f}%`) exhibit `|skewness| > 2` and `{skew_gt10}` (`{skew_gt10/n_sensors*100:.1f}%`) exceed `|skewness| > 10`. Because continuous floating-point readings rarely repeat identically unless quantized or median-imputed, mode is mainly informative on discrete/low-cardinality signals.

---

## 2. Feature Rankings (Missingness, Variance, Unique Values)

### 2A. Missingness Ranking (Top 15 of 590 Raw Features)
| Rank | Feature | Missing Count | Missing % | Phase 2 Action |
|---:|---|---:|---:|---|
{miss_rank_rows}

### 2B. Variance Ranking (Top 15 of 440 Cleaned Features)
*Note: Variance is scale-dependent (units are undisclosed in UCI SECOM); high raw variance reflects both physical signal scale and extreme tail excursions.*

| Rank | Feature | Variance | Std Dev | Range | Skewness |
|---:|---|---:|---:|---:|---:|
{var_rank_rows}

### 2C. Unique-Value Count Ranking (`n_unique_non_null_raw`)
**Highest Cardinality (Top 10 Continuous Signals):**

| Rank | Feature | Unique Values | Mode (Freq) |
|---:|---|---:|---|
{uniq_top_rows}

**Lowest Cardinality Among Retained Active Sensors (Bottom 10 Quantized / Discrete Signals):**

| Rank | Feature | Unique Values | Mode (Freq, %) |
|---:|---|---:|---|
{uniq_low_rows}

---

## 3. Pass vs. Fail Distribution Comparison & Methodology

Because `{skew_gt2}` sensors are strongly skewed and class sizes are unbalanced (`1,463` vs `104`), **non-parametric Mann-Whitney U tests** and **Spearman rank correlation (`rho`)** are preferred alongside **Pearson `r`** and median/IQR comparisons (parametric normality assumptions of Student's t-test are violated for most sensors).

| Feature | Pearson `r` | Spearman `rho` | Mann-Whitney `p` | Pass Median | Fail Median | Pass IQR | Fail IQR |
|---|---:|---:|---:|---:|---:|---:|---:|
{cand_rows}

### Statistical Limitations & Assumptions
1. **Association ≠ Causation:** Statistical separation (`p < 0.001`) indicates correlation with test outcomes, not physical root cause; sensor definitions and upstream/downstream process order are undocumented.
2. **Class Imbalance Compression:** At `6.64%` Fail prevalence, linear Pearson point-biserial `r` is compressed (max `|r| = 0.1560`), even when tail failure rates multiply (`3.9×` above Q75 in `sensor_059`).
3. **Multiple Comparisons:** Screening `440` features requires adjusting significance thresholds (e.g., Bonferroni `p < 1.14e-4` or FDR) and confirming stability across chronological folds in Phase 3.
4. **Imputation Effect:** Unsupervised median imputation preserves row count without target leakage, but compresses variance/IQR on moderately missing features (`sensor_247`, `sensor_519` at `45.63%` missing).

---

## 4. Sensor-to-Sensor Correlation & Collinearity
- **Unique Sensor Pairs Evaluated:** `{corr_summary['total_unique_sensor_pairs']:,}`
- **Pairs with `|Pearson r| >= 0.99`:** `{corr_summary['pearson_pairs_abs_ge_0_99']}` (`>= 0.95`: `{corr_summary['pearson_pairs_abs_ge_0_95']}`, `>= 0.90`: `{corr_summary['pearson_pairs_abs_ge_0_90']}`, `>= 0.80`: `{corr_summary['pearson_pairs_abs_ge_0_80']}`)
- **Pairs with `|Spearman rho| >= 0.90`:** `{corr_summary['spearman_pairs_abs_ge_0_90']}`

| Feature A | Feature B | Pearson `r` |
|---|---|---:|
{top10_pairs}

---

## 5. Key Temporal Process-Drift Discovery

| Month | Wafers | Fail Rate | `sensor_059` Pass Med | `sensor_059` Fail Med | `sensor_103` Pass Med | `sensor_103` Fail Med |
|---|---:|---:|---:|---:|---:|---:|
{drift_rows}

Across the 90-day timeline, monthly fail rates swing from `22.22%` (Jul) down to `2.88%` (Sep) and back to `6.13%` (Oct). Meanwhile, the strongest global candidate (`sensor_059`) drifts steadily downward (`13.114` → `-0.630`) and loses Pass/Fail median separation in October (`-0.630` vs `-0.730`), highlighting strong process non-stationarity.

---

## 6. Visualisations & Interpretations

### 1. Pass vs. Fail Class Distribution
![Pass vs Fail Class Distribution](figures/class_distribution.png)

**Interpretation:** The dataset exhibits a `14.07 : 1` imbalance (`1,463` Pass `93.36%` vs. `104` Fail `6.64%`), while monthly defect rates fluctuate sharply from `22.22%` in July 2008 to `2.88%` in September 2008 before rising to `6.13%` in October 2008. Accuracy alone is therefore uninformative, and evaluation must respect temporal non-stationarity.

### 2. Missingness Across Sensor Features
![Missing Values by Feature](figures/missing_values.png)

**Interpretation:** Sensor missingness clusters into discrete operational blocks; `28` sensors exceed the `50%` cutoff (`50.67%`–`91.19%` missing) and are separated by a clear gap from the `4` moderate-missingness sensors at `45.63%`, justifying the `>50%` feature-removal boundary.

### 3. Feature & Record Missing-Percentage Distributions
![Missing Percentage Distribution](figures/missing_percentage.png)

**Interpretation:** Most raw features (`538 / 590`) have `<= 5%` missing values, whereas every single wafer record (`1,567 / 1,567`) contains between `0.68%` and `25.76%` missing sensor values (median `4.07%`). Dropping incomplete records is therefore infeasible and unsupervised imputation is required.

### 4. Selected Sensor Distributions
![Selected Sensor Distributions](figures/sensor_distributions.png)

**Interpretation:** Cleaned sensors span from near-symmetric (`sensor_028`, `skew = -0.06`) and mildly skewed (`sensor_103`, `skew = 0.83`) distributions to heavily right-skewed, tail-dominated signals (`sensor_059` `skew = 4.73`, `sensor_510` `skew = 4.11`, `sensor_431` `skew = 7.10`), motivating non-parametric tests and median imputation.

### 5. Pass vs. Fail Boxplot Comparison
![Pass vs Fail Boxplots](figures/pass_fail_boxplots.png)

**Interpretation:** Top Spearman-ranked sensors (`sensor_059`, `sensor_103`, `sensor_510`) show upward-shifted medians and wider upper tails in Fail wafers compared to Pass wafers. On `sensor_247` and `sensor_519` (`45.63%` missing), the Pass box collapses near the imputed median because Pass records had higher missingness (`46.62%` vs `31.73%`), illustrating why missingness regime differences require caution.

### 6. Correlation Heatmap (Top 20 Candidate Sensors)
![Correlation Heatmap](figures/correlation_heatmap.png)

**Interpretation:** Strong collinear blocks appear among target-associated features (e.g., `sensor_430`/`sensor_431`/`sensor_434`/`sensor_435`/`sensor_436` with `r >= 0.90`, `sensor_160`/`sensor_295` at `r = 1.00`, and `sensor_163`/`sensor_298` at `r = 0.99`), confirming substantial redundancy across anonymous monitoring channels.

### 7. Feature Variability Comparison
![Feature Variability](figures/feature_variability.png)

**Interpretation:** Relative dispersion varies by orders of magnitude across the `440` sensors (`122` with `|std / mean| > 1.0`), and several sensors exhibit more than double the standard deviation in Fail wafers compared to Pass wafers, suggesting variance/excursion sensitivity rather than pure mean shifts.

### 8. Pass-versus-Fail Quantile Escalation & Temporal Drift
![Pass vs Fail Sensor Comparison](figures/pass_fail_sensor_comparison.png)

**Interpretation:** Defect rates escalate markedly in the upper quantiles of top candidate sensors (e.g., `sensor_059` rises from `3.8%` below Q75 to `15.1%` above Q75 and `16.6%` above Q90), yet the right panel shows `sensor_059` drifting downward over time and losing separation in October 2008—demonstrating why static thresholds alone are insufficient.
"""
    out_path.write_text(content, encoding="utf-8")


def run_eda(
    cleaned_csv: Path = DATA_PROCESSED_DIR / "secom_cleaned.csv",
    missing_csv: Path = REPORTS_DIR / "phase2_missing_value_report.csv",
    cleaning_summary_json: Path = DATA_PROCESSED_DIR / "secom_cleaning_summary.json",
    reports_dir: Path = REPORTS_DIR,
) -> dict:
    """Execute statistical analysis, rankings, correlation analysis, and visualisations."""
    cleaned_df = pd.read_csv(cleaned_csv)
    missing_report_df = pd.read_csv(missing_csv)
    cleaning_summary = json.loads(cleaning_summary_json.read_text(encoding="utf-8"))
    raw_sensors_df, _ = load_and_parse_raw_secom(DATA_RAW_DIR)
    raw_row_missing_pct = raw_sensors_df.isna().mean(axis=1) * 100.0

    stats_df = compute_descriptive_statistics(cleaned_df, raw_sensors_df)
    stats_csv = reports_dir / "phase2_statistical_summary.csv"
    stats_df.to_csv(stats_csv, index=False)

    pearson_mat, spearman_mat, corr_summary = compute_correlation_summary(cleaned_df)
    figures = generate_visualisations(
        cleaned_df=cleaned_df,
        missing_report_df=missing_report_df,
        raw_row_missing_pct=raw_row_missing_pct,
        stats_df=stats_df,
        pearson_mat=pearson_mat,
        figures_dir=reports_dir / "figures",
    )

    report_md = reports_dir / "phase2_statistical_analysis.md"
    write_statistical_analysis_report(
        cleaned_df=cleaned_df,
        missing_report_df=missing_report_df,
        stats_df=stats_df,
        corr_summary=corr_summary,
        monthly_miss_summary=cleaning_summary["monthly_missingness_vs_yield"],
        out_path=report_md,
    )

    eda_summary = {
        "statistical_summary_csv": str(stats_csv),
        "statistical_analysis_md": str(report_md),
        "figures_generated": [str(p) for p in figures],
        "skew_gt_2_count": int((stats_df["skewness"].abs() > 2).sum()),
        "skew_gt_10_count": int((stats_df["skewness"].abs() > 10).sum()),
        "cv_gt_1_count": int((stats_df["cv_abs"] > 1.0).sum()),
        "correlation_summary": corr_summary,
    }
    (reports_dir / "phase2_eda_summary.json").write_text(
        json.dumps(eda_summary, indent=2), encoding="utf-8"
    )
    return eda_summary


def main() -> None:
    summary = run_eda()
    print(json.dumps({k: v for k, v in summary.items() if k != "correlation_summary"}, indent=2))
    print("Correlation pairs |r|>=0.99:", summary["correlation_summary"]["pearson_pairs_abs_ge_0_99"])


if __name__ == "__main__":
    main()
