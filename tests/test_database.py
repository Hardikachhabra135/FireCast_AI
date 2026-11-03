"""
Tests for SQLite History Persistence
"""

import os
import pytest
from src.database import (
    init_db,
    save_prediction_record,
    get_prediction_history,
    delete_prediction_record,
    clear_all_history
)
from src.predict import predict_burned_area


def test_sqlite_crud_operations():
    init_db()
    
    # 1. Generate prediction
    payload = {
        "month": "aug",
        "day": "sun",
        "temp": 26.0,
        "RH": 35.0,
        "wind": 4.0,
        "rain": 0.0,
        "FFMC": 91.0,
        "DMC": 105.0,
        "DC": 600.0,
        "ISI": 8.0
    }
    pred_res = predict_burned_area(payload, include_shap=False)
    
    # 2. Insert
    rec_id = save_prediction_record(pred_res, notes="Test record")
    assert rec_id > 0
    
    # 3. Read
    history_df = get_prediction_history(limit=50)
    assert not history_df.empty
    assert (history_df["id"] == rec_id).any()
    
    # 4. Delete
    deleted = delete_prediction_record(rec_id)
    assert deleted is True
    
    # Verify deleted
    history_after = get_prediction_history(limit=50)
    assert not (history_after["id"] == rec_id).any()
