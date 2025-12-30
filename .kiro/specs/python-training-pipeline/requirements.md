# Requirements Document

## Introduction

A clean, research-only Python training pipeline for cryptocurrency market data analysis. The system fetches OHLCV data, builds causal features, and trains a LightGBM regression model for offline research purposes only.

## Glossary

- **OHLCV**: Open, High, Low, Close, Volume market data
- **CCXT**: CryptoCurrency eXchange Trading library
- **Causal Features**: Features that only use historical data (no look-ahead bias)
- **Future_Ret**: Future return label used only in training (not in production)
- **LightGBM**: Light Gradient Boosting Machine regression algorithm
- **Parquet**: Columnar storage file format
- **Data_Fetcher**: Component responsible for retrieving market data
- **Feature_Builder**: Component responsible for creating training features
- **Model_Trainer**: Component responsible for training the regression model

## Requirements

### Requirement 1: Data Fetching

**User Story:** As a researcher, I want to fetch cryptocurrency OHLCV data reliably, so that I can build a consistent training dataset.

#### Acceptance Criteria

1. THE Data_Fetcher SHALL use CCXT library to retrieve OHLCV data from cryptocurrency exchanges
2. WHEN fetching data, THE Data_Fetcher SHALL only retrieve closed candles (no incomplete bars)
3. THE Data_Fetcher SHALL cache data per symbol in parquet format for efficient storage
4. THE Data_Fetcher SHALL fetch data deterministically and sequentially (no asynchronous operations)
5. THE Data_Fetcher SHALL implement the fetch_raw.py module in the research/ directory

### Requirement 2: Feature Engineering

**User Story:** As a researcher, I want to create causal features from market data, so that I can train models without look-ahead bias.

#### Acceptance Criteria

1. THE Feature_Builder SHALL create only causal features using historical data
2. THE Feature_Builder SHALL NOT include microstructure features
3. THE Feature_Builder SHALL NOT include fractional differentiation (fracdiff) features
4. THE Feature_Builder SHALL NOT include CUSUM features
5. THE Feature_Builder SHALL NOT include rolling z-score features
6. THE Feature_Builder SHALL create return features: ret_1, ret_3, ret_6, ret_12
7. THE Feature_Builder SHALL create exponential moving averages: ema_12, ema_24, ema_48
8. THE Feature_Builder SHALL create price-to-EMA ratio: close / ema_w - 1
9. THE Feature_Builder SHALL create realized volatility features: rv_24, rv_72
10. THE Feature_Builder SHALL create log_volume feature
11. THE Feature_Builder SHALL create average daily volume feature: adv_30
12. WHEN in training mode, THE Feature_Builder SHALL add future_ret label
13. THE Feature_Builder SHALL shift ALL features by +1 bar to ensure causality
14. THE Feature_Builder SHALL implement the build_features.py module in the research/ directory

### Requirement 3: Model Training

**User Story:** As a researcher, I want to train a LightGBM regression model, so that I can predict future returns from historical features.

#### Acceptance Criteria

1. THE Model_Trainer SHALL train a LightGBM regressor on the prepared features
2. THE Model_Trainer SHALL NOT implement scanner logic
3. THE Model_Trainer SHALL NOT implement ranking functionality
4. THE Model_Trainer SHALL NOT implement EWMA smoothing
5. THE Model_Trainer SHALL NOT calculate evaluation metrics
6. THE Model_Trainer SHALL export model.pkl to artifacts/ directory
7. THE Model_Trainer SHALL export meta.json to artifacts/ directory
8. THE Model_Trainer SHALL export features.json to artifacts/ directory
9. THE Model_Trainer SHALL implement the train_model.py module in the research/ directory
10. THE Model_Trainer SHALL set and fix a random seed for LightGBM training


### Requirement 4: System Constraints

**User Story:** As a researcher, I want a clean training-only system, so that I can focus on research without production complexity.

#### Acceptance Criteria

1. THE System SHALL be designed for training and offline research only
2. THE System SHALL allow future_ret labels ONLY in training context
3. THE System SHALL NOT implement scanner ranking functionality
4. THE System SHALL NOT implement smoothing operations
5. THE System SHALL NOT implement API endpoints
6. THE System SHALL NOT implement Supabase database uploads
7. THE System SHALL NOT implement S3 cloud storage uploads
8. THE System SHALL produce deterministic and readable code
9. THE System SHALL be import-safe (no execution on module import)
10. THE System SHALL create exactly three files: fetch_raw.py, build_features.py, train_model.py
11. THE System SHALL NOT include additional files beyond the specified three modules.
11a. adv_30 SHALL be defined as a 30-bar rolling mean of raw volume (not dollar volume)
