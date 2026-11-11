# Phase 1 Dataset Audit Report — UCI SECOM

**Project:** Smart Manufacturing: Intelligent Process Quality Analysis and Predictive Defect Detection Using Machine Learning  
**Dataset:** SECOM (Semiconductor Manufacturing Process), UCI Machine Learning Repository ID 179 (`doi:10.24432/C54305`)  
**Scope:** Data retrieval, structural inspection, target-label verification, chronological assessment, data dictionary creation, and data leakage risk identification. *(No ML models or dashboards built in Phase 1.)*

---

## 1. Documented Retrieval Method & File Inventory

Retrieved directly from the official UCI repository archive via `src/secom_project/download_data.py`:
- **Landing page:** `https://archive.ics.uci.edu/dataset/179/secom`
- **Primary archive:** `https://archive.ics.uci.edu/static/public/179/secom.zip`
- **Metadata API:** `https://archive.ics.uci.edu/api/dataset?id=179`

Extracted files in `data/raw/` (checksums recorded in `data/raw/DOWNLOAD_MANIFEST.json`):

| File | Size (bytes) | Format & Structure |
|---|---:|---|
| `secom.zip` | 1,964,989 | Official UCI archive |
| `secom.data` | 5,389,983 | Space-separated numeric matrix (`1567` rows × `590` columns), no header, missing values encoded as `NaN` |
| `secom_labels.data` | 40,638 | Space-separated labels & quoted timestamps (`1567` rows × `2` columns), no header |
| `secom.names` | 4,223 | Plain-text UCI dataset documentation & baseline feature-selection notes |
| `uci_api_metadata.json` | — | Official UCI REST metadata snapshot |

### Documentation Discrepancies Caught
1. **Attribute count (`590` vs `591`):** Both `secom.names` and `uci_api_metadata.json` list `591` attributes/features, whereas `secom.data` actually contains **590** sensor columns (`sensor_000`–`sensor_589`). Counting the timestamp (or label) gives `591`.
2. **Missing values flag:** `uci_api_metadata.json` erroneously reports `"has_missing_values": "no"`, while `secom.names` correctly states `"Missing Values? Yes"` (`NaN` as per MATLAB) and `secom.data` contains `41,951` `NaN` entries.

---

## 2. Quantitative Structural Audit

| Metric | Observed Value |
|---|---:|
| **Rows (Production Entities)** | `1,567` (aligned 1:1 across `secom.data` and `secom_labels.data`) |
| **Sensor Columns (`secom.data`)** | `590` (`sensor_000` – `sensor_589`, all `float64`) |
| **Label / Metadata Columns (`secom_labels.data`)** | `2` (`target_label`, `timestamp_raw`) |
| **Target Labels: Pass (`-1`)** | `1,463` (`93.3631%`) |
| **Target Labels: Fail (`1`)** | `104` (`6.6369%`) |
| **Class Imbalance Ratio (Pass : Fail)** | `14.0673 : 1` |
| **Missing Labels / Timestamps** | `0` (`0.0%`) |
| **Missing Sensor Cells** | `41,951` / `924,530` (`4.5375%`) |
| **Sensor Columns with Any Missingness** | `538` / `590` (`52` columns have `0` missing values) |
| **Sensor Columns >50% / >80% / >90% Missing** | `28` / `8` / `4` (max column missingness: `91.1934%`, `1,429` rows) |
| **All-NaN Sensor Columns** | `0` |
| **Rows with Any Missing Sensor Value** | `1,567` / `1,567` (`100%`; `0` complete rows; min `0.678%`, median `4.0678%`, max `25.7627%`) |
| **Mean Row Missingness (Pass vs Fail)** | `4.5533%` (Pass) vs `4.3155%` (Fail) |
| **Constant (Zero-Variance) Sensor Columns** | `116` / `590` (`19.661%`) |
| **Non-Constant Duplicate Sensor Columns** | `0` (`7` duplicate groups exist only among constant columns) |
| **Duplicate Rows** | `0` (across sensors alone, sensors + label, and sensors + label + timestamp) |

---

## 3. Verification of Target-Label Encoding

In `secom.names` (line 46), an ASCII encoding glitch prints:
> *"Where .1 corresponds to a pass and 1 corresponds to a fail"*

Cross-checking against the live UCI metadata (`uci_api_metadata.json`) and the dataset summary resolves this unambiguously:
- `uci_api_metadata.json` preserves the original en-dash: *"Where –1 corresponds to a pass and 1 corresponds to a fail"*.
- `secom.names` (line 69) explicitly states: *"SECOM Dataset: 1567 examples 591 features, 104 fails"*.
- In `secom_labels.data`, the value `1` occurs exactly **104** times and `-1` occurs **1,463** times.

**Verified encoding:** **`-1` = Pass**, **`1` = Fail**.

---

## 4. Chronological Analysis Assessment (`timestamp_raw`)

