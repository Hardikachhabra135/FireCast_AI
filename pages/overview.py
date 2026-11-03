"""
FireCast AI — Module 01: Wildfire Intelligence Dashboard
iOS / visionOS Bento Layout:
- Strict 8-pt Bento grid alignment (Row A Hero, Row B 4-Card Grid, Row C 8:4 Charts, Row D 8:4 Charts & Insights)
- Equal-height CSS Grid cards (+/-0px height deviation)
- Full-page theming with dynamic CSS custom properties
"""

import os
import json
import streamlit as st
import pandas as pd
from src.analytics import get_dataset, get_dataset_kpis, get_monthly_distribution
from components import (
    render_metric_grid,
    bento_card_header,
    insight_list,
    html
)
from components.charts import (
    plot_monthly_fire_dual_axis,
    plot_burned_area_distribution,
    plot_weather_conditions_overview
)
from components.icons import get_lucide_svg
from theme import get_current_theme_tokens


def render_overview_page():
    """Renders Module 01: Wildfire Intelligence Dashboard in Bento layout."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    t = get_current_theme_tokens(theme_mode)

    # 1. Load Data & Compute Dynamic KPIs (Cached)
    df = get_dataset()
    kpis = get_dataset_kpis()
    df_monthly = get_monthly_distribution()

    # Load active model metadata dynamically
    model_name_display = "Gradient Boosting"
    test_mae_display = "11.11 ha"
    if os.path.exists("models/model_metadata.json"):
        try:
            with open("models/model_metadata.json", "r", encoding="utf-8") as f:
                meta = json.load(f)
                model_name_display = meta.get("model_name", model_name_display).replace(" Regressor", "")
                test_mae = meta.get("best_metrics", {}).get("test_metrics", {}).get("MAE", 11.11)
                test_mae_display = f"{test_mae:.2f} ha"
        except Exception:
            pass

    # 2. Row A: Hero Section with Aligned CTA & Footnote Chip
    h_col1, h_col2 = st.columns([3.5, 1.2], gap="medium")
    with h_col1:
        map_pin_svg = get_lucide_svg("MapPin", size=14, color="var(--fc-accent)", stroke_width=1.75)
        hero_html = f"""<div style="margin-bottom:1.25rem;">
