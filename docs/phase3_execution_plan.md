# Phase 3 Execution Plan — Predictive Defect Detection & Model Evaluation (UCI SECOM)

**Repository:** `guhan-star/smart-manufacturing-predictive-quality-analytics`  
**Status:** **PREPARED EXECUTION PLAN ONLY — NOT YET EXECUTED**  
**Prerequisite Gate (Phase 2 Status):**
1. Phase 2 review fixes complete: Verified (`data_validation.py`, `data_cleaning.py`, `eda.py`, reports, and notebook aligned on `load_raw_secom()` and `sensor_000`–`sensor_589`).
2. Full Phase 2 pipeline executed: Verified (`data_cleaning.py`, `eda.py`, and `notebooks/02_data_preparation_and_eda.ipynb`).
3. Phase 2 tests passing: Verified (`5 passed` in `tests/test_data_cleaning.py`).
4. Phase 2 committed & pushed to `main`: Verified (`79bdc44` on `main` / `origin/main`).
5. **Project owner explicit approval to start Phase 3:** **PENDING** *(Do not run modeling code or build dashboards until approved.)*

---

## 1. Objective & Problem Formulation
- **Research Question:** *Can manufacturing sensor measurements predict product quality failures, and which anonymous sensor features are most strongly associated with failure predictions?*
- **Task:** Binary classification on `target_label` (`-1` = Pass, `1` = Fail; mapped internally to `0 = Pass`, `1 = Fail` for scikit-learn metrics while preserving `-1` / `1` semantics in outputs).
- **Dataset Baseline Facts (from Phase 1 & Phase 2):**
  - `1,567` records (`1,463` Pass / `93.36%`, `104` Fail / `6.64%`, `14.07 : 1` imbalance).
  - `590` anonymous raw sensors (`sensor_000`–`sensor_589`); `440` active sensors retained under Phase 2 unsupervised cleaning (`116` constant, `6` near-constant, `28` `>50%` missing removed; `0` rows dropped).
  - Chronological span: `2008-07-19 11:55:00` to `2008-10-17 06:07:00` (`89.76` days), monotonically non-decreasing in raw row order, with `32` repeated-timestamp groups (`65` rows, `3` groups with mixed labels).
- **Strict Interpretation Guardrails:**
  - Never invent physical meanings or engineering units for anonymous sensors.
  - Never equate predictive importance or correlation with causal root cause.
  - Prioritize reliable failure detection (PR-AUC, Fail recall, Fail F1, MCC, balanced accuracy) over raw accuracy.

---

## 2. Data Preparation & Leakage-Free Pipeline Architecture
Reuse Phase 2 modules (`load_raw_secom()`, `load_and_parse_raw_secom()`, `fit_cleaning_plan()`, `apply_cleaning_plan()`) without modifying `data/raw/`.

### Planned Preprocessing Experiments (Fit Strictly on Training Folds Only)
All transformations will be wrapped inside `sklearn.pipeline.Pipeline` (and custom scikit-learn-compatible transformers where needed) so validation/test data are never inspected during fitting:
1. **Experiment A — Phase 2 Rules Refit Per Training Fold:** Inside each training fold, drop constant (`nunique <= 1`), near-constant (`>= 99%` dominant), and `>50%` missing features, then apply unsupervised median imputation + model-appropriate scaling (`StandardScaler` / `RobustScaler` for linear and SVM models).
2. **Experiment B — Training-Only Adaptive Pipeline:** Training-fold variance threshold (`VarianceThreshold`), missingness cutoff (`>50%`), median imputation (comparing optional missingness-indicator flags vs. no indicators to quantify whether non-MCAR logging regimes act as regime proxies), and robust scaling.
3. **Experiment C — Controlled Retention of Near-Constant Features:** Controlled comparison retaining the `6` near-constant features (`sensor_074`, `sensor_206`, `sensor_209`, `sensor_342`, `sensor_347`, `sensor_478`) inside the training-only pipeline to verify whether retaining single-excursion signals alters validation PR-AUC or fold stability.

