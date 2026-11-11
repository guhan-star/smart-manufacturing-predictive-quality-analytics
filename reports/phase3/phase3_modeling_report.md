# Phase 3 Predictive Quality Modeling Report — UCI SECOM

## 1. Chronological Split & Leakage Prevention
- **Method:** Reused Phase 1 `load_raw_secom()` and Phase 2 `fit_cleaning_plan()` inside `SecomTrainingPreprocessor`, fitting all feature filtering (`constant`, `>=99% near-constant`, `>50% missing`), median imputation, and `StandardScaler` strictly on the Training partition (`y` ignored). Raw `timestamp` and `target_label` were never used as predictors, and repeated-timestamp groups were kept intact across boundaries.
- **Train (`2008-07-19 11:55:00` → `2008-09-04 08:41:00`):** `725` records (`658` Pass, `67` Fail / `9.24%`)
- **Validation (`2008-09-04 08:53:00` → `2008-09-30 23:58:00`):** `483` records (`468` Pass, `15` Fail / `3.11%`)
- **Held-out Test (`2008-10-01 00:20:00` → `2008-10-17 06:07:00`):** `359` records (`337` Pass, `22` Fail / `6.13%`)

*Small-Sample Limitation:* The chronological validation window (`2008-09`) contains `15` Fail examples (`3.11%`) and the October held-out test set contains `22` Fail examples (`6.13%`). Per project safeguards, we preserve chronological ordering rather than switching to random splits.

## 2. Model Comparison (Validation-Only Selection & Thresholding)
| Model | Val t* | Val PR-AUC | Val ROC-AUC | Val Prec | Val Rec | Val F1 | Val F2 | Test PR-AUC | Test ROC-AUC | Test Prec | Test Rec | Test F1 | Test F2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `Dummy_Majority` | 0.50 | 0.0311 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0613 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `LogisticRegression` | 0.64 | 0.0333 | 0.5236 | 0.0319 | 0.4000 | 0.0591 | 0.1210 | 0.0775 | 0.5979 | 0.0805 | 0.3182 | 0.1284 | 0.2000 |
| `RandomForest` | 0.22 | 0.1537 | 0.7091 | 0.1111 | 0.3333 | 0.1667 | 0.2381 | 0.0901 | 0.5943 | 0.0833 | 0.1818 | 0.1143 | 0.1471 |
| `HistGradientBoosting` | 0.19 | 0.2080 | 0.6610 | 0.2381 | 0.3333 | 0.2778 | 0.3086 | 0.0828 | 0.5968 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

- **Selected Model:** **`HistGradientBoosting`** (selected solely from Validation performance: highest Validation PR-AUC `=0.2080` with strong Fail Recall `=0.3333`).
- **Selected Decision Threshold (Validation-Only):** **`t* = 0.19`** (maximizing Validation `F2` within a `1%–40%` flag rate).
- **Final Held-Out Test Evaluation (`HistGradientBoosting` at `t* = 0.19`):**
  - PR-AUC: `0.0828` | ROC-AUC: `0.5968`
  - Fail Precision: `0.0000` | Fail Recall: `0.0000` | F1: `0.0000` | F2: `0.0000`
  - Confusion Matrix: `TN=324`, `FP=13`, `FN=22`, `TP=0`

## 3. Visualisations
- `confusion_matrix.png`: Compares Validation vs. Held-out Test confusion matrices at `t* = 0.19`.
- `precision_recall_curve.png`: Shows Precision–Recall trade-offs against the `3.11%` validation and `6.13%` test base rates.
- `roc_curve.png`: Shows TPR vs. FPR across thresholds for all three ML models.
- `feature_importance.png`: Displays the top 15 sensors from `LogisticRegression` standardized coefficients and `RandomForest` impurity importance.

## 4. Top 15 Predictive Anonymous Sensors (Association Only — Not Causation)
| Rank | Sensor | LogReg Signed Coef | RandomForest Importance |
|---:|---|---:|---:|
| 1 | `sensor_059` | +0.4655 | 0.03029 |
| 2 | `sensor_000` | -0.3435 | 0.00818 |
| 3 | `sensor_021` | +0.1625 | 0.01038 |
| 4 | `sensor_064` | +0.1977 | 0.00743 |
| 5 | `sensor_562` | -0.2465 | 0.00354 |
| 6 | `sensor_460` | +0.2113 | 0.00575 |
| 7 | `sensor_008` | -0.2509 | 0.00292 |
| 8 | `sensor_485` | -0.2537 | 0.00236 |
| 9 | `sensor_341` | +0.0839 | 0.01283 |
| 10 | `sensor_197` | +0.1923 | 0.00522 |
| 11 | `sensor_280` | -0.2072 | 0.00416 |
| 12 | `sensor_058` | +0.1885 | 0.00533 |
| 13 | `sensor_091` | -0.2296 | 0.00241 |
| 14 | `sensor_041` | -0.2063 | 0.00353 |
| 15 | `sensor_488` | -0.2088 | 0.00320 |

*Causality Safeguard:* All sensors are anonymous; coefficients and tree importances reflect statistical predictive associations in historical data, not physical root causes.
