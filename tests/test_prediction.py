"""
Tests for End-to-End Prediction Execution
"""

import pytest
from src.predict import predict_burned_area


def test_prediction_returns_valid_structure():
    payload = {
        "month": "aug",
        "day": "sun",
        "temp": 28.0,
        "RH": 30.0,
        "wind": 5.0,
        "rain": 0.0,
        "FFMC": 92.0,
        "DMC": 120.0,
        "DC": 650.0,
        "ISI": 9.0
    }
    result = predict_burned_area(payload, include_shap=True)
    assert "burned_area_ha" in result
    assert "severity" in result
    assert "inference_time_ms" in result
    assert result["burned_area_ha"] >= 0.0, "Burned area must never be negative."
    assert result["inference_time_ms"] > 0.0


def test_prediction_without_shap():
    payload = {
        "month": "sep",
        "day": "mon",
        "temp": 18.0,
        "RH": 55.0,
        "wind": 3.0,
        "rain": 0.0,
        "FFMC": 85.0,
        "DMC": 60.0,
        "DC": 400.0,
        "ISI": 4.0
    }
    result = predict_burned_area(payload, include_shap=False)
    assert result["shap_explanation"] is None
    assert result["burned_area_ha"] >= 0.0


def test_extreme_weather_prediction():
    payload = {
        "month": "aug",
        "day": "sat",
        "temp": 38.0,
        "RH": 15.0,
        "wind": 9.0,
        "rain": 0.0,
        "FFMC": 96.0,
        "DMC": 250.0,
        "DC": 850.0,
        "ISI": 25.0
    }
    result = predict_burned_area(payload, include_shap=False)
    assert result["burned_area_ha"] >= 0.0
    assert len(result["warnings"]) > 0, "Extreme conditions should trigger extrapolation warning."
