"""
FireCast AI — Module 05: Model Performance Center
Scientific tournament benchmarks on true hectares with plain-language explanations.
"""

import os
import json
import joblib
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.utils import load_config, clean_html
from components import section, metric_card, html
from components.charts import (
    plot_model_tournament_comparison,
    apply_spatial_chart_theme
)
from theme import get_current_theme_colors


def render_performance_page():
    """Renders Module 05: Model Performance Center."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    c = get_current_theme_colors(theme_mode)
    
    # Load serialized evaluation results and metadata
    metrics_path = "models/evaluation_metrics.json"
    meta_path = "models/model_metadata.json"
    
    if not os.path.exists(metrics_path) or not os.path.exists(meta_path):
        st.error("Model performance metrics not found. Please run the training pipeline first.")
        return

    with open(metrics_path, "r", encoding="utf-8") as f:
        all_eval = json.load(f)

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    section(
        "Model Performance Center",
        "Empirical validation metrics evaluated strictly on original natural hectares. Compare candidate algorithms against Mean and Median baselines under repeated 5-fold cross-validation."
    )

    # 1. Champion Model Highlights
    best_name = metadata["model_name"]
    best_metrics = metadata["best_metrics"]["test_metrics"]
    best_cv = metadata["best_metrics"]["cv_metrics"]

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        metric_card(
            label="Selected Model",
            value=best_name.replace(" Regressor", ""),
            context=f"Production champion",
            icon_name="BrainCircuit",
            icon_color=c["ai_purple"],
            badge="ACTIVE"
        )
    with c2:
        metric_card(
            label="Test MAE",
            value=f"{best_metrics['MAE']:.2f} ha",
            context="Average error on test partition",
            icon_name="Target",
            icon_color=c["accent"]
        )
    with c3:
        metric_card(
            label="5-Fold CV MAE",
            value=f"{best_cv['cv_MAE_mean']:.2f} ha",
            context=f"± {best_cv['cv_MAE_std']:.2f} ha (15 repeated folds)",
            icon_name="Activity",
            icon_color=c["analytics_blue"]
        )
    with c4:
        metric_card(
            label="Inference Latency",
            value=f"{best_metrics['latency_ms']:.1f} ms",
            context="Single-event execution speed",
            icon_name="Cpu",
            icon_color=c["success"]
        )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 2. Metric Explanations in Plain English
    exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4, gap="medium")
    with exp_c1:
        st.markdown(html(f"""<div class="fc-card" style="padding:0.9rem;border-radius:8px;font-size:0.75rem;color:{c['text_2']};min-height:90px;">
<b style="color:{c['text']};">Mean Absolute Error (MAE):</b> Average magnitude of error in hectares on the held-out test split, directly interpretable in land area.
</div>"""), unsafe_allow_html=True)
    with exp_c2:
        st.markdown(html(f"""<div class="fc-card" style="padding:0.9rem;border-radius:8px;font-size:0.75rem;color:{c['text_2']};min-height:90px;">
<b style="color:{c['text']};">Root Mean Squared Error (RMSE):</b> Standard deviation of residuals in hectares; penalizes large outlier estimation mistakes more heavily.
</div>"""), unsafe_allow_html=True)
    with exp_c3:
        st.markdown(html(f"""<div class="fc-card" style="padding:0.9rem;border-radius:8px;font-size:0.75rem;color:{c['text_2']};min-height:90px;">
<b style="color:{c['text']};">Coefficient of Determination (R²):</b> Proportion of variance explained by weather alone; near-zero reflects unmodeled tactical suppression.
</div>"""), unsafe_allow_html=True)
    with exp_c4:
        st.markdown(html(f"""<div class="fc-card" style="padding:0.9rem;border-radius:8px;font-size:0.75rem;color:{c['text_2']};min-height:90px;">
