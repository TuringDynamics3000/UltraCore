# UltraCore Financial Data MCP Server

## Overview

A **Model Context Protocol (MCP) server** that provides unified access to financial data from multiple sources for the UltraCore/UltraWealth system.

## Architecture

### Multi-Source Design

```
┌─────────────────────────────────────────────────────────┐
│         UltraCore Financial Data MCP Server             │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │           MCP Protocol Interface                 │   │
│  │  (Tools, Resources, Prompts)                    │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Data Source Abstraction Layer            │   │
│  │  (Unified interface for all data sources)       │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                 │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐│
│  │  Yahoo   │  Alpha   │  ASX     │  Custom  │ Future ││
│  │  Finance │  Vantage │  Official│  APIs    │ Sources││
│  └──────────┴──────────┴──────────┴──────────┴────────┘│
└─────────────────────────────────────────────────────────┘
```

### Data Sources (Extensible)

#### Currently Implemented
1. **Yahoo Finance (via Manus API)**
   - ASX ETF historical data
   - Daily OHLCV data
   - 10 years history

#### Planned Data Sources
2. **Alpha Vantage**
   - Real-time quotes
   - Fundamental data
   - Technical indicators

3. **ASX Official Data**
   - Corporate actions
   - Dividend announcements
   - Index constituents

4. **Alternative Data**
   - News sentiment
   - Social media sentiment
   - Economic indicators

5. **Custom APIs**
   - Broker integrations (OpenMarkets)
   - Internal databases
   - Proprietary data

## MCP Tools

### Category 1: ETF Data Tools

#### `get_etf_data`
Get historical OHLCV data for an ETF.

**Input:**
```json
{
  "ticker": "VAS",
  "start_date": "2020-01-01",
  "end_date": "2025-01-01",
  "source": "yahoo"  // optional, defaults to best available
}
```

**Output:**
```json
{
  "ticker": "VAS",
  "data": [...],  // OHLCV data
  "source": "yahoo",
  "rows": 1260
}
```

#### `get_multiple_etfs`
Get data for multiple ETFs at once.

**Input:**
```json
{
  "tickers": ["VAS", "VGS", "VTS"],
  "period": "5y",
  "source": "yahoo"
}
```

#### `get_etf_info`
Get metadata about an ETF.

**Input:**
```json
{
  "ticker": "VAS"
}
```

**Output:**
```json
{
  "ticker": "VAS",
  "name": "Vanguard Australian Shares Index ETF",
  "issuer": "Vanguard",
  "inception_date": "2009-05-08",
  "aum": "12.5B",
  "expense_ratio": "0.10%",
  "benchmark": "S&P/ASX 300"
}
```

### Category 2: Market Data Tools

#### `get_latest_price`
Get current/latest price for an ETF.

**Input:**
```json
{
  "ticker": "VAS"
}
```

**Output:**
```json
{
  "ticker": "VAS",
  "price": 107.41,
  "change": 0.52,
  "change_percent": 0.49,
  "timestamp": "2025-11-15T16:00:00Z"
}
```

#### `get_market_snapshot`
Get current prices for multiple ETFs.

**Input:**
```json
{
  "tickers": ["VAS", "VGS", "VTS", "VAF"]
}
```

### Category 3: Portfolio Analytics Tools

#### `calculate_portfolio_metrics`
Calculate risk/return metrics for a portfolio.

**Input:**
```json
{
  "tickers": ["VAS", "VGS", "VTS"],
  "weights": [0.4, 0.3, 0.3],
  "lookback_years": 5
}
```

**Output:**
```json
{
  "expected_return": 0.12,
  "volatility": 0.18,
  "sharpe_ratio": 0.65,
  "max_drawdown": -0.15,
  "correlation_matrix": [[...]]
}
```

#### `optimize_portfolio`
Optimize portfolio allocation using UltraOptimiser.

**Input:**
```json
{
  "tickers": ["VAS", "VGS", "VTS", "VAF"],
  "objective": "sharpe",  // or "volatility", "income", "alpha"
  "risk_budget": 0.15,
  "constraints": {
    "min_weight": 0.0,
    "max_weight": 0.5
  }
}
```

**Output:**
```json
{
  "optimal_weights": {
    "VAS": 0.25,
    "VGS": 0.35,
    "VTS": 0.30,
    "VAF": 0.10
  },
  "expected_return": 0.14,
  "volatility": 0.15,
  "sharpe_ratio": 0.91
}
```

### Category 4: RL Agent Tools

#### `get_rl_agent_recommendation`
Get portfolio recommendation from trained RL agent.

**Input:**
```json
{
  "agent": "alpha",  // alpha, beta, gamma, delta
  "tickers": ["VAF", "VAS"],
  "initial_capital": 15000,
  "market_conditions": {...}
}
```

**Output:**
```json
{
  "agent": "alpha",
  "recommended_weights": {
    "VAF": 0.70,
    "VAS": 0.30
  },
  "confidence": 0.85,
  "expected_volatility": 0.12
}
```

### Category 5: Data Source Management

#### `list_data_sources`
List all available data sources.

**Output:**
```json
{
  "sources": [
    {
      "name": "yahoo",
      "status": "active",
      "coverage": ["ASX", "US"],
      "rate_limit": "2000/day"
    },
    {
      "name": "alpha_vantage",
      "status": "active",
      "coverage": ["global"],
      "rate_limit": "500/day"
    }
  ]
}
```

