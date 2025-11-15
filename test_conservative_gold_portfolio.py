#!/usr/bin/env python3
"""
Conservative Portfolio Optimization with GOLD Diversifier
Target: 10% Volatility
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ultracore.domains.wealth.integration.etf_data_provider import ETFDataProvider
import pandas as pd

print("=" * 80)
print("Conservative Portfolio Optimization - 10% Volatility Target with GOLD")
print("=" * 80)
print()

# Initialize
data_provider = ETFDataProvider(data_dir="data/etf")

# Portfolio candidates including GOLD as diversifier
portfolio_etfs = ['VAS', 'VGS', 'VTS', 'VAF', 'VGB', 'GOLD', 'BILL']

print("Portfolio Candidates:")
for etf in portfolio_etfs:
    print(f"  • {etf}")
print()

# Check availability
print("Checking data availability...")
availability = data_provider.check_data_availability(portfolio_etfs)
available = [etf for etf, avail in availability.items() if avail]
print(f"Available: {len(available)}/{len(portfolio_etfs)} ETFs")
print()

if len(available) < 3:
    print("❌ Not enough ETFs available for optimization")
    sys.exit(1)

# Get risk metrics for each ETF
print("Individual ETF Risk Metrics (3-year lookback):")
print("-" * 80)
print(f"{'ETF':<8} {'Return':>10} {'Volatility':>12} {'Sharpe':>8} {'Max DD':>10}")
print("-" * 80)

risk_data = {}
for etf in available:
    try:
        metrics = data_provider.calculate_risk_metrics(etf, lookback_years=3)
        risk_data[etf] = metrics
        print(f"{etf:<8} {metrics['mean_return']*100:>9.2f}% {metrics['volatility']*100:>11.2f}% "
              f"{metrics['sharpe_ratio']:>8.2f} {metrics['max_drawdown']*100:>9.2f}%")
    except Exception as e:
        print(f"{etf:<8} ❌ Error: {e}")

print()

# Correlation matrix
print("Correlation Matrix:")
print("-" * 80)
try:
    corr_matrix = data_provider.calculate_correlation_matrix(available, lookback_years=3)
    print(corr_matrix.round(2).to_string())
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Portfolio Optimization - 10% Volatility Target
print("=" * 80)
print("PORTFOLIO OPTIMIZATION: 10% Volatility Target")
print("=" * 80)
print()

try:
    result = data_provider.optimize_portfolio_mean_variance(
        tickers=available,
        risk_budget=0.10,  # 10% volatility target
        lookback_years=3
    )
    
    print(f"Optimization Status: {'✅ Converged' if result['optimization_success'] else '⚠️ ' + result['optimization_message']}")
    print()
    
    print("Portfolio Metrics:")
    print(f"  Expected Return:  {result['expected_return']*100:>8.2f}% p.a.")
    print(f"  Volatility:       {result['volatility']*100:>8.2f}%")
    print(f"  Sharpe Ratio:     {result['sharpe_ratio']:>8.2f}")
    print()
    
    print("Optimal Asset Allocation:")
    print("-" * 80)
    print(f"{'ETF':<8} {'Weight':>10} {'Expected Contribution':>25}")
    print("-" * 80)
    
    # Sort by weight
    sorted_weights = sorted(result['optimal_weights'].items(), key=lambda x: x[1], reverse=True)
    
    for etf, weight in sorted_weights:
        if weight > 0.001:  # Only show allocations > 0.1%
            contribution = weight * risk_data[etf]['mean_return'] if etf in risk_data else 0
            print(f"{etf:<8} {weight*100:>9.2f}% {contribution*100:>24.2f}%")
    
    print("-" * 80)
    print(f"{'TOTAL':<8} {sum([w for _, w in sorted_weights])*100:>9.2f}%")
    print()
    
    # Analysis
    print("Portfolio Analysis:")
    print("-" * 80)
    
    # Calculate weighted volatility contribution
    weights_dict = result['optimal_weights']
    
    # Diversification
    num_holdings = sum(1 for w in weights_dict.values() if w > 0.01)
    print(f"Number of Holdings: {num_holdings}")
    
    # Concentration
    top3_weight = sum(sorted([w for w in weights_dict.values()], reverse=True)[:3])
    print(f"Top 3 Concentration: {top3_weight*100:.1f}%")
    
    # Asset class breakdown
    equities = sum(weights_dict.get(etf, 0) for etf in ['VAS', 'VGS', 'VTS'])
    bonds = sum(weights_dict.get(etf, 0) for etf in ['VAF', 'VGB', 'BILL'])
    gold = weights_dict.get('GOLD', 0)
    
    print()
    print("Asset Class Breakdown:")
    print(f"  Equities:  {equities*100:>6.2f}%")
    print(f"  Bonds:     {bonds*100:>6.2f}%")
    print(f"  Gold:      {gold*100:>6.2f}%")
    print()
    
    # Risk contribution
    print("Key Insights:")
    if gold > 0.05:
        print(f"  • Gold allocation of {gold*100:.1f}% provides diversification")
        print(f"    (Gold has negative correlation with equities)")
    else:
        print(f"  • Gold not selected (only {gold*100:.1f}% allocation)")
    
    if bonds > 0.5:
        print(f"  • Heavy bond allocation ({bonds*100:.1f}%) for low volatility target")
    
    if equities < 0.3:
        print(f"  • Low equity allocation ({equities*100:.1f}%) limits growth potential")
    
    print()
    
except Exception as e:
    print(f"❌ Optimization failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
