"""
FireCast AI — Performance & Redesign Automated Verification Suite
Verifies:
1. Feature schema order: ["X","Y","month","day","FFMC","DMC","DC","ISI","temp","RH","wind","rain"]
2. Prediction output is finite and non-negative.
3. Dashboard statistics exactly equal values recomputed directly from forestfires.csv.
"""

import math
import pytest
import pandas as pd
import numpy as np

from src.preprocessing import ALL_FEATURES, load_raw_dataset
from src.predict import predict_burned_area
from src.analytics import get_dataset_kpis


def test_feature_schema_order():
    """Check 1: Verify exact required feature schema order."""
    expected_features = [
        "X", "Y", "month", "day", "FFMC", "DMC", "DC", "ISI", "temp", "RH", "wind", "rain"
    ]
    assert ALL_FEATURES == expected_features, (
        f"Feature order mismatch! Expected: {expected_features}, got: {ALL_FEATURES}"
    )


def test_prediction_output_finite_and_non_negative():
    """Check 2: Verify prediction output is finite and non-negative across edge inputs."""
    test_cases = [
        # Normal baseline
        {"X": 7, "Y": 5, "month": "aug", "day": "sun", "temp": 24.0, "RH": 45.0, "wind": 4.0, "rain": 0.0, "FFMC": 90.0, "DMC": 100.0, "DC": 600.0, "ISI": 7.0},
        # High extreme
        {"X": 8, "Y": 6, "month": "aug", "day": "sat", "temp": 38.0, "RH": 15.0, "wind": 10.0, "rain": 0.0, "FFMC": 96.0, "DMC": 280.0, "DC": 850.0, "ISI": 25.0},
        # Low extreme
        {"X": 1, "Y": 2, "month": "dec", "day": "fri", "temp": 2.2, "RH": 95.0, "wind": 0.9, "rain": 6.4, "FFMC": 20.0, "DMC": 2.0, "DC": 15.0, "ISI": 0.5},
        # Zero area fire conditions
        {"X": 4, "Y": 4, "month": "mar", "day": "tue", "temp": 12.0, "RH": 65.0, "wind": 2.5, "rain": 0.0, "FFMC": 85.0, "DMC": 40.0, "DC": 300.0, "ISI": 3.0}
    ]

    for tc in test_cases:
        res = predict_burned_area(tc, include_shap=False)
        ha = res["burned_area_ha"]
        assert isinstance(ha, (int, float)), f"Burned area must be numeric, got {type(ha)}"
        assert not math.isnan(ha), "Burned area must not be NaN"
        assert not math.isinf(ha), "Burned area must not be Infinite"
        assert ha >= 0.0, f"Burned area must be non-negative, got {ha}"
        assert res["predicted_log_scale"] is not None


def test_dashboard_stats_equal_csv_recomputation():
    """Check 3: Verify dashboard statistics equal values recomputed directly from the CSV."""
    df_raw = pd.read_csv("dataset/forestfires.csv")
    df_clean = df_raw.drop_duplicates()
    kpis = get_dataset_kpis()

    # Total record count
    assert kpis["total_records"] == len(df_clean), (
        f"Record count mismatch: KPI={kpis['total_records']} vs CSV clean={len(df_clean)}"
    )

    # Cumulative burned area
    expected_sum = round(float(df_clean["area"].sum()), 1)
    assert kpis["total_area_ha"] == expected_sum, (
        f"Total area mismatch: KPI={kpis['total_area_ha']} vs CSV sum={expected_sum}"
    )

    # Mean area
    expected_mean = round(float(df_clean["area"].mean()), 2)
    assert kpis["mean_area_ha"] == expected_mean, (
        f"Mean area mismatch: KPI={kpis['mean_area_ha']} vs CSV mean={expected_mean}"
    )

    # Zero burn count and percentage
    expected_zero_count = int((df_clean["area"] == 0).sum())
    expected_zero_pct = round((expected_zero_count / len(df_clean)) * 100.0, 1)
    assert kpis["zero_area_count"] == expected_zero_count, (
        f"Zero count mismatch: KPI={kpis['zero_area_count']} vs CSV={expected_zero_count}"
    )
    assert kpis["zero_area_pct"] == expected_zero_pct, (
        f"Zero pct mismatch: KPI={kpis['zero_area_pct']} vs CSV={expected_zero_pct}"
    )

    # Peak fire month
    expected_peak_month = str(df_clean["month"].value_counts().index[0]).upper()
    assert kpis["peak_month"] == expected_peak_month, (
        f"Peak month mismatch: KPI={kpis['peak_month']} vs CSV={expected_peak_month}"
    )