#### `add_data_source`
Register a new data source.

**Input:**
```json
{
  "name": "custom_api",
  "type": "rest_api",
  "config": {
    "base_url": "https://api.example.com",
    "api_key": "...",
    "rate_limit": 1000
  }
}
```

## MCP Resources

### Resource 1: ETF Universe
**URI:** `etf://universe/asx`

Returns list of all available ASX ETFs.

### Resource 2: Historical Data
**URI:** `etf://data/{ticker}/historical`

Returns historical data for specific ETF.

### Resource 3: Portfolio State
**URI:** `portfolio://state/{portfolio_id}`

Returns current state of a portfolio.

## MCP Prompts

### Prompt 1: Analyze ETF
**Name:** `analyze_etf`

**Arguments:**
- `ticker`: ETF ticker symbol
- `analysis_type`: "fundamental", "technical", "risk"

**Returns:** Detailed analysis report

### Prompt 2: Compare ETFs
**Name:** `compare_etfs`

**Arguments:**
- `tickers`: List of ETF tickers
- `metrics`: List of comparison metrics

**Returns:** Comparative analysis

### Prompt 3: Portfolio Recommendation
**Name:** `recommend_portfolio`

**Arguments:**
- `risk_profile`: "conservative", "balanced", "growth"
- `goals`: List of financial goals
- `capital`: Initial capital amount

**Returns:** Recommended portfolio allocation

## Implementation Details

### Technology Stack
- **Language:** Python 3.11+
- **MCP SDK:** `mcp` Python package
- **Data:** Pandas, NumPy
- **Storage:** Parquet files + SQLite cache
- **API:** FastAPI for REST endpoints

### File Structure
```
src/ultracore/mcp/
├── __init__.py
├── server.py                 # Main MCP server
├── tools/
│   ├── __init__.py
│   ├── etf_data_tools.py    # ETF data tools
│   ├── market_tools.py       # Market data tools
│   ├── portfolio_tools.py    # Portfolio analytics
│   └── rl_agent_tools.py     # RL agent tools
├── resources/
│   ├── __init__.py
│   └── etf_resources.py      # MCP resources
├── prompts/
│   ├── __init__.py
│   └── analysis_prompts.py   # MCP prompts
├── sources/
│   ├── __init__.py
│   ├── base_source.py        # Abstract data source
│   ├── yahoo_source.py       # Yahoo Finance
│   ├── alpha_vantage_source.py
│   └── asx_official_source.py
└── cache/
    ├── __init__.py
    └── data_cache.py          # Caching layer
```

### Configuration
```yaml
# mcp_config.yaml
server:
  name: "ultracore-financial-data"
  version: "1.0.0"
  port: 8080

data_sources:
  yahoo:
    enabled: true
    priority: 1
    cache_ttl: 3600
  
  alpha_vantage:
    enabled: false
    api_key: ${ALPHA_VANTAGE_API_KEY}
    priority: 2
  
  asx_official:
    enabled: false
    priority: 3

cache:
  enabled: true
  backend: "sqlite"
  path: "data/cache/mcp_cache.db"
  max_size_mb: 1000

rate_limiting:
  enabled: true
  requests_per_minute: 60
```

## Benefits

### 1. **Unified Interface**
- Single API for all financial data
- Consistent data format
- Standardized error handling

### 2. **Multi-Source Support**
- Easy to add new data sources
- Automatic failover between sources
- Source priority configuration

### 3. **Caching & Performance**
- Intelligent caching layer
- Reduced API calls
- Faster response times

### 4. **Extensibility**
- Plugin architecture for new sources
- Custom tools and resources
- Integration with external systems

### 5. **MCP Ecosystem**
- Compatible with MCP clients
- Shareable across applications
- Standard protocol

## Use Cases

### 1. **UltraWealth Portfolio Optimization**
```python
# Get data via MCP
etf_data = mcp_client.call_tool("get_multiple_etfs", {
    "tickers": ["VAS", "VGS", "VTS", "VAF"],
    "period": "5y"
})

# Optimize portfolio
result = mcp_client.call_tool("optimize_portfolio", {
    "tickers": ["VAS", "VGS", "VTS", "VAF"],
    "objective": "sharpe",
    "risk_budget": 0.15
})
```

### 2. **RL Agent Training**
```python
# Get training data from multiple sources
training_data = mcp_client.call_tool("get_etf_data", {
    "ticker": "VAS",
    "period": "10y",
    "source": "best"  # Auto-select best source
})

# Train agent
agent.train(training_data)
```

### 3. **Real-Time Portfolio Monitoring**
```python
# Get latest prices
prices = mcp_client.call_tool("get_market_snapshot", {
    "tickers": portfolio.tickers
})

# Calculate current value
portfolio.update_prices(prices)
```

## Next Steps

1. ✅ Design architecture (DONE)
2. ⏭️ Implement base MCP server
3. ⏭️ Implement Yahoo Finance source
4. ⏭️ Implement ETF data tools
5. ⏭️ Implement portfolio analytics tools
6. ⏭️ Add caching layer
7. ⏭️ Test with UltraCore
8. ⏭️ Document API
9. ⏭️ Deploy to production

## Future Enhancements

- WebSocket support for real-time data
- GraphQL interface
- Multi-tenancy support
- Advanced caching strategies
- Data quality monitoring
- Cost tracking per source
- A/B testing for data sources
