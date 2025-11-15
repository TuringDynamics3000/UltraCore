# UltraOptimiser ETF Data Integration

## Overview

UltraOptimiser now has full access to real ASX ETF historical data for portfolio optimization. This integration combines UltraOptimiser's proven optimization algorithms with comprehensive market data for 200+ Australian ETFs.

## What's New

### Real Market Data

- **Historical prices**: Complete OHLCV data for all ASX ETFs
- **Returns analysis**: Daily, weekly, monthly returns
- **Risk metrics**: Volatility, Sharpe ratio, Sortino ratio, max drawdown
- **Correlations**: Asset correlation matrices for diversification
- **Covariance**: Full covariance matrices for mean-variance optimization

### Enhanced Optimization

- **Data-driven allocation**: Uses real historical returns and volatility
- **Risk-adjusted optimization**: Maximizes Sharpe ratio with actual market data
- **Diversification analysis**: Correlation-based portfolio construction
- **Rebalancing recommendations**: Based on real price movements

## Architecture

```
UltraOptimiser
    ├── UltraOptimiserAdapter
    │   ├── Portfolio optimization logic
    │   ├── Risk tolerance mapping
    │   └── Rebalancing calculations
    │
    └── ETFDataProvider (NEW)
        ├── Historical data access
        ├── Returns calculation
        ├── Risk metrics
        ├── Correlation matrices
        ├── Covariance matrices
        └── Mean-variance optimization
```

## Usage

### Basic Portfolio Optimization

```python
from ultracore.domains.wealth.integration import UltraOptimiserAdapter
from decimal import Decimal

# Initialize with ETF data
optimiser = UltraOptimiserAdapter(
    optimiser=your_optimisation_service,
    etf_data_dir="/data/etf"
)

# Optimize portfolio
result = await optimiser.optimize_portfolio(
    risk_tolerance="medium",      # low, medium, high
    time_horizon_years=10,
    current_holdings={},          # Empty for new portfolio
    available_cash=Decimal("100000")
)

# Results include:
print(result['expected_return'])      # 8.5% p.a.
print(result['expected_volatility'])  # 12.3%
print(result['sharpe_ratio'])         # 0.71
print(result['target_allocation'])    # {'VAS': 0.30, 'VGS': 0.40, ...}
print(result['recommended_trades'])   # [{'ticker': 'VAS', 'action': 'buy', ...}]
```

### Portfolio Analytics

```python
# Analyze existing portfolio
holdings = {
    "VAS": Decimal("30000"),
    "VGS": Decimal("40000"),
    "VAF": Decimal("20000"),
    "VHY": Decimal("10000"),
}

analytics = optimiser.get_portfolio_analytics(holdings)

# Get comprehensive metrics
print(analytics['expected_return'])        # Expected annual return
print(analytics['volatility'])             # Portfolio volatility
print(analytics['sharpe_ratio'])           # Risk-adjusted return
print(analytics['diversification_score'])  # 0-100 score
print(analytics['risk_metrics_by_holding']) # Individual ETF metrics
print(analytics['correlation_matrix'])      # Asset correlations
```

### Rebalancing Check

```python
# Check if rebalancing is needed
rebalance = await optimiser.check_rebalancing_needed(
    current_allocation=current_weights,
    target_allocation=target_weights,
    threshold=Decimal("0.05")  # 5% drift threshold
)

if rebalance['needs_rebalancing']:
    print("Rebalancing recommended!")
    print(rebalance['drift_details'])
```

### Direct ETF Data Access

```python
from ultracore.domains.wealth.integration import ETFDataProvider

# Initialize data provider
etf_data = ETFDataProvider(data_dir="/data/etf")

# Get returns for multiple ETFs
returns_df = etf_data.get_returns(
    tickers=["VAS", "VGS", "IVV"],
    start_date=date(2021, 1, 1),
    end_date=date.today()
)

# Calculate expected returns
expected_returns = etf_data.calculate_expected_returns(
    tickers=["VAS", "VGS", "IVV"],
    method="historical_mean",
    lookback_years=3
)

# Get correlation matrix
corr_matrix = etf_data.calculate_correlation_matrix(
    tickers=["VAS", "VGS", "IVV"],
    lookback_years=3
)

# Calculate risk metrics
risk_metrics = etf_data.calculate_risk_metrics(
    ticker="VAS",
    lookback_years=3
)
print(risk_metrics['volatility'])      # 15.2%
print(risk_metrics['sharpe_ratio'])    # 0.68
print(risk_metrics['max_drawdown'])    # -18.5%
```

## Features

### 1. Expected Returns Calculation

Multiple methods for estimating future returns:

- **Historical Mean**: Average historical returns (annualized)
- **Exponential Weighted**: More weight on recent data
- **CAPM**: Capital Asset Pricing Model (future enhancement)

```python
expected_returns = etf_data.calculate_expected_returns(
    tickers=["VAS", "VGS"],
    method="historical_mean",
    lookback_years=3
)
# Returns: {'VAS': 0.089, 'VGS': 0.095}  # 8.9%, 9.5% p.a.
```

