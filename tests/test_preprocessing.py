"""
Tests for Preprocessing Pipeline & Stratification
"""

import pytest
import numpy as np
import pandas as pd
from src.preprocessing import (
    load_raw_dataset,
    create_stratified_split,
    build_preprocessor,
    get_feature_names_from_preprocessor
)


def test_stratified_split_ratio():
    df = load_raw_dataset("dataset/forestfires.csv")
    train_df, test_df = create_stratified_split(df, test_size=0.20, random_state=42)
    assert len(train_df) + len(test_df) == len(df)
    # Check approximately 80/20
    test_ratio = len(test_df) / len(df)
    assert 0.18 <= test_ratio <= 0.22


def test_log1p_transformation_invertibility():
    original_areas = np.array([0.0, 0.52, 10.4, 1090.84])
    transformed = np.log1p(original_areas)
    inverted = np.expm1(transformed)
    np.testing.assert_allclose(original_areas, inverted, rtol=1e-5)


def test_preprocessor_shape_and_features():
    df = load_raw_dataset("dataset/forestfires.csv")
    features = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
    preprocessor = build_preprocessor()
    X_trans = preprocessor.fit_transform(df[features])
    
    # 10 numerical features + 12 months + 7 days = 29 columns
    assert X_trans.shape[1] == 29, f"Expected 29 transformed features, got {X_trans.shape[1]}"
    feature_names = get_feature_names_from_preprocessor(preprocessor)
    assert len(feature_names) == 29
