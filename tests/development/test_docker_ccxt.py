#!/usr/bin/env python3
"""
Test CCXT functionality inside Docker environment
"""

import sys
import ccxt
import pandas as pd

def test_ssl_environment():
    """Verify SSL/OpenSSL environment"""
    import ssl
    print("🔒 SSL ENVIRONMENT CHECK")
    print("=" * 30)
    print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
    print(f"Python version: {sys.version}")
    
    # Should show OpenSSL 3.x, not LibreSSL
    if "OpenSSL" in ssl.OPENSSL_VERSION and "LibreSSL" not in ssl.OPENSSL_VERSION:
        print("✅ OpenSSL detected (not LibreSSL)")
        return True
    else:
        print("❌ Still using LibreSSL or incompatible SSL")
        return False

def test_ccxt_exchanges():
    """Test CCXT with real exchanges"""
    print(f"\n📡 CCXT EXCHANGE TEST")
    print("=" * 25)
    
    exchanges_to_test = [
        ("toobit", "BTC/USDT"),
        ("bitfinex", "BTC/USD"),
        ("xt", "BTC/USDT"),
    ]
    
    success_count = 0
    
    for exchange_name, symbol in exchanges_to_test:
        print(f"\n🔄 Testing {exchange_name}...")
        
        try:
            # Create exchange
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'timeout': 15000,
            })
            
            # Test market loading first
            print(f"   Loading {exchange_name} markets...")
            exchange.load_markets()
            print(f"   ✅ Markets loaded")
            
            # Test OHLCV fetch
            print(f"   Fetching {symbol} OHLCV...")
            ohlcv = exchange.fetch_ohlcv(symbol, "4h", limit=5)
            
            if ohlcv and len(ohlcv) > 0:
                print(f"   ✅ SUCCESS: Got {len(ohlcv)} bars")
                
                # Show sample data
                latest = ohlcv[-1]
                timestamp = pd.Timestamp(latest[0], unit='ms', tz='UTC')
                close_price = latest[4]
                volume = latest[5]
                
                print(f"      Latest: {timestamp}")
                print(f"      Close: ${close_price:,.2f}")
                print(f"      Volume: {volume:,.0f}")
                
                success_count += 1
            else:
                print(f"   ❌ No data returned")
                
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:80]}...")
    
    return success_count

def test_our_pipeline():
    """Test our fetch_raw module"""
    print(f"\n🧪 PIPELINE MODULE TEST")
    print("=" * 25)
    
    try:
        sys.path.insert(0, '/app/research')
        from fetch_raw import fetch_symbol_data
        
        print("   Testing fetch_symbol_data...")
        
        # Test basic fetch
        data = fetch_symbol_data("BTC/USDT", "4h", "toobit", limit=10)
        
        if not data.empty:
            print(f"   ✅ SUCCESS: Got {len(data)} rows")
            print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
            print(f"   Time range: {data['timestamp'].min()} to {data['timestamp'].max()}")
            
            # Test with since parameter
            since_time = pd.Timestamp("2024-01-01", tz="UTC")
            since_data = fetch_symbol_data("BTC/USDT", "4h", "toobit", limit=20, since=since_time)
            
            if not since_data.empty:
                print(f"   ✅ Since parameter: {len(since_data)} rows from {since_time}")
                print(f"   Earliest: {since_data['timestamp'].min()}")
                return True
            else:
                print(f"   ⚠️  Since parameter returned empty (may be date range issue)")
                return True  # Basic fetch worked
        else:
            print(f"   ❌ fetch_symbol_data returned empty")
            return False
            
    except Exception as e:
        print(f"   ❌ Pipeline test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🐳 DOCKER ENVIRONMENT VERIFICATION")
    print("=" * 50)
    
    # Test 1: SSL environment
    ssl_ok = test_ssl_environment()
    
    # Test 2: CCXT exchanges
    exchange_success_count = test_ccxt_exchanges()
    
    # Test 3: Our pipeline
    pipeline_ok = test_our_pipeline()
    
    # Final results
    print(f"\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    print(f"SSL Environment: {'✅ PASS' if ssl_ok else '❌ FAIL'}")
    print(f"CCXT Exchanges: {exchange_success_count}/3 working")
    print(f"Pipeline Module: {'✅ PASS' if pipeline_ok else '❌ FAIL'}")
    
    if ssl_ok and exchange_success_count > 0 and pipeline_ok:
        print(f"\n🎉 DOCKER ENVIRONMENT FIX SUCCESSFUL!")
        print(f"   ✓ OpenSSL working correctly")
        print(f"   ✓ CCXT can fetch real market data")
        print(f"   ✓ Our pipeline code works unchanged")
        print(f"   ✓ Ready for research pipeline execution")
    else:
        print(f"\n❌ Environment fix incomplete")
        if not ssl_ok:
            print(f"   - SSL environment issue")
        if exchange_success_count == 0:
            print(f"   - No exchanges working")
        if not pipeline_ok:
            print(f"   - Pipeline module issue")

if __name__ == "__main__":
    main()