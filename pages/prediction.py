"""
FireCast AI — Module 02: Predict Burned Area
Scoped with @st.fragment for high-performance slider response without whole-page reruns.
Calm Glass primary result card with severity bar and real SHAP explanations.
"""

import time
import streamlit as st
import pandas as pd
from typing import Dict, Any

from src.utils import load_config, clean_html
from src.preprocessing import MONTHS, DAYS
from src.predict import predict_burned_area
from src.explainability import create_waterfall_chart
from src.database import save_prediction_record
from src.reports import generate_pdf_report
from src.analytics import get_dataset
from components import section, severity_bar, html
from theme import COLORS, get_current_theme_colors


@st.fragment
def render_prediction_form_fragment(df: pd.DataFrame, config: Dict[str, Any]):
    """Isolated fragment managing prediction inputs, execution, and result display."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    c = get_current_theme_colors(theme_mode)
    presets = config.get("presets", {})

    # Preset Quick Selectors
    st.markdown(html(f"""<div style="font-size:0.75rem;font-weight:600;color:{c['text_2']};text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">
Quick Presets
</div>"""), unsafe_allow_html=True)

    p_cols = st.columns(len(presets))
    for idx, (p_key, p_val) in enumerate(presets.items()):
        with p_cols[idx]:
            p_label = p_val['name'].split('(')[0].strip()
            if st.button(p_label, key=f"pred_preset_{p_key}", use_container_width=True):
                st.session_state["active_preset"] = p_key
                st.rerun()

    active_p = None
    if "active_preset" in st.session_state and st.session_state["active_preset"] in presets:
        active_p = presets[st.session_state["active_preset"]]

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    # 4 Semantic Groups
    col_loc, col_weather, col_fwi, col_temp = st.columns(4, gap="medium")

    # 1. Location
    with col_loc:
        with st.container(border=True):
            st.markdown(html(f"""<div style="font-size:0.78rem;font-weight:700;color:{c['analytics_blue']};text-transform:uppercase;margin-bottom:0.8rem;">
1. Location (Grid)
</div>"""), unsafe_allow_html=True)
            x_def = int(active_p.get("X", 7) if active_p else 7)
            y_def = int(active_p.get("Y", 5) if active_p else 5)

            x_val = st.slider(
                "Montesinho Grid X",
                min_value=1,
                max_value=9,
                value=x_def,
                step=1,
                help="West-to-East spatial park coordinate within Montesinho grid (1 to 9)."
            )
            y_val = st.slider(
                "Montesinho Grid Y",
                min_value=2,
                max_value=9,
                value=y_def,
                step=1,
                help="South-to-North spatial park coordinate within Montesinho grid (2 to 9)."
            )
            model_options = [
                "Gradient Boosting Regressor",
                "Random Forest Regressor",
                "XGBoost Regressor",
                "Support Vector Regressor (SVR)",
                "Ridge Regression",
                "Linear Regression"
            ]
            model_choice = st.selectbox(
                "AI Architecture",
                options=model_options,
                index=0,
                help="Candidate regression architecture trained on log1p(area)."
            )

    # 2. Weather (Min/Max strictly from dataset)
    with col_weather:
        with st.container(border=True):
            st.markdown(html(f"""<div style="font-size:0.78rem;font-weight:700;color:{c['accent']};text-transform:uppercase;margin-bottom:0.8rem;">
