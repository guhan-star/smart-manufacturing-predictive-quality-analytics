# Project Demonstration & Viva Defense Guide

## 1. Live Demonstration Script (`uv run streamlit run app.py`)
1. **Verify Environment & Tests First (Terminal):**
   ```bash
   uv run pytest -v
   uv run streamlit run app.py
   ```
2. **Section 1 — Project Overview:** Highlight `1,567` records, `590` raw sensors (`440` cleaned), `6.64%` Fail imbalance (`14.07:1`), and the strict chronological split table (`725` Train / `483` Val / `359` Test) with `0` shared timestamps.
3. **Section 2 — Exploratory Data Analysis:** Show the `22.22% → 2.88% → 6.13%` monthly fail-rate swing, the `50%` missingness cutoff, BH-FDR correction (`86` raw `p<0.05` → `25` imputed `q<0.05` vs `20` observed-only `q<0.05`), and the correlation heatmap (`112` pairs `|r| >= 0.99`).
4. **Section 3 — Predictive Model Comparison:** Contrast Validation (`HistGradientBoosting` PR-AUC `0.2080`, `t* = 0.19`) against Held-out October Test (`PR-AUC = 0.0828`, `0/22` TP at fixed `t*`), explaining why random splits would hide this drift.
5. **Section 4 — Interactive Prediction:** Click **"Download Sample Sensor CSV (10 Real Rows)"**, upload it into the file uploader, and show live `P(Fail)` scoring (`Max = 0.1125` Moderate Watch, `Mean = 0.0462`), threshold marker `t* = 0.19`, and downloadable prediction CSV. Optionally upload a CSV missing `sensor_059` to demonstrate clear input-validation error handling.
6. **Section 5 — Explainability & Findings:** Show Top 15 anonymous sensors (`sensor_059`, `sensor_000`, `sensor_021`), emphasize **association ≠ causation**, and present rolling-retraining + adaptive SPC recommendations.

---

## 2. Known Limitations & Anticipated Evaluator (Viva) Questions

- **Q1: Why did `HistGradientBoosting` achieve `0.2080` PR-AUC on Validation but `0` True Positives on the October Test set?**  
  *Answer:* On September validation, `HistGradientBoosting` achieved `33.33%` recall and `23.81%` precision at `t* = 0.19`. In October, covariate drift across sensors (including `sensor_059` drifting downward) compressed predicted probabilities below `0.19`. Importantly, its ranking metric stayed above the `0.0613` base rate (`Test PR-AUC = 0.0828`, `ROC-AUC = 0.5968`). We deliberately did **not** re-tune `t*` on October test labels because doing so would be test-set leakage; instead, this proves static thresholds require rolling recalibration.

- **Q2: Why didn't you drop rows with missing values or drop statistical outliers?**  
  *Answer:* `100%` of the `1,567` wafer records contain at least one `NaN` (`0.68%`–`25.76%`), so dropping incomplete rows would destroy the entire dataset. Likewise, `1,392` (`88.8%`) of wafers contain at least one `3.0 × IQR` spike; without physical sensor documentation, deleting spikes risks erasing genuine failure excursions.

- **Q3: Why not use SMOTE before splitting or random 10-fold CV?**  
  *Answer:* Random CV mixes wafers from the same monthly drift regime across train and test, artificially inflating metrics, and `32` repeated-timestamp groups would leak contemporaneous state if split randomly. Applying SMOTE before splitting leaks synthetic minority neighbors across folds; instead, we used class weighting (`balanced` / `balanced_subsample`) strictly inside training pipelines.

- **Q4: Why didn't `sensor_059` being #1 prove it causes wafer defects?**  
  *Answer:* All `590` UCI SECOM sensors are anonymous without engineering units or process-step timestamps. High coefficient/importance values establish statistical association with model predictions, not physical causality.

- **Q5: Is the current model ready for automated wafer scrapping in a real fab?**  
  *Answer:* No. With `104` total failures, anonymous sensors, and multi-week drift sensitivity, it is suitable only as a **demonstration risk-ranking decision-support prototype**; production deployment requires rolling retraining, drift-triggered threshold recalibration, physical sensor mapping, and fab-specific scrap vs. inspection cost matrices.
