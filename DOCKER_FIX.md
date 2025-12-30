# Docker Environment Fix for SSL/CCXT Issues

## 🔍 Problem Summary

**Root Cause:** macOS system Python (3.9.6) uses LibreSSL 2.8.3, but CCXT requires OpenSSL 1.1.1+ for modern TLS support.

**Symptoms:**
- All CCXT exchanges fail with SSL certificate errors
- `urllib3 v2 only supports OpenSSL 1.1.1+` warnings
- `certificate verify failed: certificate has expired` errors

**Failed Attempts:**
- ❌ Downgrading urllib3 to <2.0
- ❌ Updating certificates with `certifi`
- ❌ Running `/Applications/Python\ 3.x/Install\ Certificates.command`

## 🐳 Docker Solution

**Strategy:** Use Docker with Python 3.11 + OpenSSL 3.x to bypass macOS LibreSSL limitations.

### Files Created

1. **`Dockerfile`** - Minimal Python 3.11 environment
2. **`test_docker_ccxt.py`** - Comprehensive CCXT testing
3. **`docker_setup.sh`** - Setup and usage commands
4. **`verify_docker_solution.py`** - Solution verification

### Quick Start

```bash
# 1. Install Docker Desktop (if not installed)
# Download from: https://www.docker.com/products/docker-desktop

# 2. Build the environment
docker build -t crypto-pipeline .

# 3. Verify SSL fix
docker run --rm crypto-pipeline python -c "import ssl; print('OpenSSL:', ssl.OPENSSL_VERSION)"

# 4. Test CCXT exchanges
docker run --rm -v $(pwd):/app crypto-pipeline python test_docker_ccxt.py

# 5. Test our pipeline
docker run --rm -v $(pwd):/app crypto-pipeline python -c "
import sys; sys.path.insert(0,'/app/research')
from fetch_raw import fetch_symbol_data
data = fetch_symbol_data('BTC/USDT', '4h', 'toobit', limit=5)
print('✅ Pipeline works:', len(data), 'rows')
"
```

### Expected Results

**Before (macOS Python):**
```
OpenSSL version: LibreSSL 2.8.3
❌ All CCXT exchanges fail with SSL errors
```

**After (Docker Python):**
```
OpenSSL version: OpenSSL 3.0.2 15 Mar 2022
✅ CCXT exchanges work
✅ fetch_symbol_data returns real market data
```

## 🧪 Verification Commands

### Test Individual Exchanges
```bash
# Toobit
docker run --rm -v $(pwd):/app crypto-pipeline python -c "
import ccxt; 
data = ccxt.toobit().fetch_ohlcv('BTC/USDT', '4h', limit=5); 
print('Toobit:', len(data), 'bars')
"

# Bitfinex  
docker run --rm -v $(pwd):/app crypto-pipeline python -c "
import ccxt; 
data = ccxt.bitfinex().fetch_ohlcv('BTC/USD', '4h', limit=5); 
print('Bitfinex:', len(data), 'bars')
"
```

### Test Pipeline Components
```bash
# Test fetch_raw.py
docker run --rm -v $(pwd):/app crypto-pipeline python -c "
import sys; sys.path.insert(0,'/app/research')
from fetch_raw import fetch_symbol_data
data = fetch_symbol_data('BTC/USDT', '4h', 'toobit', limit=10)
print('fetch_raw:', len(data), 'rows')
"

# Test full pipeline
docker run --rm -v $(pwd):/app crypto-pipeline python /app/test_pipeline.py
```

## 📋 Code Unchanged Guarantee

**✅ No modifications to:**
- `research/fetch_raw.py` - All logic preserved
- `research/build_features.py` - Feature engineering unchanged  
- `research/train_model.py` - Training logic unchanged
- `requirements.txt` - Dependencies unchanged

**✅ Pipeline flow preserved:**
```
fetch_raw.py → build_features.py → train_model.py
```

## 🎯 Success Criteria

After running Docker commands:

1. **SSL Environment:** OpenSSL 3.x (not LibreSSL 2.8.3)
2. **CCXT Functionality:** `ccxt.toobit().fetch_ohlcv()` succeeds
3. **Pipeline Module:** `fetch_symbol_data()` returns non-empty DataFrame
4. **Determinism:** `since` parameter works correctly
5. **No Code Changes:** All existing Python files unchanged

## 🚀 Production Usage

For ongoing development:

```bash
# Interactive development
docker run -it --rm -v $(pwd):/app crypto-pipeline bash

# Run specific scripts
docker run --rm -v $(pwd):/app crypto-pipeline python research/fetch_raw.py

# Full pipeline execution
docker run --rm -v $(pwd):/app crypto-pipeline python -c "
import sys; sys.path.insert(0, '/app/research')
from fetch_raw import fetch_symbol_data, cache_to_parquet
from build_features import build_feature_set  
from train_model import prepare_training_data, train_lightgbm_model, export_model_artifacts

# Fetch real data
data = fetch_symbol_data('BTC/USDT', '4h', 'toobit', limit=500)
cache_to_parquet(data, 'BTC/USDT')

# Build features  
features = build_feature_set(data, include_labels=True)

# Train model
X, y = prepare_training_data(features)
model = train_lightgbm_model(X, y)
export_model_artifacts(model, list(X.columns), {'symbol': 'BTC/USDT'})

print('✅ Full pipeline completed with real data')
"
```

This Docker solution provides a clean, reproducible environment that fixes the SSL/OpenSSL compatibility issue without requiring any changes to the existing pipeline code.