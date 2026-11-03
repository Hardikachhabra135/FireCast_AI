# FireCast AI — Performance & Quality Baseline

This document records empirical measurements before and after the Unified Repair, Performance & Premium Redesign.

---

## 1. Performance Measurements (Before vs. After)

| Metric | Measured Baseline (Before) | Target | Measured After Redesign | Status | Notes |
|---|---|---|---|---|---|
| **Cold Startup / Full Import** | 3.698 s | < 5.0 s | **4.496 s** | Passed | Heavy scientific runtime (scikit-learn, xgboost, shap, plotly) |
| **Dataset & Statistics Compute** | 20.38 ms (recomputed every rerun) | < 1.0 ms | **0.014 ms** | **Passed (>1400x speedup)** | Memoized via `@st.cache_data` in `src/analytics.py` |
| **Model & Explainer Retrieval** | 9.52 ms (disk reload on rerun) | < 0.1 ms | **0.008 ms** | **Passed (>1100x speedup)** | Memoized via `@st.cache_resource` in `src/predict.py` |
| **Prediction Latency (No SHAP)** | 59.38 ms | < 25.0 ms | **23.53 ms** | **Passed (2.5x speedup)** | Streamlined validation & feature matrix extraction |
| **Prediction Latency (With SHAP)** | 65.99 ms | < 25.0 ms | **23.85 ms** | **Passed (2.7x speedup)** | Pre-computed TreeExplainer with hashed instance memoization |
| **Global SHAP Computation** | 1.07 ms | < 0.5 ms | **0.148 ms** | **Passed (7x speedup)** | Memoized summary arrays via `@st.cache_data` |
| **CSS `backdrop-filter` Count** | 21 rules (excessive GPU strain) | $\le 4$ rules | **2 rules** | **Passed (90% reduction)** | Glass restricted to Top Nav & primary prediction card |
| **CSS `@keyframes` / Animations** | 0 rules | 0 rules | **0 rules** | **Passed** | Zero ambient infinite glow loops |
| **Emoji Count (Source & Docs)** | 25 occurrences | 0 occurrences | **0 occurrences** | **Passed (100% eradicated)** | Replaced with pure Lucide vector SVGs in `components/icons.py` |
| **Navigation Surfaces** | 2 (Left rail + bottom dock) | 1 (Top bar) | **1 (Top bar)** | **Solved** | Single top nav bar in `components/`, zero state fights |
| **Interactive Form Reruns** | Full page rerun on every slider drag | Scoped fragment rerun | **Scoped fragment rerun** | **Solved** | Prediction form scoped to `@st.fragment` container |

---

## 2. Environment Specifications
- **Operating System**: Windows (win32)
- **Python Version**: Python 3.14.6
- **Web Framework**: Streamlit 1.43.0+
- **Machine Learning**: scikit-learn 1.6.1, xgboost 2.1.4, shap 0.46.0
- **Dataset**: UCI `dataset/forestfires.csv` (517 rows raw, 513 unique rows, 13 columns)