<div style="display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;background:var(--fc-accent-tint);border:1px solid var(--fc-hairline);margin-bottom:0.6rem;">
{map_pin_svg}
<span style="font-size:0.8rem;font-weight:600;color:var(--fc-accent);">Montesinho Natural Park · historical dataset</span>
</div>
<h1 class="fc-large-title">
Wildfire Intelligence Dashboard
</h1>
<div class="fc-body" style="color:var(--fc-text-2);margin-top:0.35rem;max-width:820px;">
Historical empirical analysis and burned area prediction calibrated on Portuguese forest fire observations.
</div>
</div>"""
        st.markdown(html(hero_html), unsafe_allow_html=True)

    with h_col2:
        st.markdown("<div style='height: 1.6rem;'></div>", unsafe_allow_html=True)
        if st.button("Start Prediction", use_container_width=True, type="primary"):
            st.session_state["page"] = "Prediction"
            st.rerun()

    # 3. Row B: Four Core Metric Cards in CSS Grid (100% Equal Height +/-0px)
    cards_data = [
        {
            "label": "Fire records",
            "value": f"{kpis['total_records']}",
            "context": f"{kpis['positive_area_count']} burned, {kpis['zero_area_count']} contained",
            "badge": "Deduplicated",
            "icon_name": "Database",
            "icon_color": "var(--fc-info-blue)"
        },
        {
            "label": "Total burned area",
            "value": f"{kpis['total_area_ha']:,.1f} ha",
            "context": "Cumulative burned surface",
            "badge": "Empirical",
            "icon_name": "Flame",
            "icon_color": "var(--fc-accent)"
        },
        {
            "label": "Average burned area",
            "value": f"{kpis['mean_area_ha']:.2f} ha",
            "context": f"Median: {kpis['median_area_ha']:.2f} ha (skewed)",
            "badge": "Historical",
            "icon_name": "Target",
            "icon_color": "var(--fc-accent-2)"
        },
        {
            "label": "AI model",
            "value": model_name_display,
            "context": f"Test MAE: {test_mae_display}",
            "badge": "Champion",
            "icon_name": "BrainCircuit",
            "icon_color": "var(--fc-ai-purple)"
        }
    ]
    render_metric_grid(cards_data)

    # 4. Row C: Bento Charts (8:4 Desktop Split)
    c_row1_1, c_row1_2 = st.columns([8, 4], gap="large")
    with c_row1_1:
        with st.container(border=True):
            st.markdown(
                bento_card_header(
                    "Monthly Fire Activity",
                    "Incident frequency and cumulative burned surface across seasonal regimes",
                    badge="Seasonal"
                ),
                unsafe_allow_html=True
            )
            st.plotly_chart(
                plot_monthly_fire_dual_axis(df_monthly, theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with c_row1_2:
        with st.container(border=True):
            st.markdown(
                bento_card_header(
                    "Burned Area Distribution",
                    "Right-skewed fire size frequency shown on log scale",
                    badge="Distribution"
                ),
                unsafe_allow_html=True
            )
            st.plotly_chart(
                plot_burned_area_distribution(df, log_scale=True, theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 5. Row D: Bento Charts & iOS Grouped Insights (8:4 Desktop Split)
    c_row2_1, c_row2_2 = st.columns([8, 4], gap="large")
    with c_row2_1:
        with st.container(border=True):
            st.markdown(
                bento_card_header(
                    "Weather Conditions Overview",
                    "Air temperature vs relative humidity with bubble radius reflecting burned area",
                    badge="Meteorology"
                ),
                unsafe_allow_html=True
            )
            st.plotly_chart(
                plot_weather_conditions_overview(df, theme_mode=theme_mode),
                theme=None,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with c_row2_2:
        # Key empirical insights computed directly from dataset
        aug_sep_count = int(len(df[df["month"].isin(["aug", "sep"])]))
        aug_sep_pct = float((aug_sep_count / kpis["total_records"]) * 100.0)
        aug_sep_area = float(df[df["month"].isin(["aug", "sep"])]["area"].sum())
        aug_sep_area_pct = float((aug_sep_area / kpis["total_area_ha"]) * 100.0)
        skew_mult = round(kpis["max_area_ha"] / kpis["mean_area_ha"], 1)

        insights = [
            {
                "title": f"{kpis['zero_area_pct']}% Containment Preponderance",
                "text": f"Almost half of recorded ignitions ({kpis['zero_area_count']} of {kpis['total_records']}) were contained at 0.0 ha prior to perimeter expansion.",
                "icon": "ShieldCheck",
                "color": "var(--fc-success)"
            },
            {
                "title": f"Late Summer Peak ({kpis['peak_month'].upper()})",
                "text": f"August and September represent {aug_sep_pct:.1f}% of ignitions and {aug_sep_area_pct:.1f}% of cumulative burned surface area.",
                "icon": "Flame",
                "color": "var(--fc-accent)"
            },
            {
                "title": f"Extreme Right-Skew ({skew_mult}x Peak Multiplier)",
                "text": f"Peak fire ({kpis['max_area_ha']:.1f} ha) exceeds the mean ({kpis['mean_area_ha']:.1f} ha) by {skew_mult}x, warranting log1p model stabilization.",
                "icon": "Target",
                "color": "var(--fc-accent-2)"
            }
        ]
        insight_list(insights)

    st.markdown("<div style='height: 1.4rem;'></div>", unsafe_allow_html=True)

    # 6. Scientific Scope Note Card
    disclaimer_html = f"""<div style="background:var(--fc-surface);border-left:3px solid var(--fc-accent);border-radius:var(--fc-radius-control);padding:0.9rem 1.25rem;font-size:0.85rem;color:var(--fc-text-2);line-height:1.5;border:1px solid var(--fc-hairline);border-left:3px solid var(--fc-accent);">
<b style="color:var(--fc-text);">Scientific Note:</b> FireCast AI estimates potential burned area conditional upon fire occurrence under specified atmospheric conditions. It is not an ignition probability model and cannot predict whether a wildfire will start or replace official civil protection alarms.
</div>"""
    st.markdown(html(disclaimer_html), unsafe_allow_html=True)
