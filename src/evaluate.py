"""
FireCast AI — Research-Grade Model Evaluation on Original Hectares Scale
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import mean_absolute_error, median_absolute_error, root_mean_squared_error, mean_squared_error, r2_score


def evaluate_predictions(
    y_true_ha: np.ndarray,
    y_pred_ha: np.ndarray,
    y_true_log: np.ndarray = None,
    y_pred_log: np.ndarray = None,
    inference_time_ms: float = 0.0
) -> Dict[str, float]:
    """
    Computes regression metrics strictly on the natural hectares scale,
    accompanied by log-scale error metrics for complete research transparency.
    """
    y_true_ha = np.asarray(y_true_ha, dtype=float)
    y_pred_ha = np.asarray(y_pred_ha, dtype=float).clip(min=0.0)
    
    mae = float(mean_absolute_error(y_true_ha, y_pred_ha))
    medae = float(median_absolute_error(y_true_ha, y_pred_ha))
    mse = float(mean_squared_error(y_true_ha, y_pred_ha))
    rmse = float(root_mean_squared_error(y_true_ha, y_pred_ha))
    r2 = float(r2_score(y_true_ha, y_pred_ha))
    
    metrics = {
        "MAE": round(mae, 3),
        "MedAE": round(medae, 3),
        "MSE": round(mse, 3),
        "RMSE": round(rmse, 3),
        "R2": round(r2, 4),
        "latency_ms": round(inference_time_ms, 2)
    }
    
    if y_true_log is not None and y_pred_log is not None:
        log_mae = float(mean_absolute_error(y_true_log, y_pred_log))
        log_rmse = float(root_mean_squared_error(y_true_log, y_pred_log))
        metrics["log_MAE"] = round(log_mae, 4)
        metrics["log_RMSE"] = round(log_rmse, 4)
        
    return metrics


def measure_inference_latency(pipeline, X_sample: pd.DataFrame, n_iterations: int = 50) -> float:
    """Measure average single-sample inference latency in milliseconds."""
    single_row = X_sample.iloc[[0]]
    # Warmup
    for _ in range(5):
        pipeline.predict(single_row)
        
    start = time.perf_counter()
    for _ in range(n_iterations):
        pipeline.predict(single_row)
    elapsed = time.perf_counter() - start
    return (elapsed / n_iterations) * 1000.0


def compute_residuals(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Compute residuals and error distributions."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float).clip(min=0.0)
    residuals = y_true - y_pred
    
    return {
        "residuals": residuals.tolist(),
        "mean_residual": float(np.mean(residuals)),
        "std_residual": float(np.std(residuals)),
        "max_underprediction": float(np.max(residuals)),  # fire was bigger than predicted
        "max_overprediction": float(abs(np.min(residuals)))  # fire was smaller than predicted
    }
