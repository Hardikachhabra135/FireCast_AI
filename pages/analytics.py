"""
FireCast AI — Module 03: Risk & Scenario Analytics
Max 2 charts per row, clean units, one-sentence plain explanations, and 4-scenario What-If modeling.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.analytics import get_dataset, get_dataset_kpis, get_monthly_distribution
from src.predict import predict_burned_area
from components import section, html
from components.charts import (
    plot_scenario_comparison_chart,
    plot_monthly_fire_dual_axis,
    plot_burned_area_distribution,
    plot_weather_vs_area,
    plot_spatial_fire_distribution
)
from theme import get_current_theme_colors


def render_analytics_page():
    """Renders Module 03: Risk & Scenario Analytics."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    c = get_current_theme_colors(theme_mode)
    df = get_dataset()
    kpis = get_dataset_kpis()
    df_monthly = get_monthly_distribution()

    section(
        "Risk Analytics & Scenario Simulator",
        "Conduct multi-scenario counterfactual experiments and inspect empirical bivariate correlations against historical burned area."
    )

    tab_sim, tab_bivariate = st.tabs([
        "Multi-Scenario What-If Modeling",
        "Bivariate Meteorological Analysis"
    ])

    with tab_sim:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        sc1, sc2, sc3, sc4 = st.columns(4, gap="medium")

        with sc1:
            with st.container(border=True):
                st.markdown(html(f"""<div style="color:{c['success']};font-weight:700;font-size:0.8rem;text-transform:uppercase;margin-bottom:0.6rem;">
Scenario A (Baseline)
</div>"""), unsafe_allow_html=True)
                s_a_x = st.slider("X (A)", 1, 9, 7, key="sa_x")
                s_a_y = st.slider("Y (A)", 2, 9, 5, key="sa_y")
                s_a_month = st.selectbox("Month (A)", ["aug", "sep", "jul", "jun", "oct"], index=0, key="sa_month")
                s_a_temp = st.slider("Temp (°C) (A)", 10.0, 40.0, 24.0, 0.5, key="sa_temp")
                s_a_rh = st.slider("Humidity (%) (A)", 10.0, 90.0, 45.0, 1.0, key="sa_rh")
                s_a_wind = st.slider("Wind (km/h) (A)", 1.0, 15.0, 4.0, 0.5, key="sa_wind")

        with sc2:
            with st.container(border=True):
                st.markdown(html(f"""<div style="color:{c['accent_2']};font-weight:700;font-size:0.8rem;text-transform:uppercase;margin-bottom:0.6rem;">
Scenario B (Heatwave Spike)
</div>"""), unsafe_allow_html=True)
                s_b_x = st.slider("X (B)", 1, 9, 7, key="sb_x")
                s_b_y = st.slider("Y (B)", 2, 9, 5, key="sb_y")
                s_b_month = st.selectbox("Month (B)", ["aug", "sep", "jul", "jun", "oct"], index=0, key="sb_month")
                s_b_temp = st.slider("Temp (°C) (B)", 10.0, 40.0, 31.0, 0.5, key="sb_temp")
                s_b_rh = st.slider("Humidity (%) (B)", 10.0, 90.0, 25.0, 1.0, key="sb_rh")
                s_b_wind = st.slider("Wind (km/h) (B)", 1.0, 15.0, 6.0, 0.5, key="sb_wind")

        with sc3:
            with st.container(border=True):
                st.markdown(html(f"""<div style="color:{c['accent']};font-weight:700;font-size:0.8rem;text-transform:uppercase;margin-bottom:0.6rem;">
Scenario C (Extreme Wind)
</div>"""), unsafe_allow_html=True)
                s_c_x = st.slider("X (C)", 1, 9, 7, key="sc_x")
                s_c_y = st.slider("Y (C)", 2, 9, 5, key="sc_y")
                s_c_month = st.selectbox("Month (C)", ["aug", "sep", "jul", "jun", "oct"], index=0, key="sc_month")
                s_c_temp = st.slider("Temp (°C) (C)", 10.0, 40.0, 35.0, 0.5, key="sc_temp")
                s_c_rh = st.slider("Humidity (%) (C)", 10.0, 90.0, 18.0, 1.0, key="sc_rh")
                s_c_wind = st.slider("Wind (km/h) (C)", 1.0, 15.0, 9.5, 0.5, key="sc_wind")

        with sc4:
            with st.container(border=True):
                st.markdown(html(f"""<div style="color:{c['analytics_blue']};font-weight:700;font-size:0.8rem;text-transform:uppercase;margin-bottom:0.6rem;">
Scenario D (Moist / Rain)
</div>"""), unsafe_allow_html=True)
                s_d_x = st.slider("X (D)", 1, 9, 7, key="sd_x")
                s_d_y = st.slider("Y (D)", 2, 9, 5, key="sd_y")
                s_d_month = st.selectbox("Month (D)", ["aug", "sep", "jul", "jun", "oct"], index=0, key="sd_month")
                s_d_temp = st.slider("Temp (°C) (D)", 10.0, 40.0, 18.0, 0.5, key="sd_temp")
                s_d_rh = st.slider("Humidity (%) (D)", 10.0, 90.0, 72.0, 1.0, key="sd_rh")
                s_d_wind = st.slider("Wind (km/h) (D)", 1.0, 15.0, 3.0, 0.5, key="sd_wind")

        # Predictions for all 4 scenarios (all 12 features present)
        p_a = {"X": s_a_x, "Y": s_a_y, "month": s_a_month, "day": "sun", "temp": s_a_temp, "RH": s_a_rh, "wind": s_a_wind, "rain": 0.0, "FFMC": 90.0, "DMC": 100.0, "DC": 600.0, "ISI": 7.0}
        p_b = {"X": s_b_x, "Y": s_b_y, "month": s_b_month, "day": "sun", "temp": s_b_temp, "RH": s_b_rh, "wind": s_b_wind, "rain": 0.0, "FFMC": 93.5, "DMC": 140.0, "DC": 700.0, "ISI": 11.0}
        p_c = {"X": s_c_x, "Y": s_c_y, "month": s_c_month, "day": "sun", "temp": s_c_temp, "RH": s_c_rh, "wind": s_c_wind, "rain": 0.0, "FFMC": 95.0, "DMC": 180.0, "DC": 780.0, "ISI": 15.5}
        p_d = {"X": s_d_x, "Y": s_d_y, "month": s_d_month, "day": "sun", "temp": s_d_temp, "RH": s_d_rh, "wind": s_d_wind, "rain": 1.5, "FFMC": 82.0, "DMC": 60.0, "DC": 400.0, "ISI": 3.0}

        res_a = predict_burned_area(p_a, include_shap=False)
        res_b = predict_burned_area(p_b, include_shap=False)
        res_c = predict_burned_area(p_c, include_shap=False)
        res_d = predict_burned_area(p_d, include_shap=False)

        scenarios = [
            {"name": "Scenario A (Baseline)", "pred_result": res_a},
            {"name": "Scenario B (Heatwave)", "pred_result": res_b},
            {"name": "Scenario C (Extreme Wind)", "pred_result": res_c},
            {"name": "Scenario D (Moist / Rain)", "pred_result": res_d}
        ]

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
        st.plotly_chart(
            plot_scenario_comparison_chart(scenarios, theme_mode=theme_mode),
            theme=None,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        # Delta comparison table
        delta_b = res_b["burned_area_ha"] - res_a["burned_area_ha"]
        delta_c = res_c["burned_area_ha"] - res_a["burned_area_ha"]
        delta_d = res_d["burned_area_ha"] - res_a["burned_area_ha"]

        comp_df = pd.DataFrame([
            {
                "Scenario": "Scenario A (Baseline)",
                "Location": f"({s_a_x}, {s_a_y})",
                "Temperature": f"{s_a_temp}°C",
                "Humidity": f"{s_a_rh}%",
                "Wind": f"{s_a_wind} km/h",
                "Predicted Area": f"{res_a['burned_area_ha']:.2f} ha",
                "Severity": res_a["severity"]["name"],
                "Shift vs A": "Reference"
            },
            {
                "Scenario": "Scenario B (Heatwave)",
                "Location": f"({s_b_x}, {s_b_y})",
                "Temperature": f"{s_b_temp}°C",
                "Humidity": f"{s_b_rh}%",
                "Wind": f"{s_b_wind} km/h",
                "Predicted Area": f"{res_b['burned_area_ha']:.2f} ha",
                "Severity": res_b["severity"]["name"],
                "Shift vs A": f"{delta_b:+.2f} ha"
            },
            {
                "Scenario": "Scenario C (Extreme Wind)",
                "Location": f"({s_c_x}, {s_c_y})",
                "Temperature": f"{s_c_temp}°C",
                "Humidity": f"{s_c_rh}%",
                "Wind": f"{s_c_wind} km/h",
                "Predicted Area": f"{res_c['burned_area_ha']:.2f} ha",
                "Severity": res_c["severity"]["name"],
                "Shift vs A": f"{delta_c:+.2f} ha"
            },
            {
                "Scenario": "Scenario D (Moist / Rain)",
                "Location": f"({s_d_x}, {s_d_y})",
                "Temperature": f"{s_d_temp}°C",
                "Humidity": f"{s_d_rh}%",
                "Wind": f"{s_d_wind} km/h",
                "Predicted Area": f"{res_d['burned_area_ha']:.2f} ha",
                "Severity": res_d["severity"]["name"],
                "Shift vs A": f"{delta_d:+.2f} ha"
            }
        ])
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    with tab_bivariate:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Row 1: Monthly Bar & Area Histogram (Max 2 per row)
        r1_c1, r1_c2 = st.columns(2, gap="medium")
        with r1_c1:
            st.plotly_chart(
                plot_monthly_fire_dual_axis(df_monthly, theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )
            st.caption("Monthly fire incident counts (bars) and cumulative burned area (line). Units: Incidents / Hectares.")
            
        with r1_c2:
            st.plotly_chart(
                plot_burned_area_distribution(df, log_scale=True, theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )
            st.caption("Log-transformed distribution of fire size illustrating zero-inflation (~48% contained). Units: ln(ha + 1).")

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # Row 2: Temp vs Area & Humidity vs Area (Max 2 per row)
        r2_c1, r2_c2 = st.columns(2, gap="medium")
        with r2_c1:
            st.plotly_chart(
                plot_weather_vs_area(df, "temp", "Temperature (°C)", theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )
            st.caption("Bivariate scatter showing ambient temperature versus burned area. Units: °C vs ha.")
            
        with r2_c2:
            st.plotly_chart(
                plot_weather_vs_area(df, "RH", "Relative Humidity (%)", theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )
            st.caption("Bivariate scatter showing relative atmospheric humidity deficit versus burned area. Units: % vs ha.")

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # Row 3: Wind vs Area & Spatial Distribution (Max 2 per row)
        r3_c1, r3_c2 = st.columns(2, gap="medium")
        with r3_c1:
            st.plotly_chart(
                plot_weather_vs_area(df, "wind", "Wind Speed (km/h)", theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )
            st.caption("Bivariate scatter showing sustained wind speed versus burned area. Units: km/h vs ha.")
            
        with r3_c2:
            st.plotly_chart(
                plot_spatial_fire_distribution(df, theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )
            st.caption("Spatial coordinate distribution across Montesinho Natural Park (X: 1-9, Y: 2-9). Units: Park Coordinates.")
