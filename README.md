# Smart Manufacturing: Intelligent Process Quality Analysis and Predictive Defect Detection Using Machine Learning

## Project Overview
This project investigates semiconductor manufacturing process quality analysis and predictive defect detection using the **UCI SECOM** dataset ([UCI Machine Learning Repository ID 179](https://archive.ics.uci.edu/dataset/179/secom)).

## Current Phase: Phase 3 — Predictive Quality Modelling
*(Phases 1 and 2 remain preserved in `docs/`, `data/`, and `reports/`. No dashboard has been built yet.)*

### Project Structure
```text
.
├── .github/workflows/ci.yml               # GitHub Actions CI (Phases 1–3 + pytest)
├── pyproject.toml                         # Project metadata and dependencies
├── requirements.txt                       # Pinned dependencies
├── README.md                              # Project documentation
├── data/
│   ├── raw/                               # Official UCI SECOM files (preserved unmodified)
│   └── processed/                         # Phase 2 cleaned dataset & cleaning summary
├── docs/
│   ├── data_dictionary.md                 # Phase 1 field dictionary
│   ├── data_dictionary.csv                # Machine-readable field dictionary
│   ├── dataset_audit_report.md            # Phase 1 audit & leakage analysis
│   └── phase3_execution_plan.md           # Phase 3 design plan
├── models/                                # Saved Phase 3 pipelines & metadata
├── notebooks/
│   └── 02_data_preparation_and_eda.ipynb  # Executed Phase 2 preparation & EDA notebook
├── reports/
│   ├── secom_audit_summary.json           # Phase 1 audit metrics
│   ├── phase2_*                           # Phase 2 quality, statistical, BH-FDR & sensitivity reports
│   ├── figures/                           # Phase 2 visualisations (8 PNGs)
│   └── phase3/                            # Phase 3 modeling metrics, plots & report
│       ├── model_comparison.csv
│       ├── test_metrics.json
│       ├── classification_report.txt
│       ├── confusion_matrix.png
│       ├── precision_recall_curve.png
│       ├── roc_curve.png
│       ├── feature_importance.csv
│       ├── feature_importance.png
│       └── phase3_modeling_report.md
├── src/
│   └── secom_project/
│       ├── download_data.py               # Phase 1: UCI SECOM retrieval & SHA-256 manifest
│       ├── inspect_data.py                # Phase 1: Raw loader (`load_raw_secom`) & audit
│       ├── data_validation.py             # Phase 2: Strict validation & duplicate checks
│       ├── data_cleaning.py               # Phase 2: Fit/transform cleaning pipeline
│       ├── eda.py                         # Phase 2: Stats, BH-FDR, sensitivity & plots
│       ├── validation.py                  # Phase 3: Chronological Train/Val/Test splitter
│       ├── evaluation.py                  # Phase 3: Metrics & validation-only threshold sweep
│       └── modeling.py                    # Phase 3: Leakage-safe models, importance & outputs
└── tests/
    ├── test_data_cleaning.py              # Phase 2 strict validation, leakage & sensitivity tests
    ├── test_temporal_validation.py        # Phase 3 chronological split & timestamp-group tests
    ├── test_modeling.py                   # Phase 3 pipeline isolation, training & persistence tests
    └── test_evaluation.py                 # Phase 3 metric, threshold & deliverable tests
```

## Setup & Reproduction (Repository Root)
```bash
uv sync --locked
uv run python -m secom_project.download_data
uv run python -m secom_project.data_cleaning
uv run python -m secom_project.eda
uv run python -m secom_project.modeling
uv run pytest -v
```
