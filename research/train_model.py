"""
Model training module for cryptocurrency market data.

Research-only guarantees:
- Training LightGBM regressor only
- No scanner logic, ranking, EWMA, or evaluation metrics
- Fixed random seed for determinism
- Export model artifacts to artifacts/ directory
- Import-safe
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor


# =========================
# DATA PREPARATION (Task 4.1)
# =========================
def prepare_training_data(features: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Separate features and labels from feature dataset.
    
    Requirements: 3.1
    """
    if not isinstance(features, pd.DataFrame):
        raise TypeError("features must be a pandas DataFrame")
    
    if "future_ret" not in features.columns:
        raise ValueError("future_ret column missing from features")
    
    # Separate features from labels
    feature_cols = [col for col in features.columns if col != "future_ret"]
    X = features[feature_cols].copy()
    y = features["future_ret"].copy()
    
    # Drop rows with NaN values
    valid_mask = ~(X.isna().any(axis=1) | y.isna())
    X = X[valid_mask]
    y = y[valid_mask]
    
    return X, y


# =========================
# LIGHTGBM TRAINING (Task 4.2)
# =========================
def train_lightgbm_model(X: pd.DataFrame, y: pd.Series) -> LGBMRegressor:
    """
    Train LightGBM regressor with fixed random seed.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.10
    """
    if not isinstance(X, pd.DataFrame):
        raise TypeError("X must be a pandas DataFrame")
    
    if not isinstance(y, pd.Series):
        raise TypeError("y must be a pandas Series")
    
    if len(X) != len(y):
        raise ValueError("X and y must have same length")
    
    if len(X) == 0:
        raise ValueError("Cannot train on empty dataset")
    
    # Configure LightGBM regressor with fixed random seed
    model = LGBMRegressor(
        random_state=42,  # Fixed seed for determinism
        verbose=-1,       # Suppress training output
        n_jobs=1,         # Single-threaded for determinism
    )
    
    # Train the model
    model.fit(X, y)
    
    return model

# =========================
# ARTIFACT EXPORT (Task 4.3)
# =========================
def export_model_artifacts(
    model: LGBMRegressor,
    feature_names: list,
    training_metadata: dict,
) -> None:
    """
    Export model artifacts to artifacts/ directory.
    
    Requirements: 3.6, 3.7, 3.8
    """
    if not isinstance(model, LGBMRegressor):
        raise TypeError("model must be a LGBMRegressor")
    
    if not isinstance(feature_names, list):
        raise TypeError("feature_names must be a list")
    
    if not isinstance(training_metadata, dict):
        raise TypeError("training_metadata must be a dict")
    
    # Ensure artifacts directory exists
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Export model.pkl
    model_path = artifacts_dir / "model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    # Export meta.json with training metadata
    meta_path = artifacts_dir / "meta.json"

    # OPTIONAL: lock seed into metadata for auditability
    training_metadata.setdefault("random_state", 42)
    
    with open(meta_path, "w") as f:
        json.dump(training_metadata, f, indent=2)
    
    # Export features.json with feature specifications
    features_spec = {
        "feature_names": feature_names,
        "num_features": len(feature_names),
        "feature_types": {name: "float" for name in feature_names}
    }
    
    features_path = artifacts_dir / "features.json"
    with open(features_path, "w") as f:
        json.dump(features_spec, f, indent=2)

# =========================
# MAIN EXECUTION PIPELINE
# =========================
def main() -> None:
    """
    Main training pipeline execution.
    
    This function would typically:
    1. Load feature datasets from build_features.py output
    2. Prepare training data
    3. Train LightGBM model
    4. Export model artifacts
    
    Note: Actual data loading implementation depends on specific file paths
    and would be added when integrating with the full pipeline.
    """
    print("Training pipeline ready - implement data loading as needed")


# =========================
# IMPORT SAFETY (Task 4.4)
# =========================
if __name__ == "__main__":
    main()