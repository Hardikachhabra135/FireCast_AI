"""
FireCast AI — Spatial Glass Plotly Visualization Suite
Designed to sit seamlessly within frosted glass panels with transparent backgrounds
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from theme import get_current_theme_tokens


def get_spatial_glass_theme(theme_mode: str = "dark") -> Dict[str, Any]:
    """Returns base layout styling for transparent frosted glass cards using active theme tokens."""
    t = get_current_theme_tokens(theme_mode)
    return {
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "font": {
            "family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            "color": t["text"],
            "size": 11
        },
        "colorway": [t["accent"], t["ai_purple"], t["accent_2"], t["success"], t["info_blue"], t["danger"]],
        "hoverlabel": {
            "bgcolor": t["surface"],
            "bordercolor": t["accent"],
            "font": {"color": t["text"], "family": "Inter, monospace", "size": 11}
        }
    }


def apply_spatial_chart_theme(fig: go.Figure, title: str = "", height: int = 300, theme_mode: str = "dark") -> go.Figure:
    """Safely applies frosted glass layout to a Plotly figure using active theme tokens."""
    t = get_current_theme_tokens(theme_mode)
    fig.update_layout(
        **get_spatial_glass_theme(theme_mode),
        height=height,
        margin=dict(l=35, r=25, t=40, b=35)
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=13, color=t["text"])))
    fig.update_xaxes(
        gridcolor=t["chart_grid"],
        zerolinecolor=t["chart_axis"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_3"], size=10),
        title_font=dict(color=t["text_2"], size=11)
    )
    fig.update_yaxes(
        gridcolor=t["chart_grid"],
        zerolinecolor=t["chart_axis"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_3"], size=10),
        title_font=dict(color=t["text_2"], size=11)
    )
    return fig


def plot_monthly_fire_dual_axis(df_monthly: pd.DataFrame, theme_mode: str = "dark") -> go.Figure:
    """Renders dual-axis monthly fire frequency and cumulative burned area."""
    t = get_current_theme_tokens(theme_mode)
    fig = go.Figure()

    # Bar: Incident Count
    fig.add_trace(go.Bar(
        x=df_monthly["month"],
        y=df_monthly["incident_count"],
        name="Fire Events",
        marker=dict(
            color="rgba(156, 140, 255, 0.75)",
            line=dict(color="rgba(156, 140, 255, 1)", width=1)
        ),
        yaxis="y",
        hovertemplate="<b>%{x}</b>: %{y} incidents<extra></extra>"
    ))

    # Line: Total Burned Area
    fig.add_trace(go.Scatter(
        x=df_monthly["month"],
        y=df_monthly["total_area_ha"],
        name="Total Area (ha)",
        mode="lines+markers",
        line=dict(color="#FF7138", width=3),
        marker=dict(size=7, color="#FFAD5C", symbol="circle"),
        yaxis="y2",
        hovertemplate="<b>%{x}</b>: %{y:,.1f} ha<extra></extra>"
    ))

    fig.update_layout(
        **get_spatial_glass_theme(theme_mode),
        yaxis=dict(
            title=dict(text="Incidents", font=dict(color=t["ai_purple"], size=11)),
            tickfont=dict(color=t["ai_purple"], size=10),
            gridcolor=t["chart_grid"],
            linecolor=t["chart_axis"],
            rangemode="tozero"
        ),
        yaxis2=dict(
            title=dict(text="Burned Area (ha)", font=dict(color=t["accent"], size=11)),
            tickfont=dict(color=t["accent"], size=10),
            overlaying="y",
            side="right",
            showgrid=False,
            rangemode="tozero",
            range=[0, float(df_monthly["total_area_ha"].max()) * 1.08]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=t["text_2"], size=11)
        ),
        height=340,
        margin=dict(l=35, r=45, t=30, b=30)
    )
    fig.update_xaxes(
        gridcolor=t["chart_grid"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_3"], size=10)
    )
    return fig


def plot_burned_area_distribution(df: pd.DataFrame, log_scale: bool = True, theme_mode: str = "dark") -> go.Figure:
    """Renders distribution of recorded burned areas on transparent glass."""
    t = get_current_theme_tokens(theme_mode)
    fig = go.Figure()
    
    if log_scale:
        data = np.log1p(df["area"])
        x_title = "Burned Area, log scale: ln(area + 1)"
        title_text = "Burned Area Distribution (log1p)"
    else:
        data = df["area"]
        x_title = "Burned Area (Hectares)"
        title_text = "Burned Area Distribution (ha)"

    fig.add_trace(go.Histogram(
        x=data,
        marker=dict(
            color="rgba(255, 113, 56, 0.8)",
            line=dict(color="rgba(255, 173, 92, 0.9)", width=1)
        ),
        nbinsx=25,
        hovertemplate="Range: %{x:.2f}<br>Count: %{y}<extra></extra>"
    ))

    apply_spatial_chart_theme(fig, title="", height=340, theme_mode=theme_mode)
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text="Count", gridcolor=t["chart_grid"])
    return fig


def plot_weather_vs_area(df: pd.DataFrame, var_col: str, var_label: str, theme_mode: str = "dark") -> go.Figure:
    """Bivariate scatter plot of a weather parameter against burned area."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[var_col],
        y=df["area"],
        mode="markers",
        marker=dict(
            size=np.clip(np.log1p(df["area"]) * 4.2, 5, 22),
            color=df["temp"],
            colorscale=[[0, "#55C99A"], [0.5, "#FFAD5C"], [1, "#FF7138"]],
            showscale=False,
            line=dict(color="rgba(255,255,255,0.4)", width=0.5)
        ),
        text=[f"Area: {a:.2f} ha<br>{var_label}: {v}" for a, v in zip(df["area"], df[var_col])],
        hovertemplate="%{text}<extra></extra>"
    ))

    apply_spatial_chart_theme(fig, title=f"{var_label} vs. Historical Burned Area", height=290, theme_mode=theme_mode)
    fig.update_xaxes(title_text=var_label)
    fig.update_yaxes(title_text="Area (ha)")
    return fig


