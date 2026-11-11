# Smart Manufacturing: Intelligent Process Quality Analysis & Predictive Defect Detection
**Final University DSE Project Presentation Slides**

---

## Slide 1 — Title & Project Overview
- **Title:** Smart Manufacturing: Intelligent Process Quality Analysis and Predictive Defect Detection Using Machine Learning
- **Dataset:** UCI SECOM Semiconductor Manufacturing Data (`ID 179`)
- **Repository:** `guhan-star/smart-manufacturing-predictive-quality-analytics`
- **Deliverables:** Reproducible Python Pipeline (`uv`), Chronological ML Models, `19` Automated Tests + CI, Interactive Streamlit Dashboard (`app.py`)

---

## Slide 2 — Problem Statement
- Modern semiconductor fabs monitor hundreds of inline sensors per wafer, but defect prediction faces four real-world barriers:
  1. **Severe Class Imbalance:** Only `6.64%` Fail wafers (`14.07 : 1` Pass:Fail) — accuracy alone is a misleading trap (`93.36%` trivial majority accuracy).
  2. **Pervasive Missingness:** `100%` of wafer records contain missing values (`4.54%` overall).
  3. **Temporal Process Drift:** Defect rates and sensor baselines shift dramatically over 90 days.
  4. **Leakage Risk:** Random splits or full-dataset imputation inflate performance unrealistically.

---

## Slide 3 — Dataset & Research Objectives
- **Source:** Official UCI SECOM (`1,567` records × `590` anonymous sensors `sensor_000`–`sensor_589`, `2008-07-19` to `2008-10-17`).
- **Verified Labels:** `-1 = Pass` (`1,463`, `93.36%`), `1 = Fail` (`104`, `6.64%`).
- **Objectives:**
  1. Strict raw verification (`SHA-256`) and leakage-free data preparation.
  2. Multiple-testing-corrected statistical audit (BH-FDR & observed-only sensitivity).
  3. Timestamp-group-safe chronological evaluation of baselines & ML classifiers.
  4. Interactive Streamlit decision-support dashboard with live CSV validation.

---

## Slide 4 — Data Cleaning & Preprocessing
- **Strict Validation:** Rejects checksum mismatches, invalid labels/timestamps, row misalignments, and `±inf`.
- **Feature Reduction (`590` → `440` active sensors on full dataset; `444` on Train split):**
  - Removed `116` constant (`nunique <= 1`), `6` near-constant (`>=99%` zero; single Pass outlier `row 1458`), and `28` `>50%` missing features.
  - **0 rows removed** (max record missingness `25.76%`; all `104` Fail wafers preserved).
  - **0 outliers removed** (`3.52%` mild, `1.25%` extreme IQR cells kept as potential excursion signals).
- **Leakage Control:** `SecomTrainingPreprocessor` wraps `fit_cleaning_plan()` strictly on training rows (`target_label` & `timestamp` excluded).

---

## Slide 5 — Exploratory Data Analysis
- **Non-Stationary Yield:** Monthly fail rates shift nearly `8×`:
  - `2008-07`: **22.22%** (`14/63`) → `2008-08`: **9.19%** (`51/555`) → `2008-09`: **2.88%** (`17/590`) → `2008-10`: **6.13%** (`22/359`)
- **Heavy Skewness & Collinearity:** `245 / 440` sensors have `|skew| > 2`; `112` sensor pairs have `|r| >= 0.99`.
- **Visual Evidence:** `reports/figures/class_distribution.png`, `missing_values.png`, `correlation_heatmap.png`, `pass_fail_sensor_comparison.png`.

---

## Slide 6 — Statistical Findings (BH-FDR & Sensitivity)
- **440 Mann–Whitney U Tests (Pass vs. Fail):**
  - Raw `p < 0.05`: **`86`** features
  - Benjamini–Hochberg FDR (`q < 0.05`, imputed): **`25`** features
  - Observed-Only BH-FDR (`q < 0.05`, non-imputed): **`20`** features (`5` boundary/imputation shifts, e.g., `sensor_112` shifted from `q = 0.0938` to `0.0493`).
- **Top Statistical Associations (Non-Causal):**
  - `sensor_059` (`r = +0.1560`, `rho = +0.1659`, `p = 5.18e-11`, `3.9×` fail rate above Q75)
  - `sensor_103` (`r = +0.1512`, `p = 9.43e-09`), `sensor_510` (`r = +0.1317`, `p = 3.42e-06`)

