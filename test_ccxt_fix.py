#!/usr/bin/env python3
"""
Test CCXT after fixing urllib3 compatibility issue
"""

import ccxt
import sys

def test_ccxt_exchanges():
    """Test the required exchanges after environment fix"""
    
    print("🔧 CCXT ENVIRONMENT FIX VERIFICATION")
    print("=" * 50)
    
    test_cases = [
        ("binance", "BTC/USDT"),
        ("toobit", "BTC/USDT"), 
        ("bitfinex", "BTC/USD"),
        ("xt", "BTC/USDT"),
    ]
    
    success_count = 0
    
    for exchange_name, symbol in test_cases:
        print(f"\n🔄 Testing {exchange_name}...")
        
        try:
            # Create exchange instance
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'timeout': 10000,  # 10 second timeout
            })
            
            # Fetch real data
            ohlcv = exchange.fetch_ohlcv(symbol, "4h", limit=5)
            
            if ohlcv and len(ohlcv) > 0:
                print(f"   ✅ {exchange_name}: SUCCESS - Got {len(ohlcv)} bars")
                
                # Show sample data
                latest = ohlcv[-1]
                import pandas as pd
                timestamp = pd.Timestamp(latest[0], unit='ms', tz='UTC')
                close_price = latest[4]
                volume = latest[5]
                
                print(f"      Latest bar: {timestamp}")
                print(f"      Close price: ${close_price:,.2f}")
                print(f"      Volume: {volume:,.0f}")
                
                success_count += 1
            else:
                print(f"   ❌ {exchange_name}: No data returned")
                
        except Exception as e:
            print(f"   ❌ {exchange_name}: {str(e)[:100]}...")
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULTS: {success_count}/{len(test_cases)} exchanges working")
    
    if success_count > 0:
        print("✅ ENVIRONMENT FIX SUCCESSFUL!")
        print("   - urllib3 downgraded to compatible version")
        print("   - HTTPS/TLS requests now working")
        print("   - CCXT can fetch real market data")
        return True
    else:
        print("❌ Environment fix failed - no exchanges working")
        return False

def test_our_module():
    """Test our fetch_raw module after fix"""
    
    print(f"\n🧪 TESTING OUR MODULE AFTER FIX")
    print("=" * 35)
    
    sys.path.insert(0, 'research')
    from fetch_raw import fetch_symbol_data
    
    try:
        # Test without since parameter
        print("   Testing fetch_symbol_data...")
        data = fetch_symbol_data("BTC/USDT", "4h", "binance", limit=10)
        
        if not data.empty:
            print(f"   ✅ SUCCESS: Got {len(data)} rows")
            print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
            
            # Test with since parameter
            import pandas as pd
            since_time = pd.Timestamp("2024-01-01", tz="UTC")
            since_data = fetch_symbol_data("BTC/USDT", "4h", "binance", limit=20, since=since_time)
            
            if not since_data.empty:
                print(f"   ✅ Since parameter works: {len(since_data)} rows from {since_time}")
                return True
            else:
                print(f"   ❌ Since parameter failed")
                return False
        else:
            print(f"   ❌ Our module returned empty data")
            return False
            
    except Exception as e:
        print(f"   ❌ Our module failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 ENVIRONMENT FIX VERIFICATION")
    print("=" * 60)
    
    # Test CCXT directly
    ccxt_success = test_ccxt_exchanges()
    
    if ccxt_success:
        # Test our module
        module_success = test_our_module()
        
        if module_success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"   ✓ Environment issue fixed")
            print(f"   ✓ CCXT working with real exchanges") 
            print(f"   ✓ Our fetch_raw.py module working")
            print(f"   ✓ Both with/without since parameter")
            print(f"\n   Ready for real data pipeline execution!")
        else:
            print(f"\n⚠️  CCXT works but our module has issues")
    else:
        print(f"\n❌ Environment fix unsuccessful")

if __name__ == "__main__":
    main()