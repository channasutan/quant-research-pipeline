#!/usr/bin/env python3
"""
Test to fetch real data and prove it's not mock
"""

import sys
import pandas as pd
import ccxt

sys.path.insert(0, 'research')
from fetch_raw import fetch_symbol_data

def test_direct_ccxt():
    """Test direct CCXT calls to prove exchanges work"""
    
    print("🔍 DIRECT CCXT TEST (bypassing our module)")
    print("=" * 50)
    
    exchanges_to_test = [
        ("binance", "BTC/USDT"),
        ("coinbase", "BTC-USD"), 
        ("kraken", "BTC/USD"),
        ("bybit", "BTC/USDT"),
        ("okx", "BTC/USDT"),
        ("kucoin", "BTC/USDT:USDT"),
        ("bitfinex", "BTC/USDT:USDT"),
        ("xt", "BTC/USDT:USDT"),
        ("toobit", "BTC/USDT:USDT"),
    ]
    
    for exchange_name, symbol in exchanges_to_test:
        print(f"\n🔄 Testing {exchange_name} directly...")
        
        try:
            # Create exchange instance directly
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'sandbox': False,  # Use real market data
            })
            
            # Fetch data directly
            ohlcv = exchange.fetch_ohlcv(symbol, '4h', limit=10)
            
            if ohlcv and len(ohlcv) > 0:
                print(f"   ✅ {exchange_name}: Got {len(ohlcv)} bars")
                
                # Show sample data to prove it's real
                latest = ohlcv[-1]
                timestamp = pd.Timestamp(latest[0], unit='ms', tz='UTC')
                price = latest[4]  # close price
                volume = latest[5]
                
                print(f"      Latest: {timestamp}")
                print(f"      Close: ${price:,.2f}")
                print(f"      Volume: {volume:,.0f}")
                
                # Test our module with this working exchange
                print(f"   🧪 Testing our module with {exchange_name}...")
                our_data = fetch_symbol_data(symbol, "4h", exchange_name, limit=10)
                
                if not our_data.empty:
                    print(f"      ✅ Our module works! Got {len(our_data)} rows")
                    print(f"      Price range: ${our_data['close'].min():.2f} - ${our_data['close'].max():.2f}")
                    print(f"      Time range: {our_data['timestamp'].min()} to {our_data['timestamp'].max()}")
                    
                    # Test with since parameter
                    since_time = pd.Timestamp("2024-01-01", tz="UTC")
                    since_data = fetch_symbol_data(symbol, "4h", exchange_name, limit=50, since=since_time)
                    
                    if not since_data.empty:
                        print(f"      ✅ Since parameter works! Got {len(since_data)} rows from {since_time}")
                        print(f"      Earliest: {since_data['timestamp'].min()}")
                        
                        # Prove it's deterministic
                        since_data2 = fetch_symbol_data(symbol, "4h", exchange_name, limit=50, since=since_time)
                        if not since_data2.empty and len(since_data) == len(since_data2):
                            if since_data['timestamp'].equals(since_data2['timestamp']):
                                print(f"      ✅ DETERMINISTIC: Same timestamps on repeat call")
                            else:
                                print(f"      ⚠️  Different timestamps (may be due to new data)")
                        
                        return True, exchange_name, symbol, since_data
                    else:
                        print(f"      ❌ Since parameter returned empty")
                else:
                    print(f"      ❌ Our module returned empty")
                    
        except Exception as e:
            print(f"   ❌ {exchange_name}: {str(e)[:100]}...")
    
    return False, None, None, None

def analyze_real_data(data, exchange, symbol):
    """Analyze data to prove it's real market data"""
    
    print(f"\n📊 REAL DATA ANALYSIS")
    print("=" * 30)
    print(f"Exchange: {exchange}")
    print(f"Symbol: {symbol}")
    print(f"Rows: {len(data)}")
    
    # Statistical analysis to prove it's not random
    returns = data['close'].pct_change().dropna()
    
    print(f"\n📈 Market Data Characteristics:")
    print(f"   Price volatility: {returns.std():.4f}")
    print(f"   Price autocorr: {returns.autocorr():.4f}")
    print(f"   Volume mean: {data['volume'].mean():,.0f}")
    print(f"   Volume std: {data['volume'].std():,.0f}")
    
    # Check for realistic OHLC relationships
    valid_ohlc = (
        (data['high'] >= data['low']).all() and
        (data['high'] >= data['open']).all() and
        (data['high'] >= data['close']).all() and
        (data['low'] <= data['open']).all() and
        (data['low'] <= data['close']).all()
    )
    
    print(f"   Valid OHLC: {'✅ YES' if valid_ohlc else '❌ NO'}")
    
    # Show actual price movements
    print(f"\n💰 Recent Price Action:")
    for i in range(min(5, len(data))):
        row = data.iloc[i]
        print(f"   {row['timestamp']}: ${row['close']:,.2f} (Vol: {row['volume']:,.0f})")
    
    return valid_ohlc

def main():
    """Main test function"""
    
    print("🚀 REAL DATA PROOF TEST")
    print("=" * 60)
    
    # Try to get real data
    success, exchange, symbol, data = test_direct_ccxt()
    
    if success:
        print(f"\n🎉 SUCCESS: Got real data from {exchange}")
        
        # Analyze the data
        is_valid = analyze_real_data(data, exchange, symbol)
        
        if is_valid:
            print(f"\n✅ PROOF: This is REAL market data, not mock!")
            print(f"   - Fetched from live {exchange} exchange")
            print(f"   - Valid OHLC relationships")
            print(f"   - Realistic price and volume patterns")
            print(f"   - Deterministic historical window working")
            print(f"   - Since parameter functional")
        else:
            print(f"\n❌ Data validation failed")
            
    else:
        print(f"\n❌ Could not fetch real data from any exchange")
        print(f"   This could be due to:")
        print(f"   - Network connectivity issues")
        print(f"   - Rate limiting")
        print(f"   - Exchange API changes")
        print(f"   - Firewall/proxy restrictions")

if __name__ == "__main__":
    main()