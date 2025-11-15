"""
ETF Data System - Example Usage
Demonstrates how to use the ETF data system for ML/RL training
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ultracore.market_data.etf.etf_data_system import ETFDataSystem
from ultracore.market_data.etf.asx_etf_list import get_all_etfs


async def main():
    """Main example function"""
    
    print("=" * 60)
    print("ETF Data System - Example Usage")
    print("=" * 60)
    
    # Initialize system
    print("\n1. Initializing ETF Data System...")
    system = ETFDataSystem(data_dir="/tmp/etf_data_example")
    
    # For demo, we'll just test with a few ETFs
    print("\n2. Testing with sample ETFs: VAS, VGS, IVV")
    
    # Get data product
    data_product = system.get_data_product()
    
    # Test data collection for a single ETF
    print("\n3. Collecting data for VAS...")
    from ultracore.market_data.etf.services.yahoo_finance_collector import YahooFinanceCollector
    from ultracore.market_data.etf.aggregates.etf_aggregate import ETFAggregate, ETFMetadata
    
    collector = YahooFinanceCollector()
    
    # Download VAS data
    result = await asyncio.to_thread(
        collector.download_historical_data,
        ticker="VAS",
        period="1y"  # Last 1 year for demo
    )
    
    if result.success:
        print(f"   ✅ Success! Downloaded {result.data_points} data points")
        print(f"   📅 Date range: {result.start_date} to {result.end_date}")
    else:
        print(f"   ❌ Failed: {result.error}")
        return
    
    # Get ETF info
    print("\n4. Getting ETF metadata...")
    info = await asyncio.to_thread(collector.get_etf_info, "VAS")
    
    if info:
        metadata = collector.extract_metadata(info, "VAS")
        print(f"   Name: {metadata.name}")
        print(f"   Issuer: {metadata.issuer}")
        print(f"   Category: {metadata.category}")
    
    # Create ETF aggregate
    print("\n5. Creating ETF aggregate...")
    etf = ETFAggregate.create("VAS", metadata)
    
    # Add to data product
    data_product.add_etf(etf)
    
    # Get price data as DataFrame
    print("\n6. Getting price data as DataFrame...")
    df = data_product.get_price_data_df("VAS")
    
    if not df.empty:
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   First 5 rows:")
        print(df.head())
        print(f"\n   Last 5 rows:")
        print(df.tail())
    
    # Calculate returns
    print("\n7. Calculating returns...")
    returns_df = data_product.get_returns_df("VAS")
    
    if not returns_df.empty:
        print(f"   Average daily return: {returns_df['returns'].mean():.4%}")
        print(f"   Volatility (std): {returns_df['returns'].std():.4%}")
        print(f"   Cumulative return: {returns_df['cumulative_returns'].iloc[-1]:.2%}")
    
    # Get technical indicators
    print("\n8. Calculating technical indicators...")
    tech_df = data_product.get_technical_indicators("VAS")
    
    if not tech_df.empty:
        print(f"   Technical indicators calculated:")
        indicators = [col for col in tech_df.columns if col not in df.columns]
        for ind in indicators[:10]:  # Show first 10
            print(f"      - {ind}")
        if len(indicators) > 10:
            print(f"      ... and {len(indicators) - 10} more")
    
    # Get ML features
    print("\n9. Generating ML features...")
    ml_df = data_product.get_ml_features("VAS", include_technical=True)
    
    if not ml_df.empty:
        print(f"   Total features: {len(ml_df.columns)}")
        print(f"   Rows: {len(ml_df)}")
        print(f"   Features include:")
        print(f"      - Price data (OHLCV)")
        print(f"      - Technical indicators (SMA, EMA, RSI, MACD, BB)")
        print(f"      - Lagged features (1, 2, 3, 5, 10 days)")
        print(f"      - Forward returns (targets for prediction)")
    
    # Export to parquet
    print("\n10. Exporting to Parquet...")
    export_dir = "/tmp/etf_data_example/parquet"
    files = data_product.export_to_parquet(export_dir, tickers=["VAS"])
    
    if files:
        print(f"   ✅ Exported to: {files[0]}")
        
        # Check file size
        file_size = Path(files[0]).stat().st_size
        print(f"   File size: {file_size / 1024:.1f} KB")
    
    # Data quality
    print("\n11. Checking data quality...")
    quality = data_product.calculate_data_quality("VAS")
    
    print(f"   Overall score: {quality.overall_score():.2%}")
    print(f"   Completeness: {quality.completeness:.2%}")
    print(f"   Timeliness: {quality.timeliness:.1f} hours")
    print(f"   Accuracy: {quality.accuracy:.2%}")
    print(f"   Consistency: {quality.consistency:.2%}")
    
    # Summary
    print("\n12. Summary Statistics...")
    summary = data_product.get_summary_statistics()
    
    print(f"   Total ETFs: {summary['total_etfs']}")
    print(f"   Total data points: {summary['total_data_points']}")
    print(f"   Average per ETF: {summary['average_data_points_per_etf']:.0f}")
    
    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)
    
    print("\n📚 Next steps:")
    print("   1. Run full initialization: python -m ultracore.market_data.etf.cli initialize")
    print("   2. Set up daily updates: python -m ultracore.market_data.etf.cli scheduler")
    print("   3. Export for ML training: python -m ultracore.market_data.etf.cli export")
    print("   4. Start building ML/RL models with the data!")


if __name__ == "__main__":
    asyncio.run(main())
