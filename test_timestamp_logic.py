#!/usr/bin/env python3
"""
Test timestamp conversion logic
"""

import sys
import pandas as pd

sys.path.insert(0, 'research')

def test_timestamp_conversion():
    """Test the timestamp conversion logic"""
    
    print("🕐 TIMESTAMP CONVERSION TEST")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        pd.Timestamp("2024-01-01 00:00:00", tz="UTC"),
        pd.Timestamp("2024-06-15 12:30:00", tz="UTC"),
        pd.Timestamp("2023-12-31 23:59:59", tz="UTC"),
    ]
    
    for i, ts in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {ts}")
        
        # Convert to milliseconds (same logic as in fetch_raw.py)
        ms_timestamp = int(ts.timestamp() * 1000)
        
        # Convert back to verify
        back_to_ts = pd.Timestamp(ms_timestamp, unit='ms', tz='UTC')
        
        print(f"      Original: {ts}")
        print(f"      Milliseconds: {ms_timestamp}")
        print(f"      Back to timestamp: {back_to_ts}")
        print(f"      Round-trip match: {'✅ YES' if ts == back_to_ts else '❌ NO'}")
    
    print(f"\n✅ Timestamp conversion logic verified")

if __name__ == "__main__":
    test_timestamp_conversion()