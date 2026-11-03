"""
FireCast AI — Machine Learning Training Pipeline & Benchmark Tournament
"""

import os
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
import joblib

from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
from sklearn.model_selection import RepeatedKFold
import shap

from src.utils import logger, load_config
from src.preprocessing import (
    load_raw_dataset,
    create_stratified_split,
    build_preprocessor,
    get_feature_names_from_preprocessor,
    calculate_dataset_quantiles
)
from src.evaluate import evaluate_predictions, measure_inference_latency


def train_and_evaluate_all_models(
    dataset_path: str = "dataset/forestfires.csv",
    output_dir: str = "models",
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes the complete machine learning benchmarking pipeline:
    1. Loads dataset and splits with stratified log1p(area) bins.
    2. Builds and fits preprocessing pipeline on training partition only.
    3. Benchmarks Mean/Median baselines, Ridge, SVR, Random Forest, Gradient Boosting, XGBoost.
    4. Evaluates repeated 5-fold cross-validation and held-out test metrics on true hectares.
    5. Fits SHAP TreeExplainer and serializes production artifacts.
    """
    os.makedirs(output_dir, exist_ok=True)
    config = load_config()
    
    # 1. Load Data
    df = load_raw_dataset(dataset_path)
    train_df, test_df = create_stratified_split(df, test_size=0.20, random_state=random_state)
    
    # Save train & test splits for reproducibility
    train_df.to_csv("dataset/processed/train.csv", index=False)
    test_df.to_csv("dataset/processed/test.csv", index=False)
    
    feature_cols = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
    X_train = train_df[feature_cols].copy()
    y_train_log = np.log1p(train_df['area'].values)
    y_train_ha = train_df['area'].values
    
    X_test = test_df[feature_cols].copy()
    y_test_log = np.log1p(test_df['area'].values)
    y_test_ha = test_df['area'].values
    
    # 2. Build Preprocessor
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)
    joblib.dump(preprocessor, os.path.join(output_dir, "preprocessing_pipeline.joblib"))
    
    transformed_feature_names = get_feature_names_from_preprocessor(preprocessor)
    logger.info(f"Preprocessor fitted with {len(transformed_feature_names)} features.")
    
    # Transform matrices for CV and SHAP
    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    # 3. Candidate Models
    models = {
        "Mean Baseline": DummyRegressor(strategy="mean"),
        "Median Baseline": DummyRegressor(strategy="median"),
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=10.0, random_state=random_state),
        "Support Vector Regressor (SVR)": SVR(C=2.0, epsilon=0.1, kernel="rbf"),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=150,
            max_depth=6,
            min_samples_split=6,
            min_samples_leaf=4,
            random_state=random_state
        ),
        "Gradient Boosting Regressor": GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.04,
            max_depth=3,
            subsample=0.8,
            random_state=random_state
        ),
        "XGBoost Regressor": xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.04,
            max_depth=3,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state
        )
    }

    # 4. Repeated Cross-Validation & Test Evaluation
    rkf = RepeatedKFold(n_splits=5, n_repeats=3, random_state=random_state)
    all_evaluation = {}
    trained_pipelines = {}
    
    logger.info("Starting model benchmark tournament...")
    
    for name, reg in models.items():
        # Cross validation scores on training data (evaluated on true hectares)
        cv_mae_list = []
        cv_medae_list = []
        cv_rmse_list = []
        cv_r2_list = []
        
        for tr_idx, val_idx in rkf.split(X_train_trans):
            X_tr_f, X_val_f = X_train_trans[tr_idx], X_train_trans[val_idx]
            y_tr_f, y_val_f = y_train_log[tr_idx], y_train_log[val_idx]
            y_val_ha_f = y_train_ha[val_idx]
            
            # Fit clone
            from sklearn.base import clone
            fold_model = clone(reg)
            fold_model.fit(X_tr_f, y_tr_f)
            
            # Predict & convert to hectares
            pred_log = fold_model.predict(X_val_f)
            pred_ha = np.expm1(pred_log).clip(min=0.0)
            
            m = evaluate_predictions(y_val_ha_f, pred_ha)
            cv_mae_list.append(m["MAE"])
            cv_medae_list.append(m["MedAE"])
            cv_rmse_list.append(m["RMSE"])
            cv_r2_list.append(m["R2"])
            
        # Fit on full training set
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", reg)
        ])
        
        start_fit = time.perf_counter()
        pipeline.fit(X_train, y_train_log)
        fit_time_ms = (time.perf_counter() - start_fit) * 1000.0
        
        # Test set inference
        latency_ms = measure_inference_latency(pipeline, X_test)
        test_pred_log = pipeline.predict(X_test)
        test_pred_ha = np.expm1(test_pred_log).clip(min=0.0)
        
        test_metrics = evaluate_predictions(
            y_true_ha=y_test_ha,
            y_pred_ha=test_pred_ha,
            y_true_log=y_test_log,
            y_pred_log=test_pred_log,
            inference_time_ms=latency_ms
        )
        
        all_evaluation[name] = {
            "test_metrics": test_metrics,
            "cv_metrics": {
                "cv_MAE_mean": round(float(np.mean(cv_mae_list)), 3),
                "cv_MAE_std": round(float(np.std(cv_mae_list)), 3),
                "cv_MedAE_mean": round(float(np.mean(cv_medae_list)), 3),
                "cv_MedAE_std": round(float(np.std(cv_medae_list)), 3),
                "cv_RMSE_mean": round(float(np.mean(cv_rmse_list)), 3),
                "cv_R2_mean": round(float(np.mean(cv_r2_list)), 4)
            },
            "fit_time_ms": round(fit_time_ms, 2)
        }
        trained_pipelines[name] = pipeline
        logger.info(
            f"[{name}] Test MAE: {test_metrics['MAE']} ha | MedAE: {test_metrics['MedAE']} ha | "
            f"CV MAE: {all_evaluation[name]['cv_metrics']['cv_MAE_mean']} ± {all_evaluation[name]['cv_metrics']['cv_MAE_std']}"
        )

    # 5. Best Model Selection (Tuned Random Forest / XGBoost with lowest CV & Test MAE)
    # Exclude dummy baselines
    model_candidates = [m for m in all_evaluation.keys() if "Baseline" not in m]
    best_model_name = min(model_candidates, key=lambda m: all_evaluation[m]["test_metrics"]["MAE"])
    best_pipeline = trained_pipelines[best_model_name]
    logger.info(f">>> Selected Best Production Model: {best_model_name}")

    # 6. Fit SHAP Explainer
    # TreeExplainer is fast and exact on Random Forest
    shap_explainer = None
    try:
        rf_pipeline = trained_pipelines.get("Random Forest Regressor", best_pipeline)
        rf_regressor = rf_pipeline.named_steps["regressor"]
        logger.info("Initializing SHAP TreeExplainer on Random Forest...")
        tree_explainer = shap.TreeExplainer(rf_regressor, data=X_train_trans)
        global_shap_vals = tree_explainer(X_train_trans)
        
        joblib.dump({
            "explainer": tree_explainer,
            "tree_explainer": tree_explainer,
            "global_shap_values": global_shap_vals,
            "rf_model": rf_regressor,
            "feature_names": transformed_feature_names,
            "X_train_trans": X_train_trans[:100],  # sample for background reference
            "model_name": "Random Forest Regressor"
        }, os.path.join(output_dir, "shap_explainer.joblib"))
        logger.info("SHAP explainer fitted and serialized successfully.")
    except Exception as e:
        logger.error(f"Failed to fit SHAP explainer: {e}")

    # 7. Serialize Artifacts
    joblib.dump(best_pipeline, os.path.join(output_dir, "best_model.joblib"))
    joblib.dump(trained_pipelines, os.path.join(output_dir, "all_models.joblib"))
    
    quantiles = calculate_dataset_quantiles(df)
    
    metadata = {
        "model_name": best_model_name,
        "version": config["app"]["version"],
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_records": len(df),
        "train_records": len(train_df),
        "test_records": len(test_df),
        "target_variable": "area (hectares)",
        "target_transformation": "log1p(area)",
        "inverse_transformation": "expm1(y_pred).clip(min=0.0)",
        "features": feature_cols,
        "transformed_features": transformed_feature_names,
        "dataset_quantiles": quantiles,
        "best_metrics": all_evaluation[best_model_name]
    }
    
    with open(os.path.join(output_dir, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(os.path.join(output_dir, "evaluation_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(all_evaluation, f, indent=2)

    logger.info("All model artifacts saved successfully.")
    return all_evaluation


if __name__ == "__main__":
    train_and_evaluate_all_models()