<b style="color:{c['text']};">Inference Latency:</b> Real-time single-sample vector transformation and regressor inference speed in milliseconds.
</div>"""), unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Model Tournament Comparison Bar Chart
    st.plotly_chart(
        plot_model_tournament_comparison(all_eval, theme_mode=theme_mode),
        theme=None,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 4. Comprehensive Benchmark Table (With Active Model Flagged)
    section("Empirical Tournament Leaderboard", "All candidate architectures benchmarked on true hectares. Excludes synthetic or unverified scores.")
    
    table_rows = []
    for m_name, m_data in all_eval.items():
        tm = m_data["test_metrics"]
        cvm = m_data["cv_metrics"]
        is_best = (m_name == best_name)
        status_flag = "SELECTED CHAMPION" if is_best else "Candidate"
        table_rows.append({
            "Status": status_flag,
            "Architecture": m_name,
            "Test MAE (ha)": f"{tm['MAE']:.3f}",
            "Test MedAE (ha)": f"{tm['MedAE']:.3f}",
            "Test RMSE (ha)": f"{tm['RMSE']:.3f}",
            "Test R²": f"{tm['R2']:.4f}",
            "5-Fold CV MAE (ha)": f"{cvm['cv_MAE_mean']:.3f} ± {cvm['cv_MAE_std']:.3f}",
            "Inference Latency": f"{tm.get('latency_ms', 0.0):.1f} ms"
        })
    df_table = pd.DataFrame(table_rows).sort_values("Test MAE (ha)").reset_index(drop=True)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 5. Residual Diagnostics
    section("Regression Residual Diagnostics", "Actual vs. Predicted agreement and error distribution for the held-out test partition.")
    
    test_df = pd.read_csv("dataset/processed/test.csv")
    all_pipelines = joblib.load("models/all_models.joblib")
    selected_diag_model = st.selectbox(
        "Select Model Architecture for Residual Diagnostics",
        list(all_pipelines.keys()),
        index=list(all_pipelines.keys()).index(best_name)
    )
    
    pipe = all_pipelines[selected_diag_model]
    feature_cols = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
    pred_log = pipe.predict(test_df[feature_cols])
    pred_ha = np.expm1(pred_log).clip(min=0.0)
    actual_ha = test_df["area"].values
    residuals = actual_ha - pred_ha

    r_col1, r_col2 = st.columns(2, gap="medium")

    with r_col1:
        # Scatter: Actual vs Predicted
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=actual_ha,
            y=pred_ha,
            mode="markers",
            marker=dict(
                size=7,
                color="rgba(255, 113, 56, 0.85)",
                line=dict(color="#FFAD5C", width=1)
            ),
            name="Test Events",
            hovertemplate="Actual: %{x:.2f} ha<br>Predicted: %{y:.2f} ha<extra></extra>"
        ))
        max_val = max(float(np.max(actual_ha)), float(np.max(pred_ha)), 10.0)
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            line=dict(color=c["ai_purple"], dash="dash", width=1.5),
            name="1:1 Perfect Agreement"
        ))
        apply_spatial_chart_theme(fig_scatter, title=f"Actual vs. Predicted ({selected_diag_model})", height=280, theme_mode=theme_mode)
        fig_scatter.update_xaxes(title_text="Actual Burned Area (ha)")
        fig_scatter.update_yaxes(title_text="Predicted Burned Area (ha)")
        st.plotly_chart(fig_scatter, theme=None, use_container_width=True, config={"displayModeBar": False})

    with r_col2:
        # Residual Distribution
        fig_res = go.Figure()
        fig_res.add_trace(go.Histogram(
            x=residuals,
            nbinsx=30,
            marker=dict(
                color="rgba(156, 140, 255, 0.8)",
                line=dict(color=c["ai_purple"], width=1)
            ),
            name="Residuals",
            hovertemplate="Residual: %{x:.2f} ha<br>Count: %{y}<extra></extra>"
        ))
        fig_res.add_vline(x=0, line_width=1.5, line_color=c["success"], line_dash="dash")
        apply_spatial_chart_theme(fig_res, title="Residual Error Distribution", height=280, theme_mode=theme_mode)
        fig_res.update_xaxes(title_text="Residual Error (ha)")
        fig_res.update_yaxes(title_text="Count")
        st.plotly_chart(fig_res, theme=None, use_container_width=True, config={"displayModeBar": False})

    # Scientific Peer-Review Rigor Note
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    honesty_html = f"""<div style="background:{c['surface']};border-left:3px solid {c['accent_2']};border-radius:6px;padding:1.1rem 1.3rem;font-size:0.82rem;color:{c['text_2']};line-height:1.6;">
<div style="font-size:0.8rem;font-weight:700;color:{c['accent_2']};text-transform:uppercase;margin-bottom:0.4rem;">
Peer-Review Methodological Rigor: Why High R² Claims Are Scientifically Unsound
</div>
<p style="margin-top:0;">
In peer-reviewed literature (Cortez & Morais, 2007), predicting forest fire burned area purely from ambient meteorological conditions yields near-zero R² on held-out test splits. Any benchmark claiming <b>"95% accuracy"</b> or high R² on this dataset indicates severe data leakage, evaluating on training data, or conflating regression with classification.
</p>
<p style="margin-bottom:0;">
• <b>Zero-Inflation:</b> ~48% of fires had area = 0.0 ha due to rapid initial attack suppression.<br/>
• <b>Tactical Suppression Variables:</b> Firefighter counts, air tankers, and response times are unrecorded in ambient weather stations.<br/>
• <b>FireCast AI Scientific Standard:</b> Evaluated honestly on original hectares using MAE and MedAE against classical baselines.
</p>
</div>"""
    st.markdown(html(honesty_html), unsafe_allow_html=True)