---

## Slide 7 — Machine-Learning Methodology
- **Chronological 3-Way Split (32 Repeated-Timestamp Groups Kept Intact):**
  - **Train:** `725` records (`67` fails / `9.24%`, Jul 19 – Sep 04)
  - **Validation:** `483` records (`15` fails / `3.11%`, Sep 04 – Sep 30)
  - **Held-Out Test:** `359` records (`22` fails / `6.13%`, Oct 01 – Oct 17)
- **Models Evaluated:** `Dummy_Majority`, `LogisticRegression` (`StandardScaler`, balanced), `RandomForest` (`balanced_subsample`), `HistGradientBoosting` (`balanced`).
- **Selection Rule:** Selected model and validation threshold `t*` strictly on Validation (`PR-AUC` & `F2`); Test evaluated once.

---

## Slide 8 — Model Comparison (Validation vs. Test)

| Model | Val `t*` | Val PR-AUC | Val Rec | Val Prec | Test PR-AUC | Test ROC-AUC | Test Rec | Test F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Dummy_Majority` | 0.50 | 0.0311 | 0.0000 | 0.0000 | 0.0613 | 0.5000 | 0.0000 | 0.0000 |
| `LogisticRegression` | 0.64 | 0.0333 | 0.4000 | 0.0319 | 0.0775 | 0.5979 | 0.3182 | 0.1284 |
| `RandomForest` | 0.22 | 0.1537 | 0.3333 | 0.1111 | 0.0901 | 0.5943 | 0.1818 | 0.1143 |
| **`HistGradientBoosting`** | **0.19** | **0.2080** | **0.3333** | **0.2381** | **0.0828** | **0.5968** | **0.0000** | **0.0000** |

- `HistGradientBoosting` won on Validation (`6.7×` base rate), yet fixed `t* = 0.19` caught `0 / 22` October failures (`TN=324, FP=13, FN=22, TP=0`) due to October covariate shift.

---

## Slide 9 — Interactive Dashboard Demonstration (`app.py`)
- **Launch:** `uv run streamlit run app.py`
- **5 Sections:**
  1. Project Overview (KPI cards, imbalance donut, chronological splits)
  2. Exploratory Data Analysis (monthly trend, missingness, BH-FDR table, heatmaps)
  3. Predictive Model Comparison (separate Validation/Test tables, PR/ROC/Confusion Matrix)
  4. Interactive Prediction (CSV upload, column/numeric validation, target stripping, live `P(Fail)` + risk bands)
  5. Explainability & Findings (Top 15 anonymous sensors, temporal shift, recommendations)
- **Live 10-Row Demo Result:** `Records Scored = 10`, `Max P(Fail) = 0.1125` (`Moderate Watch`), `Mean = 0.0462`.

---

## Slide 10 — Major Findings
1. **Temporal Covariate Drift Causes Threshold Collapse:** `HistGradientBoosting` maintained above-baseline October ranking (`PR-AUC = 0.0828` vs `0.0613`), but shifted scores fell below `t* = 0.19` (`0` TP).
2. **Baseline Drift in Top Sensor (`sensor_059`):** Top predictor in both LogReg (`+0.4655`) and RF (`0.0303`), yet Pass median drifted from `13.114` (Jul) to `-0.630` (Oct), losing separation.
3. **Imputation & Missingness Regime Confounding:** Logging-schedule shifts alter missingness over time, impacting `5` borderline BH-FDR features.

---

## Slide 11 — Limitations & Future Improvements
- **Limitations:**
  - Small failure sample (`104` total; `15` val; `22` test).
  - Completely anonymous sensors (no physical units or step order; association ≠ causation).
  - Static training degrades over multi-week horizons.
- **Future Improvements:**
  - Rolling-window retraining (30–45 day sliding window).
  - Adaptive threshold recalibration & drift alerts (PSI/KS monitoring).
  - Integration with fab tool/recipe metadata and scrap vs. inspection cost matrices.

---

## Slide 12 — Conclusion
- Built a fully reproducible, CI-tested (`19/19` tests passing) end-to-end SECOM quality analytics system.
- Demonstrated honest chronological validation without hiding test-set drift collapse.
- Ready as a **risk-ranking decision-support prototype** for human-in-the-loop semiconductor metrology triage.
