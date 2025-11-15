# UltraCore Financial Data MCP Server

## Overview

A **Model Context Protocol (MCP) server** providing unified access to financial data for the UltraCore/UltraWealth system.

## Features

✅ **Multi-Source Support** - Extensible architecture for multiple data providers  
✅ **10 MCP Tools** - ETF data, market prices, portfolio optimization  
✅ **137 ASX ETFs** - Complete historical data (10 years daily)  
✅ **Portfolio Analytics** - Risk metrics, optimization, efficient frontier  
✅ **UltraOptimiser Integration** - RL-based portfolio optimization  
✅ **Caching** - Efficient data access from Parquet files  

## Installation

```bash
# Install MCP SDK
pip install mcp

# Clone/pull UltraCore
cd UltraCore
git pull origin main

# Test the server
python test_mcp_server.py
```

## Usage

### Starting the Server

```bash
# Run directly
python src/ultracore/mcp/server.py

# Or via manus-mcp-cli
manus-mcp-cli server add ultracore-financial-data python src/ultracore/mcp/server.py
```

### Available Tools

#### 1. ETF Data Tools

**`get_etf_data`** - Get historical OHLCV data
```json
{
  "ticker": "VAS",
  "period": "5y"
}
```

**`get_multiple_etfs`** - Get data for multiple ETFs
```json
{
  "tickers": ["VAS", "VGS", "VTS"],
  "period": "1y"
}
```

**`get_etf_info`** - Get ETF metadata
```json
{
  "ticker": "VAS"
}
```

**`get_latest_price`** - Get current price
```json
{
  "ticker": "VAS"
}
```

**`get_market_snapshot`** - Get prices for multiple ETFs
```json
{
  "tickers": ["VAS", "VGS", "VTS", "VAF"]
}
```

**`list_available_etfs`** - List all available ETFs
```json
{}
```

#### 2. Portfolio Tools

**`calculate_portfolio_metrics`** - Calculate risk/return metrics
```json
{
  "tickers": ["VAS", "VGS", "VTS", "VAF"],
  "weights": [0.25, 0.25, 0.25, 0.25],
  "lookback_years": 5
}
```

**`optimize_portfolio`** - Optimize portfolio allocation
```json
{
  "tickers": ["VAS", "VGS", "VTS", "VAF"],
  "objective": "sharpe",
  "risk_budget": 0.15,
  "lookback_years": 5
}
```

**`calculate_efficient_frontier`** - Calculate efficient frontier
```json
{
  "tickers": ["VAS", "VGS", "VTS", "VAF"],
  "n_portfolios": 100,
  "lookback_years": 5
}
```

**`rebalance_portfolio`** - Calculate rebalancing trades
```json
{
  "current_holdings": {"VAS": 100, "VGS": 50},
  "target_weights": {"VAS": 0.6, "VGS": 0.4},
  "total_value": 20000
}
```

## Using with manus-mcp-cli

```bash
# Add server
manus-mcp-cli server add ultracore-financial-data python src/ultracore/mcp/server.py

# List tools
manus-mcp-cli tool list -s ultracore-financial-data

# Call a tool
manus-mcp-cli tool call -s ultracore-financial-data get_latest_price '{"ticker": "VAS"}'

# Get ETF data
manus-mcp-cli tool call -s ultracore-financial-data get_etf_data '{"ticker": "VAS", "period": "1y"}'

# Optimize portfolio
manus-mcp-cli tool call -s ultracore-financial-data optimize_portfolio '{
  "tickers": ["VAS", "VGS", "VTS", "VAF"],
  "objective": "sharpe",
  "risk_budget": 0.15
}'
```

## Architecture

```
ultracore/mcp/
├── server.py              # Main MCP server
├── tools/
│   ├── etf_data_tools.py  # ETF data access tools
│   └── portfolio_tools.py # Portfolio analytics tools
├── sources/
│   ├── base_source.py     # Abstract data source
│   └── yahoo_source.py    # Yahoo Finance source
├── resources/             # MCP resources (future)
├── prompts/               # MCP prompts (future)
└── cache/                 # Caching layer (future)
```

## Data Sources

### Currently Implemented

**Yahoo Finance (via Manus API)**
- 137 ASX ETFs
- 10 years daily data
- OHLCV + volume
- Local Parquet cache

### Future Sources

- Alpha Vantage (real-time quotes)
- ASX Official (corporate actions)
- Custom APIs (broker integrations)

## Integration with UltraCore

The MCP server integrates with:

✅ **Data Mesh** - ETF data from Parquet files  
✅ **ETF Data Provider** - Portfolio optimization  
✅ **UltraOptimiser** - RL-based optimization  
✅ **Event Sourcing** - Audit trail (future)  

## Test Results

```
✅ list_available_etfs - 137 ETFs found
✅ get_etf_info - Metadata retrieved
✅ get_latest_price - Current prices working
✅ get_market_snapshot - Multiple prices working
✅ get_etf_data - Historical data retrieved
✅ calculate_portfolio_metrics - Metrics calculated
✅ optimize_portfolio - Optimization working
```

## Performance

- **Local cache**: Instant access to 137 ETFs
- **Data loading**: <1s for single ETF
- **Portfolio optimization**: 2-5s for 4 ETFs
- **Efficient frontier**: 5-10s for 100 portfolios

## Extending the Server

### Adding a New Data Source

1. Create source class inheriting from `BaseDataSource`
2. Implement required methods:
   - `get_historical_data()`
   - `get_latest_price()`
   - `get_ticker_info()`
3. Register in `server.py`

Example:
```python
from ultracore.mcp.sources.base_source import BaseDataSource

class AlphaVantageSource(BaseDataSource):
    def __init__(self, config):
        super().__init__("alpha_vantage", config)
        self.api_key = config.get('api_key')
    
    def get_historical_data(self, ticker, ...):
        # Implementation
        pass
```

### Adding a New Tool

1. Add method to appropriate tools class
2. Register in `server.py` `list_tools()`
3. Add handler in `call_tool()`

## Troubleshooting

**Issue**: "No data available"  
**Solution**: Ensure ETF data is downloaded to `data/etf/historical/`

**Issue**: "Source not found"  
**Solution**: Check data source configuration in server initialization

**Issue**: "Insufficient data"  
**Solution**: ETF needs at least 252 trading days (1 year) for analytics

## Future Enhancements

- [ ] WebSocket support for real-time data
- [ ] Additional data sources (Alpha Vantage, ASX Official)
- [ ] MCP resources for ETF universe
- [ ] MCP prompts for analysis
- [ ] Caching layer with SQLite
- [ ] Rate limiting per source
- [ ] Data quality monitoring
- [ ] Multi-tenancy support

## License

Part of UltraCore system.

## Support

For issues or questions, see main UltraCore documentation.
