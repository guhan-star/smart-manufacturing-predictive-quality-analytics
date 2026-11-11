# Phase 2 Final Review & Fixes Summary — UCI SECOM

## 1. Multiple-Testing Correction (Benjamini–Hochberg FDR)
- **Tests Performed:** `440` two-sided Mann–Whitney U tests comparing Pass (`-1`) vs. Fail (`1`) distributions across the `440` cleaned active sensors.
- **Results (Imputed Dataset):**
  - Raw `p < 0.05`: **`86`** features
  - Benjamini–Hochberg FDR `q < 0.05`: **`25`** features (`reports/phase2_statistical_summary.csv` retains raw `mannwhitney_p`, adjusted `mannwhitney_p_fdr_bh`, `is_raw_significant_0_05`, and `is_fdr_significant_0_05`).
- **Interpretation:** Under `440` simultaneous tests, raw `p < 0.05` allows ~`22` expected false positives by random chance. BH-FDR controls the expected false-discovery proportion at `5%`, tightening candidate discoveries from `86` down to `25`.

## 2. Observed-Only vs. Median-Imputed Statistical Sensitivity (`reports/phase2_observed_vs_imputed_sensitivity.csv`)
- **Comparison Summary:**
  - Raw `p < 0.05`: `86` (observed-only) vs. `86` (median-imputed)
  - BH-FDR `q < 0.05`: **`20`** (observed-only) vs. **`25`** (median-imputed)
- **Features Where BH-FDR Conclusions Differ (`5` features):**

| Feature | Observed `n` (Pass / Fail) | Observed `p` (BH `q`) | Imputed `p` (BH `q`) | Conclusion Shift |
|---|---:|---:|---:|---|
| `sensor_452` | 1462 / 104 | 2.4065e-03 (0.0503) | 2.3992e-03 (0.0493) | Obs FDR=False vs Imp FDR=True |
| `sensor_298` | 1462 / 103 | 2.5488e-03 (0.0503) | 2.6368e-03 (0.0493) | Obs FDR=False vs Imp FDR=True |
| `sensor_431` | 1462 / 103 | 2.6277e-03 (0.0503) | 2.7358e-03 (0.0493) | Obs FDR=False vs Imp FDR=True |
| `sensor_122` | 1454 / 104 | 2.8239e-03 (0.0518) | 2.8016e-03 (0.0493) | Obs FDR=False vs Imp FDR=True |
| `sensor_112` | 781 / 71 | 9.1702e-03 (0.0938) | 2.7948e-03 (0.0493) | Obs FDR=False vs Imp FDR=True |

- **Key Takeaway & Small-Sample Limitation:** In `sensor_112` (`45.63%` missing overall; `n_pass=781`, `n_fail=71`), median imputation injects `682` identical Pass median constants vs `33` Fail medians, artificially tightening tied ranks and pushing `q` from `0.0938` (not FDR-significant on observed data) down to `0.0493`. Similarly, `sensor_122`, `sensor_298`, `sensor_431`, and `sensor_452` lie right on the `q ≈ 0.05` boundary. Features with high missingness (`45.6%`) have substantially smaller observed Fail counts (`n=71` vs `104`), reducing statistical power and amplifying sensitivity to non-MCAR imputation.

## 3. Near-Constant Feature Sensitivity Investigation
All `6` removed near-constant features (`>= 99%` dominant value) equal `0.0` in `1,560 / 1,561` non-null rows (`6` NaNs each) and share **one single exceptional wafer observation (`row_index = 1458`, `target_label = -1` Pass, `timestamp = 2008-10-11 07:39:00`)**:

| Feature | Dominant Value (Count) | NaN Count | Exceptional Row | Exceptional Value | Label & Timestamp |
|---|---:|---:|---:|---:|---|
| `sensor_074` | 0.0 (1560x) | 6 | 1458 | 4.1955 | -1 (2008-10-11 07:39:00) |
| `sensor_206` | 0.0 (1560x) | 6 | 1458 | 2.0 | -1 (2008-10-11 07:39:00) |
| `sensor_209` | 0.0 (1560x) | 6 | 1458 | 46.15 | -1 (2008-10-11 07:39:00) |
| `sensor_342` | 0.0 (1560x) | 6 | 1458 | 0.4472 | -1 (2008-10-11 07:39:00) |
| `sensor_347` | 0.0 (1560x) | 6 | 1458 | 13.9147 | -1 (2008-10-11 07:39:00) |
| `sensor_478` | 0.0 (1560x) | 6 | 1458 | 200.0 | -1 (2008-10-11 07:39:00) |

- **Assessment:** Retaining these `6` features provides zero reliable predictive signal because: (1) all non-zero variance comes from a single Pass wafer (`row 1458`) occurring in October 2008 (Holdout), making all 6 features **strictly zero-variance (`0.0` everywhere)** in Pre-Holdout training (`2008-07`–`2008-09`), and (2) Phase 3 controlled experiments confirmed retaining them degraded Random Forest OOF PR-AUC (`0.1216 → 0.0429`). Removing them is preserved as the reproducible strategy.

## 4. Strict Raw-Data Validation & Duplicate-Column Verification
- `data_validation.py` now enforces strict rejection (`FileNotFoundError` / `ValueError`) for missing manifest or raw files, SHA-256 mismatches, row/dimension misalignment, non-numeric or `±inf` corruption, invalid/missing `target_label`, and missing/unparseable timestamps.
- `find_duplicate_columns()` now uses hashes strictly as a candidate pre-filter and verifies **exact missing-value mask equality AND exact observed-value array equality** before flagging any duplicate column.

## 5. Leakage Tests & Continuous Integration
- `tests/test_data_cleaning.py` verifies that substantial test-set value perturbations (`+1e6`), injected test missingness (`>60%`), and target-label flips leave `fit_cleaning_plan()` medians and feature selection completely invariant, and that `apply_cleaning_plan()` imputes test NaNs using training-fitted medians.
- `.github/workflows/ci.yml` executes `uv sync`, raw retrieval/verification, cleaning, and `pytest` on every push and pull request.
