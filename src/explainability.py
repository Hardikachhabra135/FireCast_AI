"""
FireCast AI — Explainable AI (XAI) Engine with SHAP Global & Local Interpretability
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from src.utils import logger, get_plotly_theme

try:
    import streamlit as st
    cache_resource = st.cache_resource
    cache_data = st.cache_data
except Exception:
    def cache_resource(func):
        return func
    def cache_data(func):
        return func

_SHAP_CACHE: Optional[Dict[str, Any]] = None
_PREPROCESSOR_CACHE: Optional[Any] = None
_INSTANCE_CACHE: Dict[str, Dict[str, Any]] = {}


@cache_resource
def get_cached_shap_artifacts() -> Dict[str, Any]:
    """Load and cache the serialized SHAP explainer and background data."""
    global _SHAP_CACHE
    if _SHAP_CACHE is None:
        path = "models/shap_explainer.joblib"
        if not os.path.exists(path):
            raise FileNotFoundError(f"SHAP artifact not found at {path}. Run training first.")
        _SHAP_CACHE = joblib.load(path)
    return _SHAP_CACHE


@cache_resource
def get_cached_preprocessor():
    """Load and cache the fitted ColumnTransformer pipeline."""
    global _PREPROCESSOR_CACHE
    if _PREPROCESSOR_CACHE is None:
        path = "models/preprocessing_pipeline.joblib"
        _PREPROCESSOR_CACHE = joblib.load(path)
    return _PREPROCESSOR_CACHE


def clean_feature_label(name: str) -> str:
    """Format technical transformed feature names into clean, readable labels."""
    name = name.replace("cat__month_", "Month: ").replace("cat__day_", "Day: ").replace("num__", "")
    mapping = {
        "X": "Spatial Coordinate X",
        "Y": "Spatial Coordinate Y",
        "temp": "Temperature (°C)",
        "RH": "Relative Humidity (%)",
        "wind": "Wind Speed (km/h)",
        "rain": "Outside Rainfall (mm)",
        "FFMC": "Fine Fuel Moisture Code (FFMC)",
        "DMC": "Duff Moisture Code (DMC)",
        "DC": "Drought Code (DC)",
        "ISI": "Initial Spread Index (ISI)"
    }
    return mapping.get(name, name.title())


def compute_instance_shap(row_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes local SHAP explanation for an individual prediction using TreeExplainer.
    Returns feature contributions, base expected value, and directional breakdown.
    Caches results by row hash.
    """
    global _INSTANCE_CACHE
    cache_key = str(row_df.to_dict(orient="records")[0])
    if cache_key in _INSTANCE_CACHE:
        return _INSTANCE_CACHE[cache_key]
    artifacts = get_cached_shap_artifacts()
    preprocessor = get_cached_preprocessor()
    
    explainer = artifacts.get("tree_explainer", artifacts.get("explainer"))
    feature_names = artifacts["feature_names"]
    
    # Preprocess instance
    X_trans = preprocessor.transform(row_df)
    
    # Compute SHAP Explanation object
    explanation = explainer(X_trans)
    
    base_val = float(explanation.base_values[0])
    shap_vals = explanation.values[0]
    raw_vals = X_trans[0]
    
    contributions = []
    for f_name, s_val, r_val in zip(feature_names, shap_vals, raw_vals):
        clean_lbl = clean_feature_label(f_name)
        # Skip zero-valued one-hot month indicators that have zero contribution
        if "Month: " in clean_lbl and abs(s_val) < 1e-4:
            continue
            
        contributions.append({
            "feature": clean_lbl,
            "raw_feature": f_name,
            "shap_value": float(s_val),
            "abs_shap": float(abs(s_val)),
            "transformed_value": float(r_val),
            "direction": "Increases Burned Area" if s_val > 0 else "Decreases Burned Area"
        })
        
    contributions = sorted(contributions, key=lambda x: x["abs_shap"], reverse=True)
    
    # Top features
    top_positive = [c for c in contributions if c["shap_value"] > 0][:4]
    top_negative = [c for c in contributions if c["shap_value"] < 0][:4]
    
    res = {
        "base_value_log": round(base_val, 4),
        "prediction_log": round(float(base_val + np.sum(shap_vals)), 4),
        "contributions": contributions,
        "top_positive": top_positive,
        "top_negative": top_negative,
        "explainer_model": artifacts.get("model_name", "Random Forest Regressor")
    }
    _INSTANCE_CACHE[cache_key] = res
    return res