- **Parsing:** All `1,567 / 1,567` timestamps parse cleanly under `DD/MM/YYYY HH:MM:SS` (`%d/%m/%Y %H:%M:%S`), with no timezone specified.
- **Time Span:** `2008-07-19 11:55:00` to `2008-10-17 06:07:00` (**89.76 days**).
- **Ordering:** The raw file is **monotonically non-decreasing** (`0` backward time steps), though **not strictly increasing** (`33` zero-second steps; `1,534` unique timestamps; `32` repeated timestamp values spanning `65` rows).
- **Sampling Intervals (sorted):** Median `37.0` min, mean `82.54` min, 95th percentile `291.0` min, max `2,918.0` min (`2.03` days).
- **Non-Stationarity / Defect Rate Drift:**
  - `2008-07`: `14` fails / `63` tests (`22.22%`)
  - `2008-08`: `51` fails / `555` tests (`9.19%`)
  - `2008-09`: `17` fails / `590` tests (`2.88%`)
  - `2008-10`: `22` fails / `359` tests (`6.13%`)
- **Shared-Timestamp Conflicts:** `3` repeated timestamps (`2008-08-05 07:12:00`, `2008-08-31 10:59:00`, `2008-10-05 00:33:00`) each contain two rows with opposing labels (`-1` and `1`).

**Conclusion:** Timestamps **do support chronological analysis** (temporal drift monitoring, rolling-window validation, and forward-in-time train/test splits). However:
1. Irregular intervals (`0` min to `2.03` days) mean it is **event-ordered process data**, not a uniform-frequency time series.
2. Time-based splits must **group identical timestamps** (especially the `32` repeated timestamp groups) so simultaneous runs are never split across train and test.

---

## 5. Data Dictionary

Generated programmatically in:
- [`docs/data_dictionary.csv`](data_dictionary.csv) (machine-readable, all `592` fields)
- [`docs/data_dictionary.md`](data_dictionary.md) (human-readable tables)

All `2` documented fields (`target_label`, `timestamp_raw`) are clearly separated from the `590` anonymous numeric sensor columns (`sensor_000`–`sensor_589`), preserving 0-based index, 1-based column number, provenance status, missingness, uniqueness, constant flag, and summary range statistics.

---

## 6. Identified Data Leakage Risks

1. **Temporal / Non-Stationarity Leakage (Random Splits vs. Chronological Splits):**
   Monthly fail rates drop from `22.22%` in July 2008 to `2.88%` in September 2008. Standard random k-fold CV (as used in the `secom.names` baseline) mixes adjacent runs from the same process regime/drift episode across train and test, overestimating prospective defect-detection performance.
   *Mitigation:* Use chronological holdout and/or forward-chaining time-series CV (`TimeSeriesSplit` / blocked temporal splits) alongside grouped handling of tied timestamps.

2. **Preprocessing, Imputation & Constant-Removal Leakage:**
   Because `100%` of rows contain missing values and `116` columns are constant overall (and additional columns may be constant within a training fold), computing imputation statistics (mean/median/kNN/iterative), scaling parameters, missingness-threshold filters, or variance filters on the full dataset before splitting leaks test-set distributions.
   *Mitigation:* Encapsulate all filtering, imputation, scaling, and modeling inside a `Pipeline` fit strictly on training folds.

3. **Supervised Feature Selection & Resampling Leakage:**
   With `590` noisy features and only `104` positive fail cases, performing supervised feature selection (`t-test`, `F-test`, `Pearson`, `S2N`, `Relief`—explicitly referenced in `secom.names`) or oversampling (`SMOTE` / class-balancing resampling) prior to cross-validation severely leaks target information and inflates minority-class metrics.
   *Mitigation:* Place feature selection and resampling strictly inside each training fold (nested CV if tuning selection `k`).

4. **Shared-Timestamp Boundary Leakage:**
   `65` rows share `32` exact timestamps (`3` pairs even have conflicting Pass/Fail labels). Splitting inside a timestamp tie allows contemporaneous process state from the same minute to appear in both training and evaluation sets.
   *Mitigation:* Keep identical timestamps together on one side of any temporal or grouped split.

5. **Timestamp-as-Feature Leakage:**
   Using raw `timestamp_raw` (or monotonic row index) as a predictor would let a model memorize historical defect waves (e.g., July 2008 `22.22%` vs September 2008 `2.88%`) rather than physical sensor excursions, failing completely on future production.
   *Mitigation:* Exclude raw timestamps and row indices from model features; use timestamps solely for splitting, drift diagnostics, and dashboard monitoring.

6. **Anonymous Feature Provenance / Post-Test Metrology Risk:**
   Because the `590` sensor signals lack process-step timestamps and descriptions, any sensor recorded *downstream of* or *derived from* the inline test point (or missingness patterns caused by aborting measurements after an inline fail) represents potential target leakage that cannot be ruled out from UCI metadata alone.
   *Mitigation:* Audit top-ranked features and missingness-indicator correlations carefully during modeling and document the anonymous-provenance caveat in final conclusions.
