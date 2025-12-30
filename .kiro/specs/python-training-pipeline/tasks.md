# Implementation Plan: Python Training Pipeline

## Overview

Implementation of a clean, research-only Python training pipeline consisting of three sequential modules: data fetching (fetch_raw.py), feature engineering (build_features.py), and model training (train_model.py). Each module operates independently with file-based data exchange.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create research/ directory structure
  - Create artifacts/ directory for model outputs
  - Set up requirements.txt with necessary dependencies (ccxt, pandas, pyarrow, lightgbm, numpy)
  - _Requirements: 1.5, 2.14, 3.9_

- [-] 2. Implement data fetching module
  - [x] 2.1 Create fetch_raw.py with CCXT integration
    - Implement fetch_symbol_data() function using CCXT
    - Ensure only closed candles are fetched (no incomplete bars)
    - Implement deterministic, sequential fetching (no async operations)
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 2.2 Implement parquet caching functionality
    - Create cache_to_parquet() function for per-symbol storage
    - Create load_cached_data() function for reading cached data
    - Ensure efficient parquet file operations
    - _Requirements: 1.3_

  - [x] 2.3 Add import safety and main execution guard
    - Ensure no code executes on module import
    - Add proper if __name__ == "__main__" guards
    - _Requirements: 4.9_

- [-] 3. Implement feature engineering module
  - [x] 3.1 Create build_features.py with return calculations
    - Implement calculate_returns() for ret_1, ret_3, ret_6, ret_12
    - Use log returns: log(close_t / close_{t-n})
    - _Requirements: 2.6_

  - [x] 3.2 Implement EMA and price ratio features
    - Create calculate_ema() for ema_12, ema_24, ema_48
    - Implement close/ema ratio features: (close / ema_w) - 1
    - _Requirements: 2.7, 2.8_

  - [x] 3.3 Implement volatility and volume features
    - Create calculate_realized_volatility() for rv_24, rv_72 from ret_1
    - Implement log_volume feature: log(volume)
    - Implement adv_30 as 30-bar rolling mean of raw volume
    - _Requirements: 2.9, 2.10, 2.11, 4.11a_

  - [x] 3.4 Implement causality enforcement and labeling
    - Create shift_features_for_causality() to shift all features by +1 bar
    - Add future_ret label creation (training mode only)
    - Ensure no look-ahead bias in feature construction
    - _Requirements: 2.1, 2.12, 2.13_

  - [x] 3.5 Integrate feature building pipeline
    - Create build_feature_set() main function
    - Ensure causal feature construction (no microstructure, fracdiff, cusum, z-score)
    - Add import safety guards
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 4.9_

- [x] 4. Implement model training module
  - [x] 4.1 Create train_model.py with data preparation
    - Implement prepare_training_data() to separate features and labels
    - Load feature datasets from build_features.py output
    - _Requirements: 3.1_

  - [x] 4.2 Implement LightGBM training
    - Create train_lightgbm_model() function
    - Configure LightGBM regressor with fixed random seed
    - Ensure no scanner logic, ranking, EWMA, or evaluation metrics
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.10_

  - [x] 4.3 Implement artifact export functionality
    - Create export_model_artifacts() function
    - Export model.pkl to artifacts/ directory
    - Export meta.json with training metadata
    - Export features.json with feature specifications
    - _Requirements: 3.6, 3.7, 3.8_

  - [x] 4.4 Add import safety and main execution
    - Ensure no code executes on module import
    - Add proper execution guards
    - _Requirements: 4.9_

- [x] 5. Final integration and validation
  - [x] 5.1 Verify system constraints compliance
    - Ensure training-only design (no production features)
    - Verify no API, Supabase, or S3 functionality
    - Confirm deterministic and readable code
    - _Requirements: 4.1, 4.2, 4.5, 4.6, 4.7, 4.8_

  - [x] 5.2 Test end-to-end pipeline execution
    - Run fetch_raw.py → build_features.py → train_model.py sequence
    - Verify artifacts are created correctly
    - Ensure exactly three files are implemented (no additional files)
    - _Requirements: 4.10, 4.11_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The pipeline must be executed sequentially: fetch → features → train
- All modules must be import-safe with no execution on import
- System is strictly training-only with no production features