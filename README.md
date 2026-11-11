# Smart Manufacturing: Intelligent Process Quality Analysis and Predictive Defect Detection Using Machine Learning

## Project Overview
This project investigates semiconductor manufacturing process quality analysis and predictive defect detection using the **UCI SECOM** dataset ([UCI Machine Learning Repository ID 179](https://archive.ics.uci.edu/dataset/179/secom)).

## Current Phase: Phase 1 — Data Acquisition & Audit
*(Note: No ML models or dashboards are built in this phase.)*

### Project Structure
```text
.
├── pyproject.toml                  # Project metadata and dependencies
├── README.md                       # Project documentation
├── data/
│   └── raw/                        # Official UCI SECOM files (retrieved via script)
├── docs/
│   ├── data_dictionary.md          # Documented & anonymous sensor field dictionary
│   ├── data_dictionary.csv         # Machine-readable field dictionary
│   └── dataset_audit_report.md     # Full Phase 1 audit, timestamp & leakage analysis
├── reports/
│   └── secom_audit_summary.json    # Automated quantitative audit metrics
└── src/
    └── secom_project/
        ├── __init__.py
        ├── download_data.py        # Reproducible UCI SECOM retrieval & checksums
        └── inspect_data.py         # Structural inspection, audit & dictionary builder
```

## Setup & Usage
Using `uv`:
```bash
uv sync
uv run python -m secom_project.download_data
uv run python -m secom_project.inspect_data
```
