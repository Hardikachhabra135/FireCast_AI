"""
Tests for UCI Forest Fires Dataset Integrity
"""

import os
import pytest
import pandas as pd
from src.preprocessing import load_raw_dataset, MONTHS, DAYS


def test_dataset_exists():
    assert os.path.exists("dataset/forestfires.csv"), "Dataset file dataset/forestfires.csv must exist."


def test_dataset_schema_and_columns():
    df = pd.read_csv("dataset/forestfires.csv")
    expected_cols = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    assert list(df.columns) == expected_cols, f"Columns do not match expected: {list(df.columns)}"


def test_dataset_record_count_and_no_nulls():
    df = pd.read_csv("dataset/forestfires.csv")
    assert len(df) == 517, f"Expected 517 rows in official UCI dataset, got {len(df)}"
    assert df.isnull().sum().sum() == 0, "Dataset contains null values."


def test_cleaned_dataset_duplicates():
    df_clean = load_raw_dataset("dataset/forestfires.csv")
    assert len(df_clean) <= 517, "Cleaned dataset should have <= 517 rows."
    assert len(df_clean) >= 510, "Cleaned dataset should have >= 510 rows after deduplication."
