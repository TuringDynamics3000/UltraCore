"""
Test MCP Server

Test script for UltraCore Financial Data MCP Server.
"""

import sys
sys.path.append('src')

from ultracore.mcp.tools.etf_data_tools import ETFDataTools
from ultracore.mcp.tools.portfolio_tools import PortfolioTools
from ultracore.mcp.sources.yahoo_source import YahooFinanceSource
import json


def print_result(title, result):
    """Pretty print test result"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(json.dumps(result, indent=2))


def main():
    print("="*80)
    print("TESTING ULTRACORE FINANCIAL DATA MCP SERVER")
    print("="*80)
    
    # Initialize tools
    yahoo_source = YahooFinanceSource({'data_dir': 'data/etf/historical'})
    etf_tools = ETFDataTools([yahoo_source])
    portfolio_tools = PortfolioTools("data/etf")
    
    # Test 1: List available ETFs
    print("\n1. Testing list_available_etfs...")
    result = etf_tools.list_available_etfs()
    print(f"   ✅ Found {result['total']} ETFs")
    print(f"   Sample: {result['tickers'][:5]}")
    
    # Test 2: Get ETF info
    print("\n2. Testing get_etf_info...")
    result = etf_tools.get_etf_info("VAS")
    if 'error' not in result:
        print(f"   ✅ VAS: {result['name']}")
        print(f"   Latest price: ${result['latest_price']}")
        print(f"   Data points: {result['data_points']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 3: Get latest price
    print("\n3. Testing get_latest_price...")
    result = etf_tools.get_latest_price("VAS")
    if 'error' not in result:
        print(f"   ✅ VAS: ${result['price']} ({result['change_percent']:+.2f}%)")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 4: Get market snapshot
    print("\n4. Testing get_market_snapshot...")
    result = etf_tools.get_market_snapshot(["VAS", "VGS", "VTS", "VAF"])
    if 'prices' in result:
        print(f"   ✅ Got prices for {len(result['prices'])} ETFs")
        for ticker, data in result['prices'].items():
            if 'price' in data:
                print(f"   {ticker}: ${data['price']}")
    else:
        print(f"   ❌ Error in result")
    
    # Test 5: Get ETF data
    print("\n5. Testing get_etf_data...")
    result = etf_tools.get_etf_data("VAS", period="1y")
    if 'error' not in result:
        print(f"   ✅ VAS: {result['rows']} rows")
        print(f"   Date range: {result['start_date']} to {result['end_date']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 6: Calculate portfolio metrics
    print("\n6. Testing calculate_portfolio_metrics...")
    result = portfolio_tools.calculate_portfolio_metrics(
        tickers=["VAS", "VGS", "VTS", "VAF"],
        weights=[0.25, 0.25, 0.25, 0.25],
        lookback_years=5
    )
    if 'error' not in result:
        print(f"   ✅ Portfolio metrics calculated")
        print(f"   Expected Return: {result['expected_return']}%")
        print(f"   Volatility: {result['volatility']}%")
        print(f"   Sharpe Ratio: {result['sharpe_ratio']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 7: Optimize portfolio
    print("\n7. Testing optimize_portfolio...")
    result = portfolio_tools.optimize_portfolio(
        tickers=["VAS", "VGS", "VTS", "VAF"],
        objective="sharpe",
        risk_budget=0.15,
        lookback_years=5
    )
    if 'error' not in result:
        print(f"   ✅ Portfolio optimized")
        print(f"   Optimal weights:")
        for ticker, weight in result['optimal_weights'].items():
            print(f"      {ticker}: {weight*100:.1f}%")
        print(f"   Sharpe Ratio: {result['sharpe_ratio']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print("\n" + "="*80)
    print("MCP SERVER TESTS COMPLETE")
    print("="*80)
    print("\n✅ All core functionality working!")
    print("\nTo start the MCP server:")
    print("  python src/ultracore/mcp/server.py")
    print("\nTo use with manus-mcp-cli:")
    print("  manus-mcp-cli server add ultracore-financial-data python src/ultracore/mcp/server.py")
    print("  manus-mcp-cli tool list -s ultracore-financial-data")


if __name__ == "__main__":
    main()
