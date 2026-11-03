"""
Tests for Pydantic Input Validation & Domain Boundaries
"""

import pytest
from pydantic import ValidationError
from src.validation import FirePredictionInput, check_training_boundary_warnings


def test_valid_input_passes():
    inp = FirePredictionInput(
        X=7,
        Y=5,
        month="aug",
        day="sun",
        temp=25.0,
        RH=40.0,
        wind=4.5,
        rain=0.0,
        FFMC=91.5,
        DMC=110.0,
        DC=650.0,
        ISI=8.5
    )
    assert inp.X == 7
    assert inp.Y == 5
    assert inp.month == "aug"
    assert inp.temp == 25.0


def test_invalid_spatial_coordinates_raise_error():
    with pytest.raises(ValidationError):
        FirePredictionInput(X=0)  # X must be >= 1
    with pytest.raises(ValidationError):
        FirePredictionInput(X=10) # X must be <= 9
    with pytest.raises(ValidationError):
        FirePredictionInput(Y=1)  # Y must be >= 2
    with pytest.raises(ValidationError):
        FirePredictionInput(Y=10) # Y must be <= 9


def test_invalid_month_raises_error():
    with pytest.raises(ValidationError):
        FirePredictionInput(month="foo")


def test_invalid_day_raises_error():
    with pytest.raises(ValidationError):
        FirePredictionInput(day="funday")


def test_out_of_range_humidity_raises_error():
    with pytest.raises(ValidationError):
        FirePredictionInput(RH=150.0)


def test_training_boundary_warnings():
    # Temp 40.0 exceeds Montesinho maximum (33.3)
    data = {"temp": 40.0, "RH": 5.0}
    warnings = check_training_boundary_warnings(data)
    assert len(warnings) >= 2
    assert any("Temperature" in w for w in warnings)
    assert any("Humidity" in w for w in warnings)
