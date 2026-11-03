"""
FireCast AI — Module 04: Explain AI (SHAP Interpretability)
Explains model decisions using cooperative game theory (SHAP).
Includes global feature importance, positive vs. negative drivers, local waterfall, and physical causality disclaimer.
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.explainability import (
    get_global_feature_importance,
    create_global_importance_chart,
    create_waterfall_chart
)
from src.predict import predict_burned_area
from components import section, html
from components.charts import get_spatial_glass_theme
from theme import get_current_theme_colors


def render_explainability_page():
    """Renders Module 04: Explain AI."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    c = get_current_theme_colors(theme_mode)

    section(
        "Why Did the AI Make This Prediction?",
        "Inspect how atmospheric and fuel parameters mathematically drive model burned-area estimates relative to historical baseline expected values."
    )

    tab_glob, tab_loc, tab_theory = st.tabs([
        "Global Feature Importance",
        "Local Instance Attribution",
        "Fuel Moisture Physics"
    ])

    with tab_glob:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        g_c1, g_c2 = st.columns([1.6, 1.1], gap="medium")
        with g_c1:
            fig_g = create_global_importance_chart(top_n=10, theme_mode=theme_mode)
            st.plotly_chart(fig_g, theme=None, use_container_width=True, config={"displayModeBar": False})

        with g_c2:
            st.markdown(html(f"""<div style="font-size:0.78rem;font-weight:700;color:{c['ai_purple']};text-transform:uppercase;margin-bottom:0.6rem;">
Global Mean |SHAP| Attribution
</div>"""), unsafe_allow_html=True)
            df_imp = get_global_feature_importance().head(10).rename(columns={"MeanAbsSHAP": "Mean |SHAP|"})
            st.dataframe(df_imp[["Feature", "Mean |SHAP|"]], use_container_width=True, height=280, hide_index=True)

    with tab_loc:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        test_df = pd.read_csv("dataset/processed/test.csv")
        sample_idx = st.slider("Select Historical Test Incident Index", 0, len(test_df) - 1, 14)
        sample_row = test_df.iloc[sample_idx]

        sample_html = f"""<div class="fc-card" style="padding:0.9rem 1.2rem;margin-bottom:1rem;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;background:{c['card']};border:1px solid {c['card_border']};">
<b>Incident #{sample_idx}:</b> Grid ({sample_row.get('X', 7)}, {sample_row.get('Y', 5)}) &nbsp;|&nbsp; 
Month: {str(sample_row['month']).upper()} &nbsp;|&nbsp; 
Temp: {sample_row['temp']}°C &nbsp;|&nbsp; 
RH: {sample_row['RH']}% &nbsp;|&nbsp; 
Wind: {sample_row['wind']} km/h &nbsp;|&nbsp; 
FFMC: {sample_row['FFMC']} &nbsp;|&nbsp; 
<b style="color:{c['accent']};">Actual Burned: {sample_row['area']:.2f} ha</b>
</div>"""
        st.markdown(html(sample_html), unsafe_allow_html=True)

        res_loc = predict_burned_area(sample_row.to_dict(), include_shap=True)

        w_col1, w_col2 = st.columns([1.5, 1.1], gap="medium")
        with w_col1:
            if res_loc.get("shap_explanation"):
                wf_fig = create_waterfall_chart(res_loc["shap_explanation"], theme_mode=theme_mode)
                st.plotly_chart(wf_fig, theme=None, use_container_width=True, config={"displayModeBar": False})

        with w_col2:
            st.markdown(html(f"""<div style="font-size:0.78rem;font-weight:700;color:{c['accent']};text-transform:uppercase;margin-bottom:0.6rem;">
Top Drivers Summary
</div>"""), unsafe_allow_html=True)
            shap_info = res_loc.get("shap_explanation", {})
            if "contributions" in shap_info:
                df_c = pd.DataFrame(shap_info["contributions"][:6])[["feature", "shap_value", "direction"]]
                df_c = df_c.rename(columns={"feature": "Parameter", "shap_value": "SHAP", "direction": "Effect"})
                st.dataframe(df_c, use_container_width=True, hide_index=True)

    with tab_theory:
        theory_html = f"""<div class="fc-card" style="padding:1.4rem;background:{c['card']};border:1px solid {c['card_border']};">
<h4 style="color:{c['accent_2']};font-size:1.05rem;margin-top:0;font-family:'Space Grotesk',sans-serif;">
Canadian Forest Fire Weather Index (FWI) Physical Strata
</h4>
<p style="font-size:0.85rem;color:{c['text_2']};line-height:1.6;">
The Canadian FWI System used in the Montesinho study models moisture across distinct forest fuel strata:
</p>
<ul style="font-size:0.85rem;color:{c['text_2']};line-height:1.6;">
<li><b>Fine Fuel Moisture Code (FFMC)</b>: Surface litter moisture (1–2 cm). Governs flame ignition ease.</li>
<li><b>Duff Moisture Code (DMC)</b>: Loosely compacted organic duff (5–10 cm). Captures moderate drying cycles.</li>
<li><b>Drought Code (DC)</b>: Deep compacted organic layer (10–20 cm). Indicates prolonged seasonal drought.</li>
<li><b>Initial Spread Index (ISI)</b>: Combines wind speed and surface fuel dryness to estimate forward spread velocity.</li>
</ul>
</div>"""
        st.markdown(html(theory_html), unsafe_allow_html=True)

    # Required Causality Disclaimer
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    disclaimer_html = f"""<div style="background:{c['surface']};border-left:3px solid {c['ai_purple']};border-radius:6px;padding:0.9rem 1.2rem;font-size:0.82rem;color:{c['text_2']};line-height:1.5;">
<b style="color:{c['text']};">Causality Note:</b> SHAP explains the model's mathematical behavior, not physical fire causation. A positive SHAP value indicates that a feature drove the model's logarithmic estimate upward relative to the training baseline, but local terrain topography and firefighting suppression dictate physical fire growth.
</div>"""
    st.markdown(html(disclaimer_html), unsafe_allow_html=True)