@cache_data
def get_global_feature_importance() -> pd.DataFrame:
    """Returns global mean absolute SHAP value ranking across all features."""
    artifacts = get_cached_shap_artifacts()
    global_shap = artifacts.get("global_shap_values")
    feature_names = artifacts["feature_names"]
    
    if global_shap is not None:
        mean_abs = np.mean(np.abs(global_shap.values), axis=0)
    else:
        # Fallback to RF feature importances if needed
        rf = artifacts.get("rf_model")
        mean_abs = rf.feature_importances_
        
    records = []
    for name, imp in zip(feature_names, mean_abs):
        records.append({
            "Feature": clean_feature_label(name),
            "RawName": name,
            "MeanAbsSHAP": float(imp)
        })
        
    df_imp = pd.DataFrame(records).sort_values("MeanAbsSHAP", ascending=False).reset_index(drop=True)
    return df_imp


def create_waterfall_chart(shap_info: Dict[str, Any], theme_mode: str = "dark") -> go.Figure:
    """
    Renders a custom Plotly waterfall chart showing how individual inputs
    drive the burned-area estimate away from the baseline Montesinho expected value.
    """
    from theme import get_current_theme_tokens
    t = get_current_theme_tokens(theme_mode)

    contributions = shap_info["contributions"][:8]  # top 8 most influential
    base_val = shap_info["base_value_log"]
    
    features = [c["feature"] for c in contributions][::-1]
    shap_vals = [c["shap_value"] for c in contributions][::-1]
    
    colors = [t["accent"] if val > 0 else t["success"] for val in shap_vals]
    
    fig = go.Figure(go.Bar(
        x=shap_vals,
        y=features,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color=t["hairline"], width=1)
        ),
        text=[f"{val:+.3f}" for val in shap_vals],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>SHAP Contribution: %{x:+.4f} (log-area)<extra></extra>"
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            color=t["text"],
            size=11
        ),
        title=dict(
            text="Local Feature Impact (SHAP Contribution to log(Burned Area))",
            font=dict(size=13, color=t["text"])
        ),
        xaxis_title="SHAP Value (Impact on ln(Area + 1))",
        yaxis_title="",
        height=320,
        margin=dict(l=10, r=40, t=40, b=30)
    )
    fig.update_xaxes(
        gridcolor=t["chart_grid"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_2"], size=10)
    )
    fig.update_yaxes(
        gridcolor=t["chart_grid"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_2"], size=10)
    )
    fig.add_vline(x=0, line_width=1.5, line_color=t["ai_purple"], line_dash="dash")
    return fig


def create_global_importance_chart(top_n: int = 10, theme_mode: str = "dark") -> go.Figure:
    """Renders global feature importance bar chart using mean absolute SHAP values."""
    from theme import get_current_theme_tokens
    t = get_current_theme_tokens(theme_mode)

    df_imp = get_global_feature_importance().head(top_n).iloc[::-1]
    
    fig = go.Figure(go.Bar(
        x=df_imp["MeanAbsSHAP"],
        y=df_imp["Feature"],
        orientation="h",
        marker=dict(
            color=df_imp["MeanAbsSHAP"],
            colorscale=[[0, t["surface"]], [0.5, t["ai_purple"]], [1, t["accent"]]],
            line=dict(color=t["hairline"], width=1)
        ),
        text=[f"{val:.3f}" for val in df_imp["MeanAbsSHAP"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Global Mean |SHAP|: %{x:.4f}<extra></extra>"
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            color=t["text"],
            size=11
        ),
        title=dict(
            text=f"Top {top_n} Global Drivers of Burned Area (Mean |SHAP|)",
            font=dict(size=13, color=t["text"])
        ),
        xaxis_title="Mean |SHAP Value| (Average Log-Hectare Impact)",
        yaxis_title="",
        height=380,
        margin=dict(l=10, r=40, t=40, b=30)
    )
    fig.update_xaxes(
        gridcolor=t["chart_grid"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_2"], size=10)
    )
    fig.update_yaxes(
        gridcolor=t["chart_grid"],
        linecolor=t["chart_axis"],
        tickfont=dict(color=t["text_2"], size=10)
    )
    return fig

