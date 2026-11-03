"""
FireCast AI — Production Prediction Engine & Safe Inference Execution
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

from src.utils import logger, load_config, format_hectares
from src.validation import FirePredictionInput, check_training_boundary_warnings
from src.severity import classify_severity

try:
    import streamlit as st
    cache_resource = st.cache_resource
except Exception:
    def cache_resource(func):
        return func

# Module-level cache for models to avoid reloading from disk on every invocation
_MODEL_CACHE: Dict[str, Any] = {}


@cache_resource
def get_cached_model(model_name: Optional[str] = None):
    """Retrieves cached model pipeline or loads it from disk."""
    global _MODEL_CACHE
    if "best_model" not in _MODEL_CACHE:
        best_path = "models/best_model.joblib"
        if not os.path.exists(best_path):
            raise FileNotFoundError(f"Model file not found at {best_path}. Please execute training pipeline first.")
        _MODEL_CACHE["best_model"] = joblib.load(best_path)

    best_name = "Random Forest Regressor"
    if os.path.exists("models/model_metadata.json"):
        try:
            import json
            with open("models/model_metadata.json", "r", encoding="utf-8") as f:
                best_name = json.load(f).get("model_name", best_name)
        except Exception:
            pass

    if model_name is None or model_name in ("Best Production Model", "best_model"):
        return _MODEL_CACHE["best_model"], best_name

    if "all_models" not in _MODEL_CACHE:
        all_path = "models/all_models.joblib"
        if os.path.exists(all_path):
            _MODEL_CACHE["all_models"] = joblib.load(all_path)

    if "all_models" in _MODEL_CACHE and model_name in _MODEL_CACHE["all_models"]:
        return _MODEL_CACHE["all_models"][model_name], model_name

    return _MODEL_CACHE["best_model"], best_name


def predict_burned_area(
    input_data: Dict[str, Any],
    model_name: Optional[str] = None,
    include_shap: bool = True
) -> Dict[str, Any]:
    """
    Executes end-to-end burned area prediction:
    1. Validates inputs through Pydantic schema.
    2. Runs inference through trained pipeline.
    3. Reverses log1p transformation via expm1 and enforces non-negative bounds.
    4. Computes analytical severity category.
    5. Computes local SHAP explanation if requested.
    6. Returns execution telemetry.
    """
    start_time = time.perf_counter()
    config = load_config()

    # 1. Validation
    validated = FirePredictionInput(**input_data)
    row_df = validated.to_dataframe_row()
    boundary_warnings = check_training_boundary_warnings(input_data, config)

    # 2. Model retrieval
    pipeline, resolved_model_name = get_cached_model(model_name)

    # 3. Model Inference (on log-scale)
    pred_log = pipeline.predict(row_df)[0]

    # 4. Inverse Transformation & Safety Clipping
    # burned area in hectares cannot be negative
    pred_ha = float(np.expm1(pred_log))
    pred_ha = max(0.0, pred_ha)

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    # 5. Severity Categorization
    severity_info = classify_severity(pred_ha, config)

    # 6. Local SHAP Explanation (TreeExplainer on Random Forest for instantaneous local waterfall)
    shap_summary = None
    if include_shap:
        try:
            from src.explainability import compute_instance_shap
            shap_summary = compute_instance_shap(row_df)
        except Exception as e:
            logger.warning(f"Could not compute instance SHAP: {e}")

    result = {
        "burned_area_ha": round(pred_ha, 3),
        "burned_area_formatted": format_hectares(pred_ha),
        "predicted_log_scale": round(float(pred_log), 4),
        "severity": severity_info,
        "model_used": resolved_model_name,
        "inference_time_ms": round(latency_ms, 2),
        "input_summary": validated.model_dump(),
        "warnings": boundary_warnings,
        "shap_explanation": shap_summary,
        "disclaimer": (
            "FireCast AI estimates the conditional burned area in hectares IF a wildfire occurs under these conditions. "
            "It does NOT predict whether a fire will start, guarantee containment, or replace official emergency warning services."
        )
    }

    return result
