# Phase 2 Data Quality & Preparation Report — UCI SECOM

## 1. Raw Data Integrity, Alignment & Validation
- `secom.zip`: VERIFIED
- `secom.data`: VERIFIED
- `secom.names`: VERIFIED
- `secom_labels.data`: VERIFIED

- **Raw Dimensions:** `1567` rows × `590` sensor columns (`sensor_000`–`sensor_589` via Phase 1 `load_raw_secom()`) + `2` label/timestamp columns (`target_label`, `timestamp_raw`).
- **Row Alignment:** `True` (original chronological row order preserved).
- **Data Types & Infinite Values:** All `590` sensors are `float64`; `0` `+inf` and `0` `-inf` values detected.
- **Target Validation:** `0` missing labels; `True` (`{-1, 1}` only).
  - **Pass (`-1`):** `1463` (`93.3631%`)
  - **Fail (`1`):** `104` (`6.6369%`)
  - **Class Imbalance:** `14.0673 : 1` (~`14:1` Pass:Fail)
- **Timestamp Validation:** `0` missing raw timestamps; `0` failed parses under `%d/%m/%Y %H:%M:%S`.
  - Span: `2008-07-19 11:55:00` to `2008-10-17 06:07:00` (`89.76` days).
  - Monotonically non-decreasing in raw order: `True` (`1534` unique timestamps; `32` repeated timestamp groups covering `65` rows).

## 2. Duplicate, Constant & Near-Constant Investigation
- **Duplicate Rows:** `0` duplicate sensor rows; `0` full duplicate rows.
- **Duplicate Columns:** `7` duplicate column groups total, all among strictly constant columns (`0` non-constant duplicate groups).
- **Strictly Constant Columns (`nunique <= 1`):** `116` features — zero variance, removed.
- **Near-Constant Columns (dominant value >= `99%`):** `6` features (`0.0` in `1,560 / 1,561` non-null rows; only Pass row `1458` differs) — removed to prevent fold instability:
- `sensor_074`: dominant value `0.0` in 99.9359% of 1561 non-null observations (only row 1458 differs)
- `sensor_206`: dominant value `0.0` in 99.9359% of 1561 non-null observations (only row 1458 differs)
- `sensor_209`: dominant value `0.0` in 99.9359% of 1561 non-null observations (only row 1458 differs)
- `sensor_342`: dominant value `0.0` in 99.9359% of 1561 non-null observations (only row 1458 differs)
- `sensor_347`: dominant value `0.0` in 99.9359% of 1561 non-null observations (only row 1458 differs)
- `sensor_478`: dominant value `0.0` in 99.9359% of 1561 non-null observations (only row 1458 differs)

## 3. Missing-Value Analysis & Threshold Impact
- **Overall Missingness (Before Cleaning):** `41,951` / `924,530` cells (`4.5375%`); `538 / 590` features and `1567 / 1,567` records (`100%`) contain at least one `NaN`.
- **Why Rows Were NOT Dropped:** Record missingness ranges from `0.68%` to `25.76%` (median `4.07%`). Dropping every row with a missing value would discard `100%` of the dataset; therefore **`0` records were removed**.

### Missingness Threshold Sensitivity Analysis
| Missingness Cutoff | Features Exceeding Cutoff | Total Removed (incl. 116 Constant + 6 Near-Constant) | Features Retained |
|---|---:|---:|---:|
| > 20% | 32 | 154 | 436 |
| > 40% | 32 | 154 | 436 |
| > 50% | 28 | 150 | 440 |
| > 60% | 24 | 146 | 444 |
| > 80% | 8 | 130 | 460 |

We select **`> 50%` missingness** (`28` features, `50.67%` to `91.19%` missing) because there is a natural empirical gap between `45.63%` (4 moderate features) and `50.67%` (`28` features), avoiding synthetic imputation of majority-missing columns while preserving `440` active sensors.

### Removed High-Missingness Features (`> 50%`, `28` Features)
- `sensor_157`: 91.19% missing
- `sensor_158`: 91.19% missing
- `sensor_292`: 91.19% missing
- `sensor_293`: 91.19% missing
- `sensor_085`: 85.58% missing
- `sensor_220`: 85.58% missing
- `sensor_358`: 85.58% missing
- `sensor_492`: 85.58% missing
- `sensor_109`: 64.96% missing
- `sensor_110`: 64.96% missing
- `sensor_111`: 64.96% missing
- `sensor_244`: 64.96% missing
- `sensor_245`: 64.96% missing
- `sensor_246`: 64.96% missing
- `sensor_382`: 64.96% missing
- `sensor_383`: 64.96% missing
- `sensor_384`: 64.96% missing
- `sensor_516`: 64.96% missing
- `sensor_517`: 64.96% missing
- `sensor_518`: 64.96% missing
- `sensor_578`: 60.56% missing
- `sensor_579`: 60.56% missing
- `sensor_580`: 60.56% missing
- `sensor_581`: 60.56% missing
- `sensor_072`: 50.67% missing
- `sensor_073`: 50.67% missing
- `sensor_345`: 50.67% missing
- `sensor_346`: 50.67% missing

