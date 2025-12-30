#!/usr/bin/env python3
"""
Phase 3: Live CCXT fetch test in GitHub Actions.
Minimal isolated test - no scanner, no training, no caching.
"""

import ccxt
import sys

def test_live_ccxt_fetch():
    """Test single live CCXT fetch with minimal data."""
    
    print("🔗 LIVE CCXT FETCH TEST")
    print("=" * 40)
    
    # Print CCXT version
    print(f"CCXT Version: {ccxt.__version__}")
    
    # Test exchange (toobit preferred)
    exchange_name = "toobit"
    symbol = "BTC/USDT"
    timeframe = "4h"
    limit = 5  # Minimal sample
    
    print(f"Exchange: {exchange_name}")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Limit: {limit}")
    
    try:
        # Initialize exchange
        exchange = getattr(ccxt, exchange_name)()
        print(f"✅ Exchange initialized: {exchange.name}")
        
        # Perform live fetch
        print("🔄 Fetching live OHLCV data...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # Print results
        rows_fetched = len(ohlcv)
        print(f"✅ Live fetch successful!")
        print(f"📊 Rows fetched: {rows_fetched}")
        
        if rows_fetched > 0:
            # Show first row as proof
            first_row = ohlcv[0]
            print(f"📈 Sample data: {first_row}")
            
        print(f"\n🎯 SUCCESS: Live CCXT fetch working in GitHub Actions")
        return True
        
    except Exception as e:
        print(f"❌ Live fetch failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def main():
    """Main test execution."""
    
    success = test_live_ccxt_fetch()
    
    if success:
        print(f"\n✅ Phase 3 COMPLETE: Live CCXT connectivity confirmed")
        sys.exit(0)
    else:
        print(f"\n❌ Phase 3 FAILED: Live CCXT connectivity issues")
        sys.exit(1)

if __name__ == "__main__":
    main()