def plot_model_tournament_comparison(all_evaluation: Dict[str, Any], theme_mode: str = "dark") -> go.Figure:
    """Compares benchmark regressors by Test MAE and CV MAE."""
    t = get_current_theme_tokens(theme_mode)
    models = list(all_evaluation.keys())
    test_maes = [all_evaluation[m]["test_metrics"]["MAE"] for m in models]
    cv_maes = [all_evaluation[m]["cv_metrics"]["cv_MAE_mean"] for m in models]
    
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=models,
        x=test_maes,
        name="Test MAE (ha)",
        orientation="h",
        marker=dict(color=t["accent"], line=dict(color=t["accent_2"], width=1)),
        text=[f"{v:.2f} ha" for v in test_maes],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Test MAE: %{x:.3f} ha<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=models,
        x=cv_maes,
        name="5-Fold CV MAE (ha)",
        orientation="h",
        marker=dict(color=t["ai_purple"], line=dict(color=t["ai_purple"], width=1)),
        text=[f"{v:.2f} ha" for v in cv_maes],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>CV MAE: %{x:.3f} ha<extra></extra>"
    ))

    apply_spatial_chart_theme(fig, title="Model Tournament — Error Comparison on True Hectares", height=350, theme_mode=theme_mode)
    fig.update_layout(
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=t["text_2"], size=10)
        )
    )
    fig.update_xaxes(title_text="Mean Absolute Error (ha)")
    return fig


def plot_scenario_comparison_chart(scenarios: List[Dict[str, Any]], theme_mode: str = "dark") -> go.Figure:
    """Side-by-side comparison of multiple user what-if scenarios."""
    names = [s["name"] for s in scenarios]
    areas = [s["pred_result"]["burned_area_ha"] for s in scenarios]
    colors = [s["pred_result"]["severity"]["color"] for s in scenarios]

    fig = go.Figure(go.Bar(
        x=names,
        y=areas,
        marker=dict(
            color=colors,
            line=dict(color="rgba(255,255,255,0.4)", width=1.5)
        ),
        text=[f"{a:,.2f} ha" for a in areas],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Estimated Area: %{y:,.2f} ha<extra></extra>"
    ))

    apply_spatial_chart_theme(fig, title="Scenario Area Estimates (Hectares)", height=280, theme_mode=theme_mode)
    fig.update_yaxes(title_text="Burned Area (ha)")
    return fig