### Missingness vs. Target & Possible Target Leakage Warning
Missingness is **not MCAR**: several sensor blocks exhibit large missingness differences between Pass and Fail records:

| Feature | Overall Missing | Pass Missing | Fail Missing | |Fail - Pass| | Action |
|---|---:|---:|---:|---:|---|
| `sensor_072` | 50.67% | 51.81% | 34.62% | 17.20 pp | Removed (High Missingness >50%) |
| `sensor_073` | 50.67% | 51.81% | 34.62% | 17.20 pp | Removed (High Missingness >50%) |
| `sensor_345` | 50.67% | 51.81% | 34.62% | 17.20 pp | Removed (High Missingness >50%) |
| `sensor_346` | 50.67% | 51.81% | 34.62% | 17.20 pp | Removed (High Missingness >50%) |
| `sensor_385` | 45.63% | 46.62% | 31.73% | 14.89 pp | Retained + Median Imputed (Unsupervised) |
| `sensor_112` | 45.63% | 46.62% | 31.73% | 14.89 pp | Retained + Median Imputed (Unsupervised) |
| `sensor_519` | 45.63% | 46.62% | 31.73% | 14.89 pp | Retained + Median Imputed (Unsupervised) |
| `sensor_247` | 45.63% | 46.62% | 31.73% | 14.89 pp | Retained + Median Imputed (Unsupervised) |
| `sensor_111` | 64.96% | 64.52% | 71.15% | 6.63 pp | Removed (High Missingness >50%) |
| `sensor_109` | 64.96% | 64.52% | 71.15% | 6.63 pp | Removed (High Missingness >50%) |

Cross-tabulating against production months shows this gap tracks **logging-regime changes** over time:

| Month | Records | Fail Rate | Mean Row Missing | `sensor_072` Missing | `sensor_112` Missing |
|---|---:|---:|---:|---:|---:|
| 2008-07 | 63 | 22.22% | 4.65% | 15.87% | 31.75% |
| 2008-08 | 555 | 9.19% | 5.33% | 32.25% | 17.48% |
| 2008-09 | 590 | 2.88% | 4.25% | 62.03% | 46.95% |
| 2008-10 | 359 | 6.13% | 3.77% | 66.57% | 89.42% |

**Leakage Risk:** If missingness reflects downstream test skipping or logging changes tied to defect waves, naive missingness indicators or full-dataset imputation could leak temporal/operational regime information.

## 4. Non-Destructive Outlier Audit
We evaluated IQR fences on the `436` retained active features with `IQR > 0` (`4` active features have `IQR = 0` due to discrete/zero-inflated distributions):
- **Mild Outliers (`1.5 × IQR`):** `23,672` / `672,380` evaluated cells (`3.5206%`)
- **Extreme Outliers (`3.0 × IQR`):** `8,420` cells (`1.2523%`), affecting `1392` / `1,567` records.
- **Decision:** **0 outliers removed.** Without physical sensor documentation, high/low spikes cannot be assumed to be measurement errors and may represent genuine process excursions associated with wafer defects.

## 5. Final Cleaning Summary & Critical Safeguards
- **Input Dimensions:** `1,567` rows × `590` sensors (`41,951` missing cells)
- **Output Dimensions (`data/processed/secom_cleaned.csv`):** `1,567` rows × `443` columns (`target_label`, `timestamp`, `timestamp_raw`, plus `440` cleaned sensors; `0` missing cells)
- **Imputation:** Unsupervised per-feature median imputation across the `10,832` missing cells in the `440` retained sensors (`uses_target_label = False`).
- **Safeguards Enforced:**
  1. Anonymous sensor names (`sensor_000`–`sensor_589`) preserved with zero fabricated physical meanings.
  2. `target_label` and `timestamp` kept separate; raw `timestamp` excluded from future predictive features unless explicitly justified by temporal design.
  3. Original chronological row order and all `32` repeated-timestamp groups preserved (`0` rows dropped).
  4. `14.07 : 1` class imbalance recorded for Phase 3 modeling/evaluation planning.
  5. `fit_cleaning_plan()` / `apply_cleaning_plan()` implemented cleanly so Phase 3 splits fit preprocessing strictly on training data.
