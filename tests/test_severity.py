"""
Tests for Severity Band Classification
"""

import pytest
from src.severity import classify_severity


def test_low_severity_boundary():
    sev = classify_severity(0.0)
    assert sev["key"] == "low"
    assert sev["name"] == "Low Severity"

    sev_border = classify_severity(2.49)
    assert sev_border["key"] == "low"


def test_moderate_severity_boundary():
    sev = classify_severity(2.5)
    assert sev["key"] == "moderate"
    assert sev["name"] == "Moderate Severity"

    sev_high = classify_severity(9.99)
    assert sev_high["key"] == "moderate"


def test_high_severity_boundary():
    sev = classify_severity(10.0)
    assert sev["key"] == "high"
    assert sev["name"] == "High Severity"

    sev_upper = classify_severity(34.9)
    assert sev_upper["key"] == "high"


def test_extreme_severity_boundary():
    sev = classify_severity(35.0)
    assert sev["key"] == "extreme"
    assert sev["name"] == "Extreme Severity"

    sev_giant = classify_severity(1090.84)
    assert sev_giant["key"] == "extreme"


def test_negative_input_handled_safely():
    sev = classify_severity(-5.0)
    assert sev["key"] == "low"
    assert sev["burned_area_ha"] == 0.0
