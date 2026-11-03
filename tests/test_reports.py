"""
Tests for PDF & Report Generation
"""

import pytest
from src.predict import predict_burned_area
from src.reports import generate_pdf_report


def test_pdf_report_generation():
    payload = {
        "month": "aug",
        "day": "sun",
        "temp": 29.5,
        "RH": 28.0,
        "wind": 5.2,
        "rain": 0.0,
        "FFMC": 93.0,
        "DMC": 130.0,
        "DC": 680.0,
        "ISI": 10.5
    }
    pred_res = predict_burned_area(payload, include_shap=True)
    pdf_bytes = generate_pdf_report(pred_res)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000, "PDF bytes should be substantial."
    assert pdf_bytes.startswith(b"%PDF"), "Generated output should be a valid PDF document."