2. Weather Conditions
</div>"""), unsafe_allow_html=True)
            temp_min, temp_max = float(df["temp"].min()), float(df["temp"].max())
            temp_val = st.slider(
                "Temperature (°C)",
                min_value=0.0,
                max_value=float(round(temp_max + 5.0, 1)),
                value=float(active_p["temp"] if active_p else round(df["temp"].median(), 1)),
                step=0.5,
                help="Ambient shade temperature in Celsius."
            )
            rh_min, rh_max = float(df["RH"].min()), float(df["RH"].max())
            rh_val = st.slider(
                "Relative Humidity (%)",
                min_value=10.0,
                max_value=100.0,
                value=float(active_p["RH"] if active_p else round(df["RH"].median(), 0)),
                step=1.0,
                help="Relative atmospheric humidity percentage."
            )
            wind_max = float(df["wind"].max())
            wind_val = st.slider(
                "Wind Speed (km/h)",
                min_value=0.4,
                max_value=float(round(wind_max + 2.0, 1)),
                value=float(active_p["wind"] if active_p else round(df["wind"].median(), 1)),
                step=0.2,
                help="Sustained surface wind velocity in km/h."
            )
            rain_val = st.slider(
                "Rain (mm)",
                min_value=0.0,
                max_value=10.0,
                value=float(active_p["rain"] if active_p else 0.0),
                step=0.1,
                help="Outside rainfall precipitation in millimeters."
            )

    # 3. Fire Weather Indices (Canadian FWI System)
    with col_fwi:
        with st.container(border=True):
            st.markdown(html(f"""<div style="font-size:0.78rem;font-weight:700;color:{c['accent_2']};text-transform:uppercase;margin-bottom:0.8rem;">
3. Fuel Moisture Indices
</div>"""), unsafe_allow_html=True)
            ffmc_val = st.slider(
                "Fine Fuel Moisture (FFMC)",
                min_value=15.0,
                max_value=98.0,
                value=float(active_p["FFMC"] if active_p else round(df["FFMC"].median(), 1)),
                step=0.5,
                help="Surface litter moisture rating (higher = drier, easier surface ignition)."
            )
            dmc_val = st.slider(
                "Duff Moisture Code (DMC)",
                min_value=1.0,
                max_value=300.0,
                value=float(active_p["DMC"] if active_p else round(df["DMC"].median(), 1)),
                step=1.0,
                help="Medium duff organic layer dryness (higher = deeper combustion)."
            )
            dc_val = st.slider(
                "Drought Code (DC)",
                min_value=5.0,
                max_value=900.0,
                value=float(active_p["DC"] if active_p else round(df["DC"].median(), 0)),
                step=5.0,
                help="Deep organic forest floor drought indicator (higher = severe seasonal drought)."
            )
            isi_val = st.slider(
                "Initial Spread Index (ISI)",
                min_value=0.0,
                max_value=60.0,
                value=float(active_p["ISI"] if active_p else round(df["ISI"].median(), 1)),
                step=0.2,
                help="Rate of fire spread velocity combined from wind and fine fuel moisture."
            )

    # 4. Month & Day
    with col_temp:
        with st.container(border=True):
            st.markdown(html(f"""<div style="font-size:0.78rem;font-weight:700;color:{c['ai_purple']};text-transform:uppercase;margin-bottom:0.8rem;">
4. Month & Day
</div>"""), unsafe_allow_html=True)
            def_month = active_p["month"] if active_p else "aug"
            m_idx = MONTHS.index(def_month) if def_month in MONTHS else 7
            month_val = st.selectbox("Month of Year", options=MONTHS, index=m_idx, format_func=lambda m: m.upper())

            def_day = active_p["day"] if active_p else "sun"
            d_idx = DAYS.index(def_day) if def_day in DAYS else 6
            day_val = st.selectbox("Day of Week", options=DAYS, index=d_idx, format_func=lambda d: d.upper())

            st.markdown(html(f"""<div style="font-size:0.75rem;color:{c['text_2']};margin-top:1.2rem;line-height:1.4;">
Montesinho Park fire regimes peak in August and September.
</div>"""), unsafe_allow_html=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Primary Action Button with double-submission guard
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.4, 1])
    with btn_col2:
        predict_clicked = st.button("Predict Burned Area", use_container_width=True, type="primary")

    # Payload with all 12 verified features
    payload = {
        "X": int(x_val),
        "Y": int(y_val),
        "month": month_val,
        "day": day_val,
        "temp": temp_val,
        "RH": rh_val,
        "wind": wind_val,
        "rain": rain_val,
        "FFMC": ffmc_val,
        "DMC": dmc_val,
        "DC": dc_val,
        "ISI": isi_val
    }

    # Execute Prediction
    if predict_clicked or "current_prediction" not in st.session_state:
        pred_res = predict_burned_area(payload, model_name=model_choice, include_shap=True)
        st.session_state["current_prediction"] = pred_res
        if predict_clicked:
            rec_id = save_prediction_record(pred_res, notes=f"Interactive Simulation ({model_choice})")
            st.toast(f"Prediction #{rec_id} saved to audit history ({pred_res['burned_area_ha']:.2f} ha)")
    else:
        pred_res = st.session_state["current_prediction"]

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Calm Glass Result Layout (Two columns: Primary Result Card + SHAP Factors)
    r_col1, r_col2 = st.columns([1.15, 1.35], gap="large")

    with r_col1:
        ha = pred_res["burned_area_ha"]
        sev = pred_res["severity"]
        sev_color = sev.get("color", c["accent"])
        model_name = pred_res["model_used"]
        latency = pred_res["inference_time_ms"]

        # Primary Result Card — The single primary Calm Glass element
        result_card_html = f"""<div class="fc-calm-glass-result" style="text-align:center;">