*Safeguard:* Exclude `timestamp` and `timestamp_raw` from model predictors; retain them strictly for chronological splitting, ordering, and drift diagnostics.

---

## 3. Chronological Validation & Holdout Strategy
Because Phase 2 demonstrated strong process drift (`22.22%` fail rate in July → `2.88%` in September → `6.13%` in October, plus `sensor_059` baseline drift), **random splitting will not be used as the primary validation strategy**.

### Timestamp-Group-Safe Chronological Design
1. Sort records stably by parsed `timestamp` (preserving original row tie-order within repeated timestamps).
2. Assign a `timestamp_group_id` to every unique timestamp so the `32` repeated-timestamp groups (`65` rows) are **never split across train, validation, or holdout sets**.
3. **Final Untouched Chronological Holdout Set:** Reserve the late production window (target candidate: **October 2008**, `2008-10-01` to `2008-10-17`, `~359` records / `~22` Fail examples, subject to exact boundary check on repeated-timestamp groups) strictly for final one-time evaluation—**never** used for hyperparameter tuning, feature selection, calibration, or threshold selection.
4. **Expanding-Window Chronological Cross-Validation (on Pre-Holdout Data: `2008-07` to `2008-09`, `~1,208` records / `~82` Fails):**
   - Construct expanding-window chronological folds (e.g., 3–4 expanding folds grouped by `timestamp_group_id`), verifying each validation fold contains sufficient Fail observations for stable PR-AUC and recall calculation.
   - Document exact start/end timestamps, record counts, and Pass/Fail counts for every fold and the final holdout set in `reports/` and `models/`.

---

## 4. Baselines & Candidate Models

### Required Baselines
1. **Majority-Class `DummyClassifier`** (`strategy="most_frequent"`): establishes the `93.36%` accuracy trap (`0.0` Fail recall).
2. **Stratified `DummyClassifier`** (`strategy="stratified"`, fixed random seed): establishes random-chance baseline PR-AUC (`~0.066`) and F1.
3. **Baseline `LogisticRegression`** (with `StandardScaler`/`RobustScaler`, `class_weight="balanced"`, and default `L2` regularization).

### Required Candidate Models
1. **Logistic Regression** (tuned `C`, penalty `l1`/`l2`/elasticnet if solver supports, `class_weight` options: `"balanced"` vs. tuned positive weight).
2. **Random Forest** (`class_weight="balanced"` / `"balanced_subsample"`, tuned `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features`).
3. **Extra Trees** (`class_weight="balanced"` / `"balanced_subsample"`, tuned `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features`).
4. **Support Vector Machine (`SVC` with `probability=True` or `CalibratedClassifierCV` on training CV)** (RBF and linear kernels, tuned `C`, `gamma`, `class_weight="balanced"`, scaled inputs).

*Synthetic Oversampling Policy:* SMOTE / ADASYN will **not** be used by default given high dimensionality (`440` features) and `104` positive samples; if tested as an optional ablation, it will be strictly inside training folds via `imblearn.pipeline.Pipeline` with documented justification.

---

## 5. Evaluation Metrics & Decision Threshold Optimization

### Evaluation Metrics (Reported on Both Expanding-Window Validation & Final Holdout)
- **Primary:** Fail-class Precision, Fail-class Recall (Sensitivity), Fail-class F1-score, Balanced Accuracy, **PR-AUC (Average Precision)**.
- **Additional:** ROC-AUC, Matthews Correlation Coefficient (MCC), Overall Accuracy, Confusion Matrix (`TN, FP, FN, TP`), Specificity (`TNR`), False-Positive Rate (`FPR`), False-Negative Rate (`FNR`).
- Model selection will prioritize **expanding-window validation PR-AUC**, **Fail Recall**, **Fail F1**, and **MCC**—never Accuracy alone.

