"""
FireCast AI — Data Preprocessing, Pipeline Construction, and Stratified Partitioning
Handles all 12 dataset features including spatial coordinates X and Y
"""

import os
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
import joblib

from src.utils import logger, load_config

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

ALL_FEATURES = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
NUMERICAL_FEATURES = ['X', 'Y', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
CATEGORICAL_FEATURES = ['month', 'day']


def load_raw_dataset(csv_path: str = "dataset/forestfires.csv") -> pd.DataFrame:
    """
    Load and clean the official UCI Forest Fires Dataset.
    Validates required columns and removes exact duplicate rows if present.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Forest fires dataset not found at: {csv_path}")
    
    df = pd.read_csv(csv_path)
    required_cols = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")
    
    # Normalize month and day strings
    df['month'] = df['month'].astype(str).str.lower().str.strip()
    df['day'] = df['day'].astype(str).str.lower().str.strip()
    
    # Check duplicates
    initial_len = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    if len(df) < initial_len:
        logger.info(f"Removed {initial_len - len(df)} duplicate records. Clean records: {len(df)}")
        
    logger.info(f"Loaded dataset: {df.shape[0]} records, {df.shape[1]} columns.")
    return df


def create_stratified_split(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
    n_bins: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs a stratified train/test split on log1p(area) bins to ensure that
    both zero-area fires and rare large wildfire events (>100 ha) are evenly distributed.
    """
    y_log = np.log1p(df['area'].values)
    
    # Create stratification bins: Bin 0 for zero area fires, and quantiles for non-zero fires
    strat_labels = np.zeros(len(df), dtype=int)
    non_zero_mask = (y_log > 0)
    
    # Divide non-zero fires into n_bins - 1 quantiles
    if np.sum(non_zero_mask) > (n_bins - 1):
        quantiles = pd.qcut(y_log[non_zero_mask], q=n_bins - 1, labels=False, duplicates='drop')
        strat_labels[non_zero_mask] = quantiles + 1
    
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(splitter.split(df, strat_labels))
    
    train_df = df.iloc[train_idx].copy().reset_index(drop=True)
    test_df = df.iloc[test_idx].copy().reset_index(drop=True)
    
    logger.info(
        f"Stratified split complete: {len(train_df)} train ({len(train_df)/len(df):.1%}), "
        f"{len(test_df)} test ({len(test_df)/len(df):.1%})"
    )
    return train_df, test_df


def build_preprocessor(
    categorical_cols: List[str] = CATEGORICAL_FEATURES,
    numerical_cols: List[str] = NUMERICAL_FEATURES,
    scaler_type: str = "robust"
) -> ColumnTransformer:
    """
    Builds a Scikit-Learn ColumnTransformer pipeline.
    One-hot encodes month and day with fixed categories to prevent unseen-category errors.
    Scales numerical spatial, weather, and FWI features using RobustScaler (or StandardScaler).
    """
    scaler = RobustScaler() if scaler_type == "robust" else StandardScaler()
    
    categories_list = []
    if 'month' in categorical_cols:
        categories_list.append(MONTHS)
    if 'day' in categorical_cols:
        categories_list.append(DAYS)
    
    cat_pipeline = OneHotEncoder(
        categories=categories_list if len(categories_list) == len(categorical_cols) else 'auto',
        handle_unknown='ignore',
        sparse_output=False
    )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', cat_pipeline, categorical_cols),
            ('num', scaler, numerical_cols)
        ],
        remainder='drop'
    )
    return preprocessor


def get_feature_names_from_preprocessor(preprocessor: ColumnTransformer) -> List[str]:
    """Extract human-readable feature names from the fitted preprocessor."""
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        names = []
        for name, trans, cols in preprocessor.transformers_:
            if name == 'remainder' or trans == 'drop':
                continue
            if hasattr(trans, 'get_feature_names_out'):
                names.extend(trans.get_feature_names_out(cols))
            else:
                names.extend(cols)
        return names


def calculate_dataset_quantiles(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate severity percentiles from non-zero fires in the dataset."""
    non_zero_fires = df[df['area'] > 0]['area']
    return {
        'p25': float(non_zero_fires.quantile(0.25)),
        'p50': float(non_zero_fires.quantile(0.50)),
        'p75': float(non_zero_fires.quantile(0.75)),
        'p90': float(non_zero_fires.quantile(0.90)),
        'max': float(df['area'].max()),
        'mean': float(df['area'].mean()),
        'median': float(df['area'].median()),
        'zero_pct': float((df['area'] == 0).mean() * 100)
    }