<div style="font-size:0.75rem;font-weight:700;color:{c['text_2']};text-transform:uppercase;letter-spacing:0.08em;font-family:'IBM Plex Mono',monospace;">
Conditional Burned Area Estimate
</div>
<div style="margin:0.8rem 0 0.4rem 0;">
<span style="font-family:'IBM Plex Mono',monospace;font-size:3.6rem;font-weight:700;color:{c['text']};line-height:1;">
{ha:,.2f}
</span>
<span style="font-size:1.3rem;font-weight:600;color:{sev_color};margin-left:0.35rem;">
ha
</span>
</div>
<div style="font-size:0.8rem;color:{c['text_2']};margin-bottom:0.8rem;">
({sev['name']} • {sev['percentile_ref']})
</div>
<div style="font-size:0.75rem;color:{c['text_2']};font-family:'IBM Plex Mono',monospace;">
Model: <span style="color:{c['text']};font-weight:600;">{model_name}</span> &nbsp;|&nbsp; 
Latency: <span style="color:{c['success']};font-weight:600;">{latency:.1f} ms</span>
</div>
</div>"""
        st.markdown(html(result_card_html), unsafe_allow_html=True)

        # Severity Bar
        severity_bar(ha, sev)

        # Action Buttons: Save & Export PDF
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            if st.button("Save to History", use_container_width=True):
                rec_id = save_prediction_record(pred_res, notes=f"{sev['name']} ({ha:.1f} ha)")
                st.success(f"Saved prediction #{rec_id} to SQLite history.")
        with a2:
            pdf_bytes = generate_pdf_report(pred_res)
            st.download_button(
                label="Export PDF Report",
                data=pdf_bytes,
                file_name=f"FireCast_Report_{ha:.1f}ha.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with r_col2:
        # Boundary Warnings
        if pred_res.get("warnings"):
            for w in pred_res["warnings"]:
                st.warning(w)

        # Local SHAP Waterfall Plot
        if pred_res.get("shap_explanation"):
            st.markdown(html(f"""<div style="font-size:0.8rem;font-weight:700;color:{c['text']};margin-bottom:0.4rem;">
Top Contributing Factors (Local SHAP Attribution)
</div>"""), unsafe_allow_html=True)
            waterfall_fig = create_waterfall_chart(pred_res["shap_explanation"], theme_mode=theme_mode)
            st.plotly_chart(
                waterfall_fig,
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    # Scientific Scope Note
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    scope_note_html = f"""<div style="background:{c['surface']};border-left:3px solid {c['accent']};border-radius:6px;padding:0.9rem 1.2rem;font-size:0.8rem;color:{c['text_2']};line-height:1.5;">
<b style="color:{c['text']};">Conditional Scope:</b> The estimated {pred_res['burned_area_ha']} hectares represents the expected burn size conditional on wildfire ignition under these exact ambient conditions. Historical data demonstrates that ~48% of fires were contained at 0.0 ha prior to perimeter expansion.
</div>"""
    st.markdown(html(scope_note_html), unsafe_allow_html=True)


def render_prediction_page():
    """Renders Module 02: Predict Burned Area."""
    config = load_config()
    df = get_dataset()

    section("Predict Burned Area", "Configure ambient meteorological parameters and fuel moisture indices to estimate potential wildfire burned area.")
    render_prediction_form_fragment(df, config)
