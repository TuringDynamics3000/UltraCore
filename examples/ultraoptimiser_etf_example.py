"""
UltraOptimiser with Real ETF Data - Example Usage
Demonstrates portfolio optimization using real ASX ETF historical data
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ultracore.domains.wealth.integration import UltraOptimiserAdapter, ETFDataProvider
from ultracore.domains.wealth.integration.ultraoptimiser_adapter import OptimisationService


class MockOptimisationService(OptimisationService):
    """Mock service for demonstration"""
    async def optimize(self, **kwargs):
        return {"status": "mock"}


async def main():
    """Main example function"""
    
    print("=" * 70)
    print("UltraOptimiser with Real ETF Data - Example")
    print("=" * 70)
    print("")
    
    # Initialize UltraOptimiser with ETF data
    print("1. Initializing UltraOptimiser with ETF data provider...")
    mock_service = MockOptimisationService()
    optimiser = UltraOptimiserAdapter(
        optimiser=mock_service,
        etf_data_dir="/tmp/etf_data_example"  # Use demo data directory
    )
    print("   ✅ UltraOptimiser initialized with real market data")
    print("")
    
    # Example 1: Optimize a new portfolio
    print("2. Optimizing a new portfolio (Medium risk, 10 year horizon)...")
    print("")
    
    current_holdings = {}  # Starting from scratch
    available_cash = Decimal("100000")  # $100,000 to invest
    
    result = await optimiser.optimize_portfolio(
        risk_tolerance="medium",
        time_horizon_years=10,
        current_holdings=current_holdings,
        available_cash=available_cash
    )
    
    print("   📊 Optimization Results:")
    print(f"   Expected Return: {result['expected_return']:.2%} p.a.")
    print(f"   Volatility: {result['expected_volatility']:.2%}")
    print(f"   Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    print(f"   Optimization Score: {result['optimization_score']:.1f}")
    print("")
    
    print("   🎯 Target Allocation:")
    for ticker, weight in sorted(result['target_allocation'].items(), key=lambda x: x[1], reverse=True):
        amount = float(available_cash) * weight
        print(f"      {ticker:6s}: {weight:6.2%}  (${amount:,.0f})")
    print("")
    
    print("   💰 Recommended Trades:")
    for trade in result['recommended_trades']:
        print(f"      {trade['action'].upper():4s} {trade['ticker']:6s}: ${trade['amount']:,.0f}")
    print("")
    
    # Example 2: Get portfolio analytics for existing holdings
    print("3. Analyzing existing portfolio...")
    print("")
    
    existing_holdings = {
        "VAS": Decimal("30000"),   # $30k in Vanguard Australian Shares
        "VGS": Decimal("40000"),   # $40k in Vanguard International Shares
        "VAF": Decimal("20000"),   # $20k in Vanguard Fixed Interest
        "VHY": Decimal("10000"),   # $10k in Vanguard High Yield
    }
    
    analytics = optimiser.get_portfolio_analytics(existing_holdings)
    
    print("   📊 Portfolio Analytics:")
    print(f"   Total Value: ${analytics['total_value']:,.0f}")
    print(f"   Expected Return: {analytics['expected_return']:.2%} p.a.")
    print(f"   Volatility: {analytics['volatility']:.2%}")
    print(f"   Sharpe Ratio: {analytics['sharpe_ratio']:.2f}")
    if analytics.get('diversification_score'):
        print(f"   Diversification Score: {analytics['diversification_score']:.1f}/100")
    print("")
    
    print("   📈 Current Allocation:")
    for ticker, weight in sorted(analytics['weights'].items(), key=lambda x: x[1], reverse=True):
        print(f"      {ticker:6s}: {weight:6.2%}")
    print("")
    
    print("   ⚠️  Risk Metrics by Holding:")
    for ticker, metrics in analytics['risk_metrics_by_holding'].items():
        print(f"      {ticker}:")
        print(f"         Volatility: {metrics['volatility']:.2%}")
        print(f"         Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"         Max Drawdown: {metrics['max_drawdown']:.2%}")
    print("")
    
    # Example 3: Check if rebalancing is needed
    print("4. Checking if rebalancing is needed...")
    print("")
    
    # Simulate some drift in allocation
    current_allocation = {
        "VAS": Decimal("0.35"),   # Drifted from 30% to 35%
        "VGS": Decimal("0.35"),   # Drifted from 40% to 35%
        "VAF": Decimal("0.20"),   # Still at 20%
        "VHY": Decimal("0.10"),   # Still at 10%
    }
    
    target_allocation = {
        "VAS": Decimal("0.30"),
        "VGS": Decimal("0.40"),
        "VAF": Decimal("0.20"),
        "VHY": Decimal("0.10"),
    }
    
    rebalance_check = await optimiser.check_rebalancing_needed(
        current_allocation=current_allocation,
        target_allocation=target_allocation,
        threshold=Decimal("0.05")  # 5% threshold
    )
    
    print(f"   Needs Rebalancing: {'Yes' if rebalance_check['needs_rebalancing'] else 'No'}")
    print(f"   Threshold: {rebalance_check['threshold']:.1%}")
    print(f"   Recommendation: {rebalance_check['recommendation']}")
    print("")
    
    print("   📊 Drift Details:")
    for asset, details in rebalance_check['drift_details'].items():
        print(f"      {asset}:")
        print(f"         Current: {details['current']:.2%}")
        print(f"         Target: {details['target']:.2%}")
        print(f"         Drift: {details['drift']:.2%}")
    print("")
    
    # Example 4: Compare different risk profiles
    print("5. Comparing different risk profiles...")
    print("")
    
    risk_profiles = ["low", "medium", "high"]
    
    for risk in risk_profiles:
        result = await optimiser.optimize_portfolio(
            risk_tolerance=risk,
            time_horizon_years=10,
            current_holdings={},
            available_cash=Decimal("100000")
        )
        
        print(f"   {risk.upper()} Risk Profile:")
        print(f"      Expected Return: {result['expected_return']:.2%}")
        print(f"      Volatility: {result['expected_volatility']:.2%}")
        print(f"      Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"      Top 3 Holdings:")
        
        sorted_allocation = sorted(
            result['target_allocation'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for ticker, weight in sorted_allocation:
            print(f"         {ticker}: {weight:.2%}")
        print("")
    
    # Example 5: Using ETF Data Provider directly
    print("6. Using ETF Data Provider directly for analysis...")
    print("")
    
    etf_data = ETFDataProvider(data_dir="/tmp/etf_data_example")
    
    # Get available ETFs
    available_etfs = etf_data.get_available_etfs()
    print(f"   Available ETFs: {len(available_etfs)}")
    print(f"   Sample: {', '.join(available_etfs[:10])}")
    print("")
    
    # Get correlation matrix for diversification analysis
    test_etfs = ["VAS", "VGS", "VAF"]
    
    print(f"   Correlation Matrix for {', '.join(test_etfs)}:")
    corr_matrix = etf_data.calculate_correlation_matrix(test_etfs, lookback_years=3)
    
    if not corr_matrix.empty:
        print(corr_matrix.to_string())
    else:
        print("   (No data available - run ETF data initialization first)")
    print("")
    
    # Summary
    print("=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)
    print("")
    print("📚 Key Features Demonstrated:")
    print("   1. Portfolio optimization with real market data")
    print("   2. Portfolio analytics and risk metrics")
    print("   3. Rebalancing recommendations")
    print("   4. Risk profile comparison")
    print("   5. Direct ETF data access")
    print("")
    print("🚀 Next Steps:")
    print("   1. Initialize ETF data: python -m ultracore.market_data.etf.cli initialize")
    print("   2. Integrate with your UltraWealth application")
    print("   3. Set up daily data updates for fresh market data")
    print("   4. Build custom optimization strategies")
    print("")


if __name__ == "__main__":
    asyncio.run(main())