### 2. Risk Metrics

Comprehensive risk analysis for each ETF:

- **Volatility**: Standard deviation of returns (annualized)
- **Sharpe Ratio**: Risk-adjusted return
- **Sortino Ratio**: Downside risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Value at Risk (VaR)**: 95% confidence loss threshold
- **Conditional VaR (CVaR)**: Expected loss beyond VaR

```python
metrics = etf_data.calculate_risk_metrics("VAS", lookback_years=3)
```

### 3. Correlation Analysis

Understand diversification benefits:

```python
# Correlation matrix
corr = etf_data.calculate_correlation_matrix(
    tickers=["VAS", "VGS", "VAF"],
    lookback_years=3
)

# Example output:
#        VAS    VGS    VAF
# VAS   1.00   0.75   0.15
# VGS   0.75   1.00   0.20
# VAF   0.15   0.20   1.00
```

Low correlation (< 0.5) = good diversification

### 4. Mean-Variance Optimization

Modern Portfolio Theory implementation:

```python
result = etf_data.optimize_portfolio_mean_variance(
    tickers=["VAS", "VGS", "VAF", "VHY"],
    target_return=0.08,      # Optional: target 8% return
    risk_budget=0.15,        # Optional: max 15% volatility
    lookback_years=3
)

# Returns optimal weights that maximize Sharpe ratio
print(result['optimal_weights'])    # {'VAS': 0.30, 'VGS': 0.40, ...}
print(result['sharpe_ratio'])       # 0.71
```

### 5. Efficient Frontier

Generate data for efficient frontier visualization:

```python
frontier = etf_data.get_efficient_frontier_data(
    tickers=["VAS", "VGS", "VAF"],
    lookback_years=3,
    num_portfolios=1000
)

# Plot efficient frontier
import matplotlib.pyplot as plt
plt.scatter(
    frontier['volatilities'],
    frontier['returns'],
    c=frontier['sharpe_ratios'],
    cmap='viridis'
)
plt.xlabel('Volatility')
plt.ylabel('Expected Return')
plt.colorbar(label='Sharpe Ratio')
plt.show()
```

## Risk Tolerance Mapping

UltraOptimiser maps risk tolerance to appropriate ETF universes:

### Low Risk (Conservative)
- **Risk Budget**: 30% volatility
- **ETFs**: VAS, VGB, VAF, VHY
- **Focus**: Capital preservation, income
- **Expected Return**: 6-8% p.a.
- **Typical Allocation**: 60% bonds, 40% defensive equities

### Medium Risk (Balanced)
- **Risk Budget**: 60% volatility
- **ETFs**: VAS, VGS, VGE, VDHG, IOZ, VGB, VAF, VHY
- **Focus**: Growth with downside protection
- **Expected Return**: 8-10% p.a.
- **Typical Allocation**: 60% equities, 40% bonds

### High Risk (Growth)
- **Risk Budget**: 90% volatility
- **ETFs**: VGS, VGE, VDHG, IOZ, NDQ, ASIA, HACK, VAS
- **Focus**: Maximum growth
- **Expected Return**: 10-12% p.a.
- **Typical Allocation**: 90%+ equities, international exposure

## Integration with UltraWealth

### Investment Pods

```python
from ultracore.domains.wealth.models import InvestmentPod

# Create investment pod
pod = InvestmentPod.create(
    tenant_id="tenant_123",
    name="Growth Portfolio",
    risk_tolerance="high",
    time_horizon_years=15
)

# Optimize with real data
optimiser = UltraOptimiserAdapter(
    optimiser=optimisation_service,
    etf_data_dir="/data/etf"
)

result = await optimiser.optimize_portfolio(
    risk_tolerance=pod.risk_tolerance,
    time_horizon_years=pod.time_horizon_years,
    current_holdings=pod.get_current_holdings(),
    available_cash=pod.available_cash
)

# Apply optimization
pod.apply_optimization(result)
```

### Anya Wealth Agent

```python
from ultracore.domains.wealth.agents import AnyaWealthAgent

# Anya can now use real market data for recommendations
agent = AnyaWealthAgent(
    optimiser_adapter=optimiser,
    etf_data_provider=etf_data
)

# Get personalized recommendations
recommendations = await agent.recommend_portfolio(
    user_profile=user_profile,
    current_holdings=current_holdings
)
```

## Data Requirements

### Initial Setup

1. **Initialize ETF data system**:
   ```bash
   python -m ultracore.market_data.etf.cli initialize
   ```

2. **This downloads**:
   - Complete historical data for 200+ ASX ETFs
   - OHLCV data (Open, High, Low, Close, Volume)
   - As far back as available (typically 5-15 years)

3. **Storage**:
   - Default: `/data/etf/`
   - ~10-50 MB per ETF
   - Total: ~2-5 GB for all ETFs

### Daily Updates

Set up automatic updates:

