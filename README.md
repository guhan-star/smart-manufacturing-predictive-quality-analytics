# Smart Manufacturing: Intelligent Process Quality Analysis and Predictive Defect Detection Using Machine Learning

## Project Overview
This project investigates semiconductor manufacturing process quality analysis and predictive defect detection using the **UCI SECOM** dataset ([UCI Machine Learning Repository ID 179](https://archive.ics.uci.edu/dataset/179/secom)).

## Current Phase: Phase 2 — Data Preparation & Exploratory Data Analysis
*(Phase 1 audit and data dictionary remain preserved in `docs/` and `reports/secom_audit_summary.json`. No ML model training or dashboarding has been performed yet.)*

### Project Structure
```text
.
├── pyproject.toml                         # Project metadata and dependencies
├── requirements.txt                       # Pinned runtime & test dependencies
├── README.md                              # Project documentation
├── data/
│   ├── raw/                               # Official UCI SECOM files (preserved unmodified)
│   └── processed/
│       ├── secom_cleaned.csv              # Analysis-ready dataset (1567 x 443)
│       └── secom_cleaning_summary.json    # Machine-readable cleaning audit & medians
├── docs/
│   ├── data_dictionary.md                 # Phase 1 documented & anonymous sensor dictionary
│   ├── data_dictionary.csv                # Machine-readable field dictionary
│   └── dataset_audit_report.md            # Phase 1 audit, timestamp & leakage analysis
├── notebooks/
│   └── 02_data_preparation_and_eda.ipynb  # Executed Phase 2 preparation & EDA notebook
├── reports/
│   ├── secom_audit_summary.json           # Phase 1 audit metrics
│   ├── phase2_data_quality_report.md      # Phase 2 validation, cleaning, outliers & safeguards
│   ├── phase2_statistical_analysis.md     # Phase 2 stats, rankings, correlations & chart interpretations
│   ├── phase2_statistical_summary.csv     # Descriptive stats & rankings for 440 cleaned sensors
│   ├── phase2_missing_value_report.csv    # Per-feature missingness audit (590 raw sensors)
│   └── figures/                           # 8 Phase 2 visualisations (PNG)
├── src/
│   └── secom_project/
│       ├── __init__.py
│       ├── download_data.py               # Phase 1: Reproducible UCI SECOM retrieval
│       ├── inspect_data.py                # Phase 1: Raw loader (load_raw_secom) & audit
│       ├── data_validation.py             # Phase 2: Validation & outlier/duplicate checks
│       ├── data_cleaning.py               # Phase 2: Fit/transform cleaning pipeline
│       └── eda.py                         # Phase 2: Stats, feature rankings & visualisations
└── tests/
    └── test_data_cleaning.py              # Automated Phase 2 tests (runnable from repo root)
```

## Setup & Usage
Using `uv` from the repository root:
```bash
uv sync
uv run python -m secom_project.download_data
uv run python -m secom_project.data_cleaning
uv run python -m secom_project.eda
uv run pytest -v
```

To re-execute the Phase 2 notebook end-to-end:
```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/02_data_preparation_and_eda.ipynb
```
