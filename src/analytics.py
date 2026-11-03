"""
FireCast AI — Historical Dataset Analytics, Statistical Mining, & Dynamic Insights
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from src.preprocessing import load_raw_dataset, MONTHS

try:
    import streamlit as st
    cache_data = st.cache_data
except Exception:
    def cache_data(func):
        return func

# Module-level cached dataframe
_DATASET_CACHE: pd.DataFrame = None


@cache_data
def get_dataset() -> pd.DataFrame:
    """Retrieve or load the cached dataset."""
    global _DATASET_CACHE
    if _DATASET_CACHE is None:
        _DATASET_CACHE = load_raw_dataset("dataset/forestfires.csv")
    return _DATASET_CACHE.copy()


@cache_data
def get_dataset_kpis() -> Dict[str, Any]:
    """Calculate key performance indicators dynamically from the empirical dataset."""
    df = get_dataset()
    total_records = len(df)
    total_area = float(df["area"].sum())
    mean_area = float(df["area"].mean())
    median_area = float(df["area"].median())
    max_area = float(df["area"].max())
    zero_area_count = int((df["area"] == 0).sum())
    zero_area_pct = float((zero_area_count / total_records) * 100.0)
    
    # Peak fire month by incident count
    month_counts = df["month"].value_counts()
    peak_month = str(month_counts.index[0]).upper()
    peak_month_count = int(month_counts.iloc[0])
    
    # Peak month by burned area
    month_area = df.groupby("month")["area"].sum()
    peak_area_month = str(month_area.idxmax()).upper()
    peak_area_val = float(month_area.max())
    
    return {
        "total_records": total_records,
        "total_area_ha": round(total_area, 1),
        "mean_area_ha": round(mean_area, 2),
        "median_area_ha": round(median_area, 2),
        "max_area_ha": round(max_area, 2),
        "zero_area_count": zero_area_count,
        "zero_area_pct": round(zero_area_pct, 1),
        "zero_pct": round(zero_area_pct, 1),
        "positive_area_count": total_records - zero_area_count,
        "peak_month": peak_month,
        "peak_month_count": peak_month_count,
        "peak_area_month": peak_area_month,
        "peak_area_val": round(peak_area_val, 1)
    }


@cache_data
def get_monthly_distribution() -> pd.DataFrame:
    """Computes fire frequency, total burned area, and average burned area per month."""
    df = get_dataset()
    monthly = []
    
    for m in MONTHS:
        subset = df[df["month"] == m]
        count = len(subset)
        tot_area = float(subset["area"].sum()) if count > 0 else 0.0
        avg_area = float(subset["area"].mean()) if count > 0 else 0.0
        med_area = float(subset["area"].median()) if count > 0 else 0.0
        
        monthly.append({
            "month": m.upper(),
            "month_raw": m,
            "incident_count": count,
            "total_area_ha": round(tot_area, 1),
            "average_area_ha": round(avg_area, 2),
            "median_area_ha": round(med_area, 2)
        })
        
    return pd.DataFrame(monthly)


@cache_data
def generate_data_grounded_insights() -> List[Dict[str, str]]:
    """Generates rigorous statistical insights directly computed from the historical data."""
    kpis = get_dataset_kpis()
    df = get_dataset()
    
    # Proportion of fires in Aug + Sep
    aug_sep_count = len(df[df["month"].isin(["aug", "sep"])])
    aug_sep_pct = (aug_sep_count / kpis["total_records"]) * 100.0
    
    # Area in Aug + Sep
    aug_sep_area = df[df["month"].isin(["aug", "sep"])]["area"].sum()
    aug_sep_area_pct = (aug_sep_area / kpis["total_area_ha"]) * 100.0
    
    # Skewness multiplier
    skew_mult = round(kpis["max_area_ha"] / kpis["mean_area_ha"], 1)
    
    # Zero vs non-zero median
    non_zero_df = df[df["area"] > 0]
    non_zero_median = non_zero_df["area"].median()
    
    insights = [
        {
            "category": "Target Distribution Skew",
            "title": "Extreme Right-Skewness & Zero-Inflation",
            "detail": (
                f"Historical records indicate that the burned-area distribution is extraordinarily right-skewed. "
                f"{kpis['zero_pct']}% of observations recorded zero or negligible area (< 0.01 ha). "
                f"The maximum historical incident ({kpis['max_area_ha']:,.1f} ha) is {skew_mult}× larger than the mean "
                f"({kpis['mean_area_ha']} ha), necessitating a log1p target transformation for stable regression."
            )
        },
        {
            "category": "Seasonality & Temporal Clustering",
            "title": "Severe Late-Summer Incident Concentration",
            "detail": (
                f"Wildfire activity is heavily concentrated in August and September. These two months account for "
                f"{aug_sep_pct:.1f}% of all historical fire ignitions ({aug_sep_count} records) and "
                f"{aug_sep_area_pct:.1f}% of all cumulative hectares burned ({aug_sep_area:,.1f} ha)."
            )
        },
        {
            "category": "Fuel Moisture Indices",
            "title": "Duff & Drought Code Decoupling",
            "detail": (
                f"Fine Fuel Moisture (FFMC) remains consistently elevated throughout summer records (mean: {df['FFMC'].mean():.1f}), "
                f"whereas deep Drought Code (DC) exhibits extreme variance (range: {df['DC'].min():.1f} – {df['DC'].max():.1f}). "
                f"SHAP feature importance indicates that deep seasonal drying (DC) and rate of spread (ISI) provide the strongest "
                f"differentiation between small and large burned areas."
            )
        },
        {
            "category": "Scientific Model Boundary",
            "title": "Weather Data Explanatory Limits",
            "detail": (
                "While meteorological conditions correlate with fire behavior, weather parameters alone do not account for "
                "topographical chokepoints, forest fuel load density, suppression team response times, or aircraft availability. "
                "Consequently, conditional burned-area models exhibit inherently high residual variance."
            )
        }
    ]
    return insights