def plot_spatial_fire_distribution(df: pd.DataFrame, theme_mode: str = "dark") -> go.Figure:
    """
    Renders 2D spatial coordinate map of historical wildfire incidents
    across the Montesinho Natural Park spatial grid (X: 1-9, Y: 2-9).
    Bubble size and color reflect burned area magnitude.
    """
    t = get_current_theme_tokens(theme_mode)
    plot_df = df.copy()
    plot_df["log_size"] = np.log1p(plot_df["area"]) * 4 + 6
    plot_df["area_label"] = plot_df["area"].apply(lambda a: f"{a:.1f} ha" if a > 0 else "0 ha (containment)")

    fig = go.Figure(go.Scatter(
        x=plot_df["X"],
        y=plot_df["Y"],
        mode="markers",
        marker=dict(
            size=plot_df["log_size"],
            color=plot_df["area"],
            colorscale=[[0, "#55C99A"], [0.2, "#FFAD5C"], [0.6, "#FF7138"], [1, "#FF4D6D"]],
            showscale=True,
            colorbar=dict(
                title=dict(text="Area (ha)", font=dict(color=t["text_2"], size=10)),
                tickfont=dict(color=t["text_3"], size=9),
                thickness=12,
                len=0.8
            ),
            line=dict(color="rgba(255,255,255,0.4)", width=1),
            opacity=0.85
        ),
        text=plot_df["area_label"],
        customdata=np.stack((plot_df["month"], plot_df["temp"], plot_df["wind"]), axis=-1),
        hovertemplate="<b>Montesinho Grid (%{x}, %{y})</b><br>Burned Area: %{text}<br>Month: %{customdata[0]}<br>Temp: %{customdata[1]}°C | Wind: %{customdata[2]} km/h<extra></extra>"
    ))

    apply_spatial_chart_theme(fig, title="Montesinho Park Spatial Grid Distribution (X vs Y)", height=320, theme_mode=theme_mode)
    fig.update_xaxes(
        title_text="Spatial Coordinate X",
        tickmode="linear",
        tick0=1,
        dtick=1,
        range=[0.5, 9.5]
    )
    fig.update_yaxes(
        title_text="Spatial Coordinate Y",
        tickmode="linear",
        tick0=2,
        dtick=1,
        range=[1.5, 9.5]
    )
    return fig


def plot_weather_conditions_overview(df: pd.DataFrame, theme_mode: str = "dark") -> go.Figure:
    """
    Renders ambient weather conditions overview:
    Air Temperature vs Relative Humidity with points scaled and colored by burned area.
    """
    t = get_current_theme_tokens(theme_mode)
    fig = go.Figure(go.Scatter(
        x=df["temp"],
        y=df["RH"],
        mode="markers",
        marker=dict(
            size=np.clip(np.log1p(df["area"]) * 4.5 + 5, 5, 22),
            color=df["area"],
            colorscale=[[0, "#45C99A"], [0.25, "#FFAD5C"], [0.65, "#FF7138"], [1, "#FF4757"]],
            showscale=False,
            line=dict(color="rgba(255,255,255,0.4)", width=0.8),
            opacity=0.8
        ),
        text=[f"Temp: {t:.1f}°C<br>RH: {rh:.0f}%<br>Burned: {a:.2f} ha" for t, rh, a in zip(df["temp"], df["RH"], df["area"])],
        hovertemplate="%{text}<extra></extra>"
    ))
    apply_spatial_chart_theme(fig, title="", height=340, theme_mode=theme_mode)
    fig.update_xaxes(title_text="Air Temperature (°C)", gridcolor=t["chart_grid"])
    fig.update_yaxes(title_text="Relative Humidity (%)", gridcolor=t["chart_grid"])
    return fig
