#  FireCast AI — AI-Powered Wildfire Burned Area Prediction & Intelligence Platform

> **Predict. Understand. Protect.**  
> *A research-grade machine learning intelligence platform developed for wildfire burned-area estimation and explainable environmental analytics.*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4%2B-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/SHAP-Explainable%20AI-8B7CFF)](https://github.com/slundberg/shap)
[![Tests](https://img.shields.io/badge/Tests-22%20Passed-35D39A)](tests/)
[![License](https://img.shields.io/badge/Dataset-UCI%20CC%20BY%204.0-blue)](https://archive.ics.uci.edu/dataset/162/forest+fires)

---

##  Executive Summary

**FireCast AI** is an advanced wildfire intelligence platform engineered to analyze historical meteorological conditions and Canadian Forest Fire Weather Indices (FWI) to estimate potential **burned area in hectares** if a wildfire event occurs.

Trained on the official **UCI Forest Fires Dataset** (*Cortez & Morais, 2007*) recorded in Montesinho Natural Park, Portugal, the platform shifts away from superficial "risk labels" by delivering:
- **True Hectare Regression**: Evaluated on natural hectares via \(\ln(\text{area} + 1)\) (`log1p`) transformation and \(\exp(\hat{y}) - 1\) inversion.
- **Empirical Baseline Benchmarking**: Every model is rigorously compared against **Mean Baseline** and **Median Baseline** regressors under repeated 5-fold cross-validation.
- **Game-Theoretic Explainability (SHAP)**: Global feature importance rankings and local waterfall attribution breakdowns for every individual prediction query.
- **Multi-Scenario Counterfactual Simulation**: Side-by-side what-if modeling to assess environmental sensitivity under changing climate conditions.
- **Dark Intelligence Command Center**: A futuristic, high-density analytics interface inspired by Palantir Foundry and NVIDIA AI operations centers.

> [!IMPORTANT]
> **Core Scientific Principle**: FireCast AI is a **conditional burned-area regression model** (*"if a wildfire ignites, how large might it grow under these conditions?"*). It is **NOT an ignition-probability or fire-detection system**. It does not predict whether a fire will start, guarantee containment, or replace official emergency evacuation orders.

---

## ️ System Architecture & Project Structure

```
FIRECAST AI/
│
├── app.py                             # Main Streamlit command center entrypoint
├── requirements.txt                   # Production dependencies
├── config.yaml                        # Central configuration (ranges, bands, presets)
├── README.md                          # Scientific report & documentation
│
├── dataset/
│   ├── forestfires.csv                # Official UCI Forest Fires dataset (517 rows)
│   └── processed/                     # Stratified train/test splits & SQLite database
│       ├── train.csv                  # 410 training records (79.9%)
│       ├── test.csv                   # 103 held-out test records (20.1%)
│       └── firecast_history.db        # SQLite prediction audit log
│
├── models/
│   ├── best_model.joblib              # Top production regressor pipeline (SVR)
│   ├── preprocessing_pipeline.joblib  # ColumnTransformer (OneHot + RobustScaler)
│   ├── all_models.joblib              # Serialized benchmark model tournament
│   ├── model_metadata.json            # Model architecture, feature schema & quantiles
│   ├── evaluation_metrics.json        # Test & 5-fold CV metrics on true hectares
│   └── shap_explainer.joblib          # SHAP TreeExplainer & background data
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py               # Data loading, stratified log-split, & transformers
│   ├── train.py                       # Training pipeline & repeated CV tournament
│   ├── evaluate.py                    # Evaluation metrics on original hectare scale
│   ├── predict.py                     # Safe inference engine with expm1 inversion
│   ├── explainability.py              # SHAP global summary & local waterfall plots
│   ├── severity.py                    # Non-zero percentile severity bands
│   ├── analytics.py                   # Dynamic dataset mining & insight generation
│   ├── validation.py                  # Pydantic schemas & range boundary guardrails
│   ├── database.py                    # SQLite prediction audit log CRUD
│   ├── reports.py                     # ReportLab PDF executive report generator
│   └── utils.py                       # Plotly dark theme templates & helpers
│
├── components/
│   ├── sidebar.py                     # Navigation & system telemetry sidebar
│   ├── metric_cards.py                # Glassmorphic KPI cards with accent glows
│   └── charts.py                      # Reusable Plotly chart suite
│
├── pages/
│   ├── overview.py                    # Module 01: Overview / Command Center
│   ├── prediction.py                  # Module 02: Fire Prediction Lab
│   ├── analytics.py                   # Module 03: Risk & Scenario Analytics (What-If)
│   ├── explainability.py              # Module 04: Explainable AI Lab (SHAP)
│   ├── performance.py                 # Module 05: Model Performance Center
│   └── history.py                     # Module 06: Prediction Audit Log
│
├── assets/
│   ├── custom.css                     # Dark Intelligence CSS design system
│   └── logo.svg                       # Geometric vector brand logo
│
└── tests/
    ├── test_dataset.py                # UCI dataset integrity & schema tests
    ├── test_preprocessing.py          # Log1p transformation & encoder tests
    ├── test_validation.py             # Pydantic schemas & range validator tests
    ├── test_prediction.py             # Inference pipeline & non-negative bounds
    ├── test_severity.py               # Severity classification threshold tests
    ├── test_database.py               # SQLite CRUD persistence tests
    └── test_reports.py                # PDF generation tests
```

---

##  Dataset Context & Target Characteristics

The system is trained on the official **UCI Forest Fires Dataset** (*Paulo Cortez and Aníbal de Morais, 2007*), collected from **Montesinho Natural Park, Portugal** (Jan 2000 – Dec 2003):

| Metric | Empirical Dataset Value |
| :--- | :--- |
| **Total Records** | 517 observations (513 unique clean records) |
| **Total Cumulative Burned Area** | 6,698.8 hectares |
| **Mean Burned Area** | 12.85 ha |
| **Median Burned Area** | 0.52 ha |
| **Maximum Single Fire** | 1,090.84 ha (Single extreme anomaly) |
| **Zero-Area Fires (\(< 0.01\text{ ha}\))** | 247 records (47.8%) |
| **Peak Wildfire Months** | August & September (74.3% of total fire events) |

### Target Transformation
Because the target distribution is heavily zero-inflated and right-skewed across several orders of magnitude:
\[
y_{\text{train}} = \ln(\text{area} + 1)
\]
Inference estimates are transformed back to the physical hectare scale:
\[
\hat{y}_{\text{ha}} = \max\left(0.0, \, \exp(\hat{y}_{\text{log}}) - 1\right)
\]

---

##  Model Tournament Benchmark Results

All models were evaluated on the **held-out stratified test set (103 observations, 20.1%)** and cross-validated using **Repeated 5-Fold Cross-Validation (3 repeats = 15 folds)**. All metrics are computed **strictly on original hectares**:

| Model Architecture | Test MAE (ha) | Test MedAE (ha) | Test RMSE (ha) | Test \(R^2\) | 5-Fold CV MAE (ha) | Inference Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Support Vector Regressor (SVR) ** | **11.028 ha** | **1.452 ha** | 23.951 ha | -0.061 | **13.308 ± 7.375 ha** | **0.85 ms** |
| **Median Dummy Baseline** | 11.052 ha | 0.580 ha | 24.120 ha | -0.076 | 13.343 ± 7.353 ha | 0.12 ms |
| **Ridge Regression (\(\alpha=10\))** | 11.141 ha | 2.215 ha | 24.103 ha | -0.075 | 13.429 ± 7.338 ha | 0.42 ms |
| **Random Forest Regressor** | 11.151 ha | 2.007 ha | 24.180 ha | -0.082 | 13.499 ± 7.359 ha | 2.10 ms |
| **Mean Dummy Baseline** | 11.224 ha | 2.034 ha | 24.150 ha | -0.079 | 13.475 ± 7.321 ha | 0.11 ms |
| **Gradient Boosting Regressor** | 11.162 ha | 2.026 ha | 24.185 ha | -0.082 | 13.677 ± 7.464 ha | 1.45 ms |
| **XGBoost Regressor** | 11.162 ha | 2.172 ha | 24.190 ha | -0.083 | 13.563 ± 7.371 ha | 1.80 ms |

> [!NOTE]
> **Scientific Transparency Regarding \(R^2\)**:  
> As documented by *Cortez & Morais (2007)*, predicting exact burned area purely from weather stations yields \(R^2 \approx 0\) on held-out test data because weather alone does not capture firefighter suppression response times, aircraft availability, fuel bed depth, or canyon topography.  
> **Any platform claiming "95% accuracy" for burned-area regression on this dataset is overfitting or misrepresenting classification accuracy.** FireCast AI transparently reports MAE and Median AE against dummy baselines.

---

## ️ Severity Classification Bands

Bands are derived from empirical percentiles of **non-zero wildfire events** in Montesinho Park:

| Severity Level | Burned Area Range | Empirical Grounding | Physical Interpretation |
| :--- | :---: | :--- | :--- |
| **Low Severity** | \(0.0 - 2.5\text{ ha}\) | \(< 50\text{th percentile}\) | Surface burn; minimal flank spread; rapid direct containment. |
| **Moderate Severity** | \(2.5 - 10.0\text{ ha}\) | \(50\text{th} - 75\text{th percentile}\) | Medium flame length; flank expansion in dry forest fuel beds. |
| **High Severity** | \(10.0 - 35.0\text{ ha}\) | \(75\text{th} - 90\text{th percentile}\) | Substantial perimeter expansion; high resistance to direct containment. |
| **Extreme Severity** | \(\ge 35.0\text{ ha}\) | \(\ge 90\text{th percentile}\) | Crown fire potential; rapid spotting; major multi-sector mobilization. |

---

##  Quickstart & Installation

### 1. Prerequisites
- Python 3.11, 3.12, or 3.14+
- Pip package manager

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-org/firecast-ai.git
cd firecast-ai
pip install -r requirements.txt
```

### 3. Run Automated Tests
Execute the 22 automated unit and integration tests:
```bash
python -m pytest tests/ -v
```

### 4. Launch the Command Center
Start the Streamlit application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

##  Intelligence Modules Overview

1. **️ Overview / Command Center**:
   Real-time dataset KPIs, dual-axis monthly fire frequencies vs burned area, bivariate weather correlation explorer, and data-grounded insights.
2. ** Fire Prediction Lab**:
   Interactive telemetry sliders for Meteorological parameters and Canadian Fire Weather Indices (FFMC, DMC, DC, ISI), environmental presets, sub-millisecond inference, dynamic severity badge, local SHAP waterfall attribution, and PDF report export.
3. ** Risk & Scenario Analytics (What-If Simulator)**:
   Counterfactual side-by-side scenario modeling (e.g. Baseline vs Heatwave vs Extreme Wind) and multivariate historical filtering with severity donut charts.
4. ** Explainable AI Lab (SHAP)**:
   Global feature importance rankings (\(\mathbb{E}[|\phi_i|]\)), interactive individual test event waterfall charts, and comprehensive guide on Canadian FWI fuel physics.
5. ** Model Performance Center**:
   Full tournament benchmark comparison, actual vs. predicted scatter plots, residual distribution histograms, and peer-reviewed scientific honesty notice.
6. ** Audit Log & History**:
   Persistent SQLite prediction tracking, multi-variable filtering, CSV export, and record management.

---

##  Development Team — "We Do It"

- **Hardika Chhabra** — Lead Architecture & ML Engineering
- **Ankur** — Data Engineering & Preprocessing
- **Ritikarsh Kumar** — Model Evaluation & Diagnostics
- **Swarup Dutta** — Frontend UX & Design Systems

---

## ️ Scientific Disclaimer

FireCast AI is a research and educational platform. Meteorological parameters alone explain only a portion of fire growth; topography, fuel loads, and initial-attack suppression times govern wildfire progression. Never use this system as a sole basis for life-safety or emergency evacuation decisions.