```bash
# Option 1: Run scheduler
python -m ultracore.market_data.etf.cli scheduler

# Option 2: Cron job (Linux/Mac)
0 18 * * * cd /path/to/ultracore && python -m ultracore.market_data.etf.cli update

# Option 3: Windows Task Scheduler
# See ETF_QUICKSTART.md for PowerShell commands
```

## Performance

### Optimization Speed

- **Single portfolio optimization**: ~0.5-1 second
- **Portfolio analytics**: ~0.2-0.5 seconds
- **Efficient frontier (1000 portfolios)**: ~2-3 seconds
- **Rebalancing check**: ~0.1 seconds

### Data Access

- **Returns calculation**: ~0.05 seconds per ETF
- **Risk metrics**: ~0.1 seconds per ETF
- **Correlation matrix**: ~0.2 seconds for 10 ETFs
- **Covariance matrix**: ~0.3 seconds for 10 ETFs

### Caching

ETFDataProvider includes caching for frequently accessed data:
- Returns DataFrames
- Correlation matrices
- Risk metrics

## Examples

### Example 1: New Portfolio for Young Investor

```python
# 25-year-old, high risk tolerance, long time horizon
result = await optimiser.optimize_portfolio(
    risk_tolerance="high",
    time_horizon_years=40,
    current_holdings={},
    available_cash=Decimal("50000")
)

# Typical result:
# - 70% international equities (VGS, VGE)
# - 20% Australian equities (VAS, IOZ)
# - 10% growth sectors (NDQ, HACK)
# - Expected return: 10-12% p.a.
# - Volatility: 16-18%
```

### Example 2: Retiree Portfolio

```python
# 65-year-old, low risk tolerance, income focus
result = await optimiser.optimize_portfolio(
    risk_tolerance="low",
    time_horizon_years=20,
    current_holdings={},
    available_cash=Decimal("500000")
)

# Typical result:
# - 60% bonds (VGB, VAF)
# - 30% defensive equities (VHY, VAS)
# - 10% cash
# - Expected return: 6-7% p.a.
# - Volatility: 8-10%
```

### Example 3: Rebalancing Existing Portfolio

```python
# Current holdings drifted from target
current = {
    "VAS": Decimal("40000"),  # Was 30%
    "VGS": Decimal("30000"),  # Was 40%
    "VAF": Decimal("20000"),  # Was 20%
    "VHY": Decimal("10000"),  # Was 10%
}

# Re-optimize
result = await optimiser.optimize_portfolio(
    risk_tolerance="medium",
    time_horizon_years=10,
    current_holdings=current,
    available_cash=Decimal("0")
)

# Get specific trades needed
trades = result['recommended_trades']
# [
#   {'ticker': 'VAS', 'action': 'sell', 'amount': 10000},
#   {'ticker': 'VGS', 'action': 'buy', 'amount': 10000}
# ]
```

## Troubleshooting

### Issue: "No ETF data available"

**Solution**: Initialize the ETF data system first:
```bash
python -m ultracore.market_data.etf.cli initialize
```

### Issue: "Optimization returns default values"

**Cause**: ETF data not found or insufficient history

**Solution**:
1. Check data directory: `/data/etf/parquet/`
2. Verify ETF tickers are correct (must include .AX suffix in data)
3. Re-run data collection for specific ETFs

### Issue: "Correlation matrix is empty"

**Cause**: Insufficient overlapping data for ETFs

**Solution**:
1. Use ETFs with longer history
2. Reduce `lookback_years` parameter
3. Check data quality: `python -m ultracore.market_data.etf.cli status`

## Best Practices

### 1. Data Freshness

- Update ETF data daily after market close (6 PM AEST)
- Use recent data (3 years) for optimization
- Longer history (5+ years) for risk metrics

### 2. Risk Management

- Always check diversification score (aim for > 60)
- Monitor correlation between holdings (aim for < 0.7)
- Set appropriate rebalancing thresholds (5-10%)

### 3. Optimization

- Use 3-year lookback for most optimizations
- Consider exponential weighting for volatile markets
- Validate results with efficient frontier visualization

### 4. Rebalancing

- Check quarterly for drift
- Rebalance if allocation drift > 5%
- Consider tax implications before selling

## Future Enhancements

- [ ] Real-time price updates
- [ ] Options data integration
- [ ] Fundamental analysis (P/E, dividends)
- [ ] News sentiment integration
- [ ] Machine learning return predictions
- [ ] Backtesting framework
- [ ] Transaction cost modeling
- [ ] Tax optimization

## API Reference

See the following files for detailed API documentation:

- `src/ultracore/domains/wealth/integration/etf_data_provider.py`
- `src/ultracore/domains/wealth/integration/ultraoptimiser_adapter.py`
- `src/ultracore/market_data/etf/data_mesh/etf_data_product.py`

## Support

For issues or questions:
- Documentation: This file + `ETF_DATA_SYSTEM.md`
- Examples: `examples/ultraoptimiser_etf_example.py`
- GitHub Issues: https://github.com/TuringDynamics3000/UltraCore/issues

---

**Built with ❤️ integrating UltraOptimiser with real ASX ETF market data**
