# Smart Manufacturing: Intelligent Process Quality Analysis and Predictive Defect Detection Using Machine Learning

## Project Overview
This project investigates semiconductor manufacturing process quality analysis and predictive defect detection using the **UCI SECOM** dataset ([UCI Machine Learning Repository ID 179](https://archive.ics.uci.edu/dataset/179/secom)).

## Current Phase: Phase 4 — Interactive Streamlit Dashboard
All four project phases are complete:
- **Phase 1:** Official dataset retrieval, SHA-256 verification, data dictionary, and leakage risk audit (`docs/`).
- **Phase 2:** Strict validation, fit/transform cleaning pipeline, BH-FDR testing, observed-only sensitivity, and EDA (`notebooks/02_data_preparation_and_eda.ipynb`, `reports/phase2_*`).
- **Phase 3:** Chronological Train/Validation/Test pipeline (`Dummy_Majority`, `LogisticRegression`, `RandomForest`, `HistGradientBoosting`), validation-only threshold selection (`t* = 0.19`), lightweight feature importance, and persisted artifacts (`models/`, `reports/phase3/`).
- **Phase 4:** Interactive Streamlit analytics & wafer-prediction dashboard (`app.py`, `src/secom_project/inference.py`).

### Project Structure
```text
.
├── app.py                                 # Phase 4: Interactive Streamlit dashboard
├── pyproject.toml                         # Project metadata and dependencies
├── requirements.txt                       # Pinned dependencies
├── README.md                              # Project documentation
├── .github/workflows/ci.yml               # GitHub Actions CI (Phases 1–4 + pytest)
├── data/
│   ├── raw/                               # Official UCI SECOM files (preserved unmodified)
│   └── processed/                         # Phase 2 cleaned dataset & cleaning summary
├── docs/                                  # Phase 1 dictionary, audit & Phase 3 plan
├── models/                                # Saved Phase 3 pipelines & metadata
├── notebooks/
│   └── 02_data_preparation_and_eda.ipynb  # Executed Phase 2 preparation & EDA notebook
├── reports/
│   ├── secom_audit_summary.json           # Phase 1 audit metrics
│   ├── phase2_*                           # Phase 2 quality, statistical & sensitivity reports
│   ├── figures/                           # Phase 2 visualisations (8 PNGs)
│   └── phase3/                            # Phase 3 modeling metrics, plots & report
├── src/secom_project/
│   ├── download_data.py                   # Phase 1: UCI SECOM retrieval
│   ├── inspect_data.py                    # Phase 1: Raw loader & audit
│   ├── data_validation.py                 # Phase 2: Strict validation & duplicate checks
│   ├── data_cleaning.py                   # Phase 2: Fit/transform cleaning pipeline
│   ├── eda.py                             # Phase 2: Stats, BH-FDR & plots
│   ├── validation.py                      # Phase 3: Chronological Train/Val/Test splitter
│   ├── evaluation.py                      # Phase 3: Metrics & validation-only threshold sweep
│   ├── transformers.py                    # Phase 3: Leakage-safe sklearn preprocessor
│   ├── modeling.py                        # Phase 3: Model comparison & persistence
│   └── inference.py                       # Phase 4: CSV validation & live prediction helper
└── tests/                                 # Automated tests (Phases 2–4, 19 tests)
```

## Installation & Launch

### 1. Install Dependencies
Using `uv` (recommended):
```bash
uv sync --locked
```
Or with `pip`:
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Reproduce Data & Models (If Needed)
```bash
uv run python -m secom_project.download_data
uv run python -m secom_project.data_cleaning
uv run python -m secom_project.eda
uv run python -m secom_project.modeling
```

### 3. Launch the Interactive Streamlit Dashboard
```bash
uv run streamlit run app.py
```

### 4. Run Automated Tests
```bash
uv run pytest -v
```
