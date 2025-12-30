"""
Data fetching module for cryptocurrency OHLCV data.

Research-only guarantees:
- Deterministic
- Sequential (no async)
- Closed candles only
- No incremental updates
- Import-safe
"""

from __future__ import annotations

import os
from typing import Optional

import ccxt
import pandas as pd


# =========================
# CONFIG (LOCKED)
# =========================
DEFAULT_TIMEFRAME = "4h"
DEFAULT_EXCHANGE = "toobit"
DEFAULT_LIMIT = 1000
CACHE_DIR = "research/raw"


# =========================
# EXCHANGE SINGLETON
# =========================
_EXCHANGE: Optional[ccxt.Exchange] = None


def _get_exchange(exchange_name: str) -> ccxt.Exchange:
    """
    Initialize and reuse a single CCXT exchange instance.
    """
    global _EXCHANGE
    if _EXCHANGE is None:
        exchange_class = getattr(ccxt, exchange_name)
        _EXCHANGE = exchange_class({
            "enableRateLimit": True,
        })
    return _EXCHANGE


# =========================
# CORE FETCH
# =========================
def fetch_symbol_data(
    symbol: str,
    timeframe: str = DEFAULT_TIMEFRAME,
    exchange_name: str = DEFAULT_EXCHANGE,
    limit: int = DEFAULT_LIMIT,
    since: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Fetch OHLCV data using CCXT.

    Invariants:
    - timestamps are UTC
    - data sorted by time
    - LAST BAR IS ALWAYS DROPPED (no incomplete candle risk)
    - deterministic historical window if `since` is provided

    Requirements: 1.1, 1.2, 1.4
    """
    ex = _get_exchange(exchange_name)

    fetch_kwargs = {
        "symbol": symbol,
        "timeframe": timeframe,
        "limit": limit,
    }

    # 🔒 OPTIONAL but CRITICAL for research determinism
    if since is not None:
        if not isinstance(since, pd.Timestamp):
            raise TypeError("since must be pandas.Timestamp")
        fetch_kwargs["since"] = int(since.timestamp() * 1000)

    try:
        ohlcv = ex.fetch_ohlcv(**fetch_kwargs)
    except Exception:
        # research-only: fail closed
        return pd.DataFrame()

    if not ohlcv:
        return pd.DataFrame()

    df = pd.DataFrame(
        ohlcv,
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )

    # UTC, timezone-aware
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

    # Enforce ordering
    df = df.sort_values("timestamp").reset_index(drop=True)

    # 🚨 CRITICAL RULE:
    # CCXT does NOT guarantee the last candle is closed.
    # Always drop the last bar, unconditionally.
    if len(df) > 1:
        df = df.iloc[:-1].reset_index(drop=True)

    return df


# =========================
# PARQUET CACHE
# =========================
def cache_to_parquet(
    data: pd.DataFrame,
    symbol: str,
    cache_dir: str = CACHE_DIR,
) -> None:
    """
    Cache OHLCV data to parquet (per symbol).
    """
    if data.empty:
        return

    os.makedirs(cache_dir, exist_ok=True)
    fname = symbol.replace("/", "_") + ".parquet"
    path = os.path.join(cache_dir, fname)

    data.to_parquet(path, index=False, engine="pyarrow")


def load_cached_data(
    symbol: str,
    cache_dir: str = CACHE_DIR,
) -> pd.DataFrame:
    """
    Load cached OHLCV data from parquet.
    """
    fname = symbol.replace("/", "_") + ".parquet"
    path = os.path.join(cache_dir, fname)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_parquet(path, engine="pyarrow")
        return df.sort_values("timestamp").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


# =========================
# IMPORT SAFETY
# =========================
if __name__ == "__main__":
    # Intentionally empty.
    # This module is NOT meant to be executed as a script.
    pass
