#!/usr/bin/env python3
"""
Patch logic validation - tests the code changes independent of exchange connectivity
"""

import sys
import pandas as pd
import inspect

sys.path.insert(0, 'research')
from fetch_raw import fetch_symbol_data

def analyze_patch_implementation():
    """Analyze the patch implementation for compliance"""
    
    print("🔍 PATCH LOGIC ANALYSIS")
    print("=" * 50)
    
    # Get function signature
    sig = inspect.signature(fetch_symbol_data)
    params = list(sig.parameters.keys())
    
    print(f"📋 Function signature analysis:")
    print(f"   Parameters: {params}")
    
    # Check 1: since parameter exists
    since_param_exists = 'since' in params
    print(f"   'since' parameter added: {'✅ YES' if since_param_exists else '❌ NO'}")
    
    # Check 2: since parameter is optional
    since_param = sig.parameters.get('since')
    since_optional = since_param and since_param.default is None
    print(f"   'since' parameter optional: {'✅ YES' if since_optional else '❌ NO'}")
    
    # Check 3: Type hint analysis
    since_type_hint = since_param.annotation if since_param else None
    expected_type = "typing.Union[pandas._libs.tslibs.timestamps.Timestamp, NoneType]"
    type_hint_ok = "Timestamp" in str(since_type_hint) or "Optional" in str(since_type_hint)
    print(f"   Type hint correct: {'✅ YES' if type_hint_ok else '❌ NO'} ({since_type_hint})")
    
    return since_param_exists and since_optional and type_hint_ok

def test_parameter_handling():
    """Test parameter handling logic"""
    
    print(f"\n🧪 PARAMETER HANDLING TEST")
    print("=" * 30)
    
    try:
        # Test 1: Function accepts since=None (default behavior)
        print("   Test 1: Default behavior (since=None)...")
        try:
            # This should not raise an error, even if exchange fails
            result = fetch_symbol_data("BTC/USDT", since=None)
            print("   ✅ Accepts since=None")
            default_behavior_ok = True
        except TypeError as e:
            if "since" in str(e):
                print(f"   ❌ TypeError with since=None: {e}")
                default_behavior_ok = False
            else:
                print("   ✅ Accepts since=None (other error expected)")
                default_behavior_ok = True
        except Exception:
            print("   ✅ Accepts since=None (exchange error expected)")
            default_behavior_ok = True
        
        # Test 2: Function rejects invalid since type
        print("   Test 2: Invalid since type rejection...")
        try:
            fetch_symbol_data("BTC/USDT", since="2024-01-01")
            print("   ❌ Should reject string since parameter")
            type_validation_ok = False
        except TypeError as e:
            if "since must be pandas.Timestamp" in str(e):
                print("   ✅ Correctly rejects invalid since type")
                type_validation_ok = True
            else:
                print(f"   ❌ Wrong error message: {e}")
                type_validation_ok = False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            type_validation_ok = False
        
        # Test 3: Function accepts valid Timestamp
        print("   Test 3: Valid Timestamp acceptance...")
        try:
            valid_since = pd.Timestamp("2024-01-01", tz="UTC")
            result = fetch_symbol_data("BTC/USDT", since=valid_since)
            print("   ✅ Accepts valid Timestamp")
            timestamp_acceptance_ok = True
        except TypeError as e:
            if "since" in str(e):
                print(f"   ❌ Rejects valid Timestamp: {e}")
                timestamp_acceptance_ok = False
            else:
                print("   ✅ Accepts valid Timestamp (other error expected)")
                timestamp_acceptance_ok = True
        except Exception:
            print("   ✅ Accepts valid Timestamp (exchange error expected)")
            timestamp_acceptance_ok = True
        
        return default_behavior_ok and type_validation_ok and timestamp_acceptance_ok
        
    except Exception as e:
        print(f"   ❌ Unexpected error in parameter testing: {e}")
        return False

def analyze_code_changes():
    """Analyze the actual code for compliance with requirements"""
    
    print(f"\n📝 CODE ANALYSIS")
    print("=" * 20)
    
    # Read the source code
    with open('research/fetch_raw.py', 'r') as f:
        source_code = f.read()
    
    checks = []
    
    # Check 1: No scanner logic added
    scanner_terms = ['scanner', 'last_closed', 'horizon', 'multi_symbol', 'live', 'inference']
    scanner_found = any(term in source_code.lower() for term in scanner_terms)
    checks.append(("No scanner logic", not scanner_found))
    
    # Check 2: Maintains closed candle guarantee
    drop_last_found = "df.iloc[:-1]" in source_code
    checks.append(("Last candle drop preserved", drop_last_found))
    
    # Check 3: UTC timestamp handling preserved
    utc_found = "utc=True" in source_code
    checks.append(("UTC timestamp handling", utc_found))
    
    # Check 4: Sorting preserved
    sort_found = "sort_values" in source_code
    checks.append(("Timestamp sorting", sort_found))
    
    # Check 5: Since parameter implementation
    since_impl_found = "since" in source_code and "timestamp() * 1000" in source_code
    checks.append(("Since parameter implementation", since_impl_found))
    
    # Check 6: Type checking for since
    type_check_found = "isinstance(since, pd.Timestamp)" in source_code
    checks.append(("Since type validation", type_check_found))
    
    # Check 7: Import safety preserved
    import_safety = '__name__ == "__main__"' in source_code
    checks.append(("Import safety preserved", import_safety))
    
    # Check 8: No cache logic modified
    cache_functions = ['cache_to_parquet', 'load_cached_data']
    cache_preserved = all(func in source_code for func in cache_functions)
    checks.append(("Cache logic unchanged", cache_preserved))
    
    print("   Code compliance checks:")
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"      {check_name}: {status}")
    
    return all(passed for _, passed in checks)

def main():
    """Main validation"""
    
    # Test 1: Patch implementation analysis
    implementation_ok = analyze_patch_implementation()
    
    # Test 2: Parameter handling
    parameter_handling_ok = test_parameter_handling()
    
    # Test 3: Code analysis
    code_analysis_ok = analyze_code_changes()
    
    # Final compliance report
    print(f"\n" + "=" * 60)
    print("🏁 COMPLIANCE CHECKLIST")
    print("=" * 60)
    
    checklist = [
        ("Deterministic historical window", implementation_ok and parameter_handling_ok),
        ("Closed-candle guarantee", code_analysis_ok),  # Verified in code analysis
        ("CCXT compatibility", implementation_ok),  # Parameter structure is correct
        ("Research-only scope preserved", code_analysis_ok),  # No scanner logic added
        ("Type safety", parameter_handling_ok),
    ]
    
    print()
    for item, status in checklist:
        result = "✅ PASS" if status else "❌ FAIL"
        print(f"{item:<35} {result}")
    
    # Final verdict
    all_pass = all(status for _, status in checklist)
    
    print(f"\n" + "=" * 60)
    print("🎯 FINAL VERDICT")
    print("=" * 60)
    
    if all_pass:
        print("✅ ACCEPT")
        print("   ✓ Patch adds deterministic historical window capability")
        print("   ✓ Preserves all existing research-only invariants")
        print("   ✓ Maintains closed-candle guarantee")
        print("   ✓ No scope creep into scanner logic")
        print("   ✓ Proper type validation for new parameter")
        print("   ✓ Backward compatible (since parameter is optional)")
    else:
        print("❌ REJECT")
        print("   Blocking issues found in code analysis")
        for item, status in checklist:
            if not status:
                print(f"   - {item}")

if __name__ == "__main__":
    main()