#!/usr/bin/env python3
"""
Test Yahoo Finance Direct Access with VPN

This script tests if the standard yfinance library works now that
you have a VPN enabled. If successful, you'll have the option to use
either the Manus API or direct yfinance access.

Run this script from your local machine (not Manus sandbox) to test.
"""

import sys
from datetime import datetime

print("=" * 80)
print("Yahoo Finance Direct Access Test (with VPN)")
print("=" * 80)
print(f"Test time: {datetime.now()}")
print()

# Check if yfinance is installed
try:
    import yfinance as yf
    print("✅ yfinance library found")
except ImportError:
    print("❌ yfinance not installed")
    print("\nInstall with: pip install yfinance")
    sys.exit(1)

print()
print("-" * 80)
print("Testing ASX ETF data access...")
print("-" * 80)

# Test ETFs
test_etfs = [
    'IOZ.AX',   # iShares Core S&P/ASX 200 ETF
    'STW.AX',   # SPDR S&P/ASX 200 Fund
    'VAS.AX',   # Vanguard Australian Shares Index ETF
    'A200.AX',  # BetaShares Australia 200 ETF
    'NDQ.AX'    # BetaShares NASDAQ 100 ETF
]

results = {
    'success': [],
    'failed': [],
    'errors': {}
}

for i, symbol in enumerate(test_etfs, 1):
    print(f"\n[{i}/{len(test_etfs)}] Testing {symbol}...")
    
    try:
        # Download data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="max")
        
        if hist.empty:
            print(f"  ❌ FAILED: No data returned")
            results['failed'].append(symbol)
            results['errors'][symbol] = "No data returned"
        else:
            # Get info
            info = ticker.info
            name = info.get('longName', 'N/A')
            
            print(f"  ✅ SUCCESS!")
            print(f"     Name: {name}")
            print(f"     Data points: {len(hist)}")
            print(f"     Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
            print(f"     Latest close: ${hist['Close'].iloc[-1]:.2f}")
            
            results['success'].append({
                'symbol': symbol,
                'name': name,
                'data_points': len(hist),
                'start_date': str(hist.index[0].date()),
                'end_date': str(hist.index[-1].date())
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ FAILED: {error_msg}")
        results['failed'].append(symbol)
        results['errors'][symbol] = error_msg

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total tested: {len(test_etfs)}")
print(f"Successful: {len(results['success'])}")
print(f"Failed: {len(results['failed'])}")
print(f"Success rate: {len(results['success'])/len(test_etfs)*100:.1f}%")

if results['success']:
    print("\n✅ Successfully accessed ETFs:")
    for etf in results['success']:
        print(f"  - {etf['symbol']}: {etf['data_points']} data points")

if results['failed']:
    print(f"\n❌ Failed ETFs:")
    for symbol in results['failed']:
        print(f"  - {symbol}: {results['errors'][symbol]}")

# Conclusion
print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if len(results['success']) == len(test_etfs):
    print("🎉 VPN WORKS! You can now use yfinance directly!")
    print("\nYou have TWO options for data collection:")
    print("  1. Manus Yahoo Finance API (already implemented)")
    print("  2. Direct yfinance (now works with VPN)")
    print("\nBoth are free and will work for your needs.")
elif len(results['success']) > 0:
    print("⚠️  PARTIAL SUCCESS - VPN helps but some issues remain")
    print(f"   {len(results['success'])}/{len(test_etfs)} ETFs accessible")
    print("\nRecommendation: Use Manus API for reliability")
else:
    print("❌ VPN DID NOT RESOLVE THE ISSUE")
    print("\nYahoo Finance is still blocking requests.")
    print("Recommendation: Continue using Manus Yahoo Finance API")

print("\n" + "=" * 80)

# Save results
import json
with open('yfinance_vpn_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: yfinance_vpn_test_results.json")

sys.exit(0 if len(results['success']) > 0 else 1)
