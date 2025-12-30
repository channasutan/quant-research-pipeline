"""
Feature engineering module for cryptocurrency market data.

Research-only guarantees:
- Causal features only (no look-ahead bias)
- Global +1 bar shift for all features
- Labels (future_ret) ONLY for training
- No microstructure, fracdiff, cusum, or z-score features
- Import-safe
"""

from __future__ import annotations

from typing import List
import numpy as np
import pandas as pd


# =========================
# RETURN CALCULATIONS (Task 3.1)
# =========================
def calculate_returns(prices: pd.Series, periods: List[int]) -> pd.DataFrame:
    """
    ret_n = log(close_t / close_{t-n})

    Requirements: 2.6
    """
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series")

    out = pd.DataFrame(index=prices.index)

    for p in periods:
        if p <= 0:
            raise ValueError("Return period must be positive")
        out[f"ret_{p}"] = np.log(prices / prices.shift(p))

    return out


# =========================
# EMA FEATURES (Task 3.2)
# =========================
def calculate_ema(prices: pd.Series, windows: List[int]) -> pd.DataFrame:
    """
    ema_w = exponential moving average

    Requirements: 2.7
    """
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series")

    out = pd.DataFrame(index=prices.index)

    for w in windows:
        if w <= 0:
            raise ValueError("EMA window must be positive")
        out[f"ema_{w}"] = prices.ewm(span=w, adjust=False).mean()

    return out


def calculate_price_ema_ratios(
    prices: pd.Series,
    ema_df: pd.DataFrame,
    windows: List[int],
) -> pd.DataFrame:
    """
    close_ema_w_ratio = (close / ema_w) - 1

    Requirements: 2.8
    """
    if not prices.index.equals(ema_df.index):
        raise ValueError("prices and ema_df must have same index")

    out = pd.DataFrame(index=prices.index)

    for w in windows:
        col = f"ema_{w}"
        if col not in ema_df.columns:
            raise KeyError(f"{col} missing in ema_df")
        out[f"close_ema_{w}_ratio"] = (prices / ema_df[col]) - 1

    return out


# =========================
# VOLATILITY FEATURES (Task 3.3)
# =========================
def calculate_realized_volatility(ret_1: pd.Series, windows: List[int]) -> pd.DataFrame:
    """
    rv_w = sqrt(sum(ret_1^2) over w bars)

    Requirements: 2.9
    """
    if not isinstance(ret_1, pd.Series):
        raise TypeError("ret_1 must be a pandas Series")

    out = pd.DataFrame(index=ret_1.index)

    for w in windows:
        if w <= 0:
            raise ValueError("Volatility window must be positive")
        out[f"rv_{w}"] = np.sqrt((ret_1 ** 2).rolling(w).sum())

    return out


# =========================
# VOLUME FEATURES (Task 3.3)
# =========================
def calculate_log_volume(volume: pd.Series) -> pd.Series:
    """
    log_volume = log(raw volume)

    Requirements: 2.10
    """
    if not isinstance(volume, pd.Series):
        raise TypeError("volume must be a pandas Series")

    return np.log(volume.clip(lower=1))


def calculate_adv_30(volume: pd.Series) -> pd.Series:
    """
    adv_30 = 30-bar rolling mean of raw volume

    Requirements: 2.11, 4.11a
    """
    if not isinstance(volume, pd.Series):
        raise TypeError("volume must be a pandas Series")

    return volume.rolling(30).mean()


# =========================
# CAUSALITY ENFORCEMENT (Task 3.4)
# =========================
def shift_features_for_causality(features: pd.DataFrame) -> pd.DataFrame:
    """
    Shift ALL feature columns by +1 bar.

    Requirements: 2.1, 2.13
    """
    if not isinstance(features, pd.DataFrame):
        raise TypeError("features must be a DataFrame")

    return features.shift(1)


# =========================
# TRAINING LABEL (Task 3.4)
# =========================
def create_future_ret_label(prices: pd.Series) -> pd.Series:
    """
    future_ret = log(close_{t+1} / close_t)

    Requirements: 2.12
    """
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series")

    y = np.log(prices.shift(-1) / prices)
    y.name = "future_ret"
    return y


# =========================
# PIPELINE INTEGRATION (Task 3.5)
# =========================
def build_feature_set(
    ohlcv: pd.DataFrame,
    include_labels: bool = True,
) -> pd.DataFrame:
    """
    Build full causal feature set from OHLCV data.

    Requirements: 2.2 – 2.5
    """
    required = {"open", "high", "low", "close", "volume"}
    if not required.issubset(ohlcv.columns):
        raise ValueError(f"Missing columns: {required - set(ohlcv.columns)}")

    close = ohlcv["close"]
    volume = ohlcv["volume"]

    # Core features
    ret_df = calculate_returns(close, [1, 3, 6, 12])
    ema_df = calculate_ema(close, [12, 24, 48])
    ratio_df = calculate_price_ema_ratios(close, ema_df, [12, 24, 48])
    vol_df = calculate_realized_volatility(ret_df["ret_1"], [24, 72])

    # Volume features
    log_vol = calculate_log_volume(volume).to_frame("log_volume")
    adv_30 = calculate_adv_30(volume).to_frame("adv_30")

    # Combine
    features = pd.concat(
        [ret_df, ema_df, ratio_df, vol_df, log_vol, adv_30],
        axis=1,
    )

    # Enforce causality
    features = shift_features_for_causality(features)

    # Labels (training only)
    if include_labels:
        y = create_future_ret_label(close)
        features = pd.concat([features, y], axis=1)

    return features


# =========================
# IMPORT SAFETY
# =========================
if __name__ == "__main__":
    pass