### Threshold Optimization (Validation Only)
- Sweep probability thresholds `t ∈ [0.05, 0.95]` on out-of-fold chronological validation predictions (never on the final holdout set).
- Plot Precision–Recall trade-offs and `FP` / `FN` operational counts across thresholds.
- Select the operating threshold using a clearly documented objective (e.g., maximizing `F_beta` with `beta=2` or `F1` subject to a minimum recall / bounded false-alarm floor), explicitly noting that true cost-optimal selection requires fab-specific scrap vs. inspection cost figures.
- Apply the validation-chosen threshold once to the frozen final holdout set and report holdout metrics at both default `0.50` (for reference) and the selected threshold.

---

## 6. Explainability, Temporal Drift & Calibration

### Explainability (`src/secom_project/explainability.py`)
- Compute **permutation importance** (scoring = `average_precision` / PR-AUC) on held-out chronological validation / holdout splits.
- Extract **model-specific importance** (e.g., standardized Logistic Regression coefficients with sign/direction, tree impurity/permutation importance).
- Run **SHAP analysis** (`LinearExplainer` / `TreeExplainer`) if computationally stable on the winning model.
- Report Top 20 predictive anonymous sensors, association direction where consistent, and **rank stability across chronological validation folds** (e.g., Spearman rank correlation of feature importances across time periods).

### Temporal Drift & Robustness
- Evaluate holdout and expanding-window validation metrics broken down by chronological sub-period (e.g., monthly / bi-weekly windows).
- Track feature distribution shift (e.g., Population Stability Index / Kolmogorov–Smirnov tests between training and holdout periods) for the top 20 predictive features, testing whether `sensor_059` drift observed in Phase 2 degrades static models in October 2008.

### Probability Calibration
- Compute Brier score and generate reliability diagrams on chronological validation predictions.
- Test post-hoc calibration (Platt/sigmoid or isotonic via training-fold CV) **only** if sample counts in validation folds are sufficient; if `~22`–`82` Fail instances are too sparse for stable isotonic binning, document the sample-size limitation explicitly rather than forcing overfit calibration.

---

## 7. Planned Deliverables & Repository Mapping
*(Adapting cleanly alongside existing Phase 2 `src/secom_project/data_validation.py`)*

- **Source Modules (`src/secom_project/`):**
  - `validation.py` — Timestamp-group-aware chronological splitting & expanding-window CV splitter.
  - `modeling.py` — Leakage-safe scikit-learn pipelines, baseline & candidate training, hyperparameter search, deterministic seeds, Joblib model persistence.
  - `evaluation.py` — Metric suite, threshold optimization, calibration/Brier analysis, temporal period evaluation, figure generation.
  - `explainability.py` — Permutation importance, model coefficients/importances, optional SHAP, cross-period importance stability.
- **Notebook:** `notebooks/03_predictive_modeling.ipynb` (executed end-to-end).
- **Reports (`reports/`):**
  - `phase3_model_comparison.md`
  - `phase3_evaluation_report.md`
  - `phase3_explainability_report.md`
  - `phase3_temporal_drift_report.md`
  - Machine-readable metric & threshold tables (`.csv` / `.json`).
- **Models (`models/`):** Saved validated pipeline artifacts (fit on pre-holdout training data, **never** refit on the final holdout set for reported metrics), preprocessing configs, split boundaries, feature lists, and random seeds.
- **Figures (`reports/figures/`):** Class distribution, model comparison, confusion matrix, PR curves, ROC curves, threshold vs. precision/recall, feature importance, SHAP summary (if appropriate), calibration curve, and performance across chronological periods (each with title, labeled axes, and written interpretation).
- **Tests (`tests/`):**
  - `test_temporal_validation.py` (chronological ordering, zero future-to-past leakage, zero shared-timestamp split leakage)
  - `test_modeling.py` (fit-on-train pipeline isolation, reproducibility with fixed seed, valid serialized predictions, target handling)
  - `test_evaluation.py` (metric calculation accuracy, threshold selection isolation from holdout, confusion matrix/PR-AUC checks)

---

## 8. Execution Gate
No Phase 3 code, model training, or dashboard work will start until the project owner explicitly approves this Phase 3 execution plan.
