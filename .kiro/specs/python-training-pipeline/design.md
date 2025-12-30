# Design Document

## Overview

The Python training pipeline is a research-focused system for cryptocurrency market analysis consisting of three sequential modules: data fetching, feature engineering, and model training. The system prioritizes deterministic behavior, causal feature construction, and clean separation of concerns while maintaining strict constraints against production-oriented functionality.

This system is training-only and intended solely for offline research.

## Architecture

The system follows a linear pipeline architecture with three independent modules:

Raw Data → Features → Trained Model  
fetch_raw.py → build_features.py → train_model.py

Each module operates independently with file-based data exchange:

- fetch_raw.py outputs parquet files per symbol
- build_features.py reads parquet files and outputs feature datasets
- train_model.py reads feature datasets and outputs model artifacts

No databases, APIs, schedulers, or external services are used.

## Components and Interfaces

### Data Fetcher (fetch_raw.py)

**Purpose**  
Retrieve and cache OHLCV data from cryptocurrency exchanges.

**Key Functions**

- fetch_symbol_data(symbol: str, timeframe: str, exchange: str) -> pd.DataFrame
- cache_to_parquet(data: pd.DataFrame, symbol: str, path: str) -> None
- load_cached_data(symbol: str, path: str) -> pd.DataFrame

**Dependencies**

- ccxt for exchange connectivity
- pandas for data manipulation
- pyarrow for parquet file operations

**Data Flow**

1. Initialize exchange connection via CCXT
2. Fetch OHLCV data using exchange.fetch_ohlcv
3. Use closed candles only (exclude incomplete bars)
4. Cache data per symbol in parquet format
5. Fetch data deterministically and sequentially (no async)

### Feature Builder (build_features.py)

**Purpose**  
Transform raw OHLCV data into causal features for model training.

**Key Functions**

- calculate_returns(prices: pd.Series, periods: List[int]) -> pd.DataFrame
- calculate_ema(prices: pd.Series, windows: List[int]) -> pd.DataFrame
- calculate_realized_volatility(returns: pd.Series, windows: List[int]) -> pd.DataFrame
- build_feature_set(ohlcv_data: pd.DataFrame, include_labels: bool) -> pd.DataFrame
- shift_features_for_causality(features: pd.DataFrame) -> pd.DataFrame

**Feature Specifications**

- Return Features: ret_1, ret_3, ret_6, ret_12  
  ret_n = log(close_t / close_{t-n})

- EMA Features: ema_12, ema_24, ema_48

- Price Ratio Features:  
  close_ema_{w}_ratio = (close / ema_{w}) - 1

- Volatility Features: rv_24, rv_72  
  Computed from ret_1

- Volume Features:  
  log_volume = log(volume)  
  adv_30 = 30-bar rolling mean of raw volume

- Training Label:  
  future_ret (forward return, training only)

**Causality Enforcement**

All feature columns are shifted by +1 bar to prevent look-ahead bias.

### Model Trainer (train_model.py)

**Purpose**  
Train a LightGBM regression model and export training artifacts.

**Key Functions**

- prepare_training_data(features: pd.DataFrame) -> (X, y)
- train_lightgbm_model(X, y) -> LGBMRegressor
- export_model_artifacts(model, features, metadata) -> None

**Model Configuration**

- Algorithm: LightGBM Regressor
- Target: future_ret
- No hyperparameter optimization
- Fixed random seed for determinism

**Artifact Exports**

- artifacts/model.pkl
- artifacts/meta.json
- artifacts/features.json

## Data Models

### OHLCV Data Schema

- timestamp: pd.Timestamp
- open: float
- high: float
- low: float
- close: float
- volume: float

### Feature Data Schema

- timestamp: pd.Timestamp
- ret_1: float
- ret_3: float
- ret_6: float
- ret_12: float
- ema_12: float
- ema_24: float
- ema_48: float
- close_ema_12_ratio: float
- close_ema_24_ratio: float
- close_ema_48_ratio: float
- rv_24: float
- rv_72: float
- log_volume: float
- adv_30: float
- future_ret: float

## Correctness Properties

- All features are strictly causal
- All features are shifted by +1 bar
- future_ret is used only during training
- No smoothing, ranking, or production logic exists
- Training results are deterministic given identical inputs
