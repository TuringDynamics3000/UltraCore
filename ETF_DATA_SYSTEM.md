# ASX ETF Historical Data System

## Overview

A comprehensive system for downloading, storing, and automatically updating complete historical transaction data for all Australian Exchange Traded Funds (ETFs) from Yahoo Finance. Built using UltraCore's Data Mesh, Agentic AI, Event Sourcing, and ML/RL frameworks.

## Features

### 🎯 Core Capabilities

- **Complete Historical Data**: Downloads all available historical OHLCV data for 200+ ASX ETFs
- **Daily Automatic Updates**: Scheduled updates after market close (6 PM AEST)
- **Event Sourcing**: Complete audit trail of all data changes
- **Data Mesh Architecture**: Treats ETF data as a first-class data product
- **Agentic AI**: Autonomous agent manages collection with retry logic and optimization
- **ML/RL Ready**: Pre-computed features and technical indicators for training
- **High Performance**: Parallel processing with batching and caching

### 📊 Data Coverage

- **200+ ASX ETFs** across all categories:
  - Australian Equity (Broad Market, Dividend, Small Cap, Sectors)
  - International Equity (US, Europe, Asia, Emerging Markets)
  - Fixed Income (Australian & International Bonds)
  - Commodities (Gold, Silver, Oil, Agriculture)
  - Currencies (USD, EUR, GBP)
  - Thematic (Technology, Healthcare, ESG, Infrastructure)
  - Leveraged & Inverse
  - Active ETFs

### 🔧 Technical Features

- **OHLCV Data**: Open, High, Low, Close, Adjusted Close, Volume
- **Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, Volume indicators
- **Returns Calculation**: Daily, weekly, monthly returns and log returns
- **Feature Engineering**: Lagged features, momentum indicators, forward returns
- **Multiple Formats**: Parquet, CSV, pandas DataFrame, JSON
- **Data Quality Metrics**: Completeness, timeliness, accuracy tracking

## Architecture

### Components

```
ETF Data System
├── ETF Collector Agent (Agentic AI)
│   ├── Autonomous data collection
│   ├── Retry logic and error handling
│   └── Performance optimization (RL)
│
├── Yahoo Finance Collector (Service)
│   ├── Historical data download
│   ├── Real-time updates
│   └── Metadata extraction
│
├── ETF Aggregate (Event Sourcing)
│   ├── Domain model
│   ├── Event-sourced state
│   └── Complete audit trail
│
├── ETF Data Product (Data Mesh)
│   ├── Data ownership
│   ├── Quality guarantees
│   ├── ML feature generation
│   └── Multiple export formats
│
└── Event Store
    ├── All data changes recorded
    ├── Time-travel queries
    └── Replay capability
```

### Data Flow

```
1. Agent schedules collection
2. Yahoo Finance API called
3. Data validated and transformed
4. Events created and stored
5. Aggregate state updated
6. Data Product refreshed
7. Parquet files exported
8. ML features computed
```

## Installation

### Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies
cd /path/to/UltraCore
pip install -r requirements.txt

# Additional dependencies (if not in requirements.txt)
pip install yfinance pandas numpy click
```

### Setup

```bash
# Navigate to UltraCore directory
cd /home/ubuntu/ultracore-fix

# The system is already integrated into UltraCore
# No additional installation needed
```

## Usage

### Command Line Interface

#### Initialize System (First Time)

```bash
# Download all historical data for all ASX ETFs
python -m ultracore.market_data.etf.cli initialize

# With custom data directory
python -m ultracore.market_data.etf.cli initialize --data-dir /custom/path

# Force re-download
python -m ultracore.market_data.etf.cli initialize --force
```

**Expected Output:**
```
🚀 Initializing ETF Data System...
📁 Data directory: /data/etf
📊 ETFs to collect: 200+

✅ Initialization Complete!
   Total ETFs: 215
   Successful: 210
   Failed: 5
   Data points: 450,000+
   Duration: 180.5s
   Parquet files: 210
```

#### Daily Update

```bash
# Update with latest data
python -m ultracore.market_data.etf.cli update

# Updates last 5 days of data for all ETFs
```

#### Run Scheduler (Continuous)

```bash
# Run scheduler for automatic daily updates
python -m ultracore.market_data.etf.cli scheduler

# Custom update time (default 18:00 AEST)
python -m ultracore.market_data.etf.cli scheduler --time 17:30
```

#### System Status

```bash
# Check system status
python -m ultracore.market_data.etf.cli status
```

**Output:**
```
📊 ETF Data System Status

Initialized: ✅ Yes
Last Update: 2024-11-14T18:30:00
Next Update: 18:00:00
Data Directory: /data/etf

📈 Agent Statistics:
   Total ETFs: 215
   Successful: 210
   Failed: 5
   Success Rate: 97.7%

💾 Data Product Statistics:
   Total ETFs: 210
   Data Points: 456,789
   Avg per ETF: 2,175
   Date Range: 2010-01-01 to 2024-11-14
```

#### View ETF Data

```bash
# Show specific ETF
python -m ultracore.market_data.etf.cli show VAS

# List all ETFs
python -m ultracore.market_data.etf.cli list-etfs
```

#### Export Data

```bash
# Export all ETFs for ML/RL training
python -m ultracore.market_data.etf.cli export

# Export specific ETFs
python -m ultracore.market_data.etf.cli export --tickers VAS,VGS,IVV

# Export single ETF to CSV
python -m ultracore.market_data.etf.cli export-ticker VAS --output vas_data.csv
```

### Python API

#### Basic Usage

```python
from ultracore.market_data.etf.etf_data_system import get_etf_system
import asyncio

# Get system instance
system = get_etf_system(data_dir="/data/etf")

# Initialize (first time only)
result = asyncio.run(system.initialize())

# Update daily
result = asyncio.run(system.update())

# Get system status
status = system.get_system_status()
print(status)
```

#### Access Data

```python
# Get price data as DataFrame
df = system.get_etf_data("VAS", format="dataframe")
print(df.head())

# Get with ML features
df_ml = system.get_ml_features("VAS", include_technical=True)
print(df_ml.columns)

# Get multiple ETFs
data_product = system.get_data_product()
multi_df = data_product.get_multi_etf_data(
    tickers=["VAS", "VGS", "IVV"],
    column="adj_close"
)
```

#### ML/RL Training

```python
# Get ML-ready features
df = system.get_ml_features("VAS", include_technical=True)

# Features included:
# - OHLCV data
# - Returns (daily, log)
# - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
# - Lagged features (1, 2, 3, 5, 10 days)
# - Forward returns (1, 5, 20 days) for targets

# Split for training
train_df = df[:'2023-12-31']
test_df = df['2024-01-01':]

# Features and targets
features = [col for col in df.columns if not col.startswith('returns_forward')]
targets = ['returns_forward_1', 'returns_forward_5', 'returns_forward_20']

X_train = train_df[features].dropna()
y_train = train_df[targets].dropna()
```

#### Export for Training

```python
# Export all data
result = system.export_for_ml(
    output_dir="/data/ml_training",
    tickers=None  # None = all ETFs
)

# Files created:
# /data/ml_training/VAS.parquet
# /data/ml_training/VGS.parquet
# ...
# /data/ml_training/metadata.json
```

### Advanced Usage

#### Custom Agent Configuration

```python
from ultracore.market_data.etf.agents.etf_collector_agent import ETFCollectorAgent
from ultracore.market_data.etf.services.yahoo_finance_collector import YahooFinanceCollector
from ultracore.event_sourcing.in_memory_event_store import InMemoryEventStore

# Create custom agent
event_store = InMemoryEventStore()
collector = YahooFinanceCollector()

agent = ETFCollectorAgent(
    event_store=event_store,
    collector=collector
)

# Configure RL parameters
agent.retry_attempts = 5
agent.retry_delay = 10
agent.batch_size = 20

# Run collection
result = asyncio.run(agent.initialize_all_etfs())
```

#### Data Product Features

```python
from ultracore.market_data.etf.data_mesh.etf_data_product import ETFDataProduct

data_product = ETFDataProduct()

# Add ETFs
for ticker, etf in agent.etf_aggregates.items():
    data_product.add_etf(etf)

# Get returns
returns_df = data_product.get_returns_df("VAS", period="daily")

# Get technical indicators
tech_df = data_product.get_technical_indicators("VAS")

# Calculate data quality
quality = data_product.calculate_data_quality("VAS")
print(f"Quality Score: {quality.overall_score():.2%}")
print(f"Completeness: {quality.completeness:.2%}")
print(f"Timeliness: {quality.timeliness:.1f} hours")
```

## Data Storage

### Directory Structure

```
/data/etf/
├── parquet/              # Parquet files (one per ETF)
│   ├── VAS.parquet
│   ├── VGS.parquet
│   └── ...
├── ml_export/            # ML training exports
│   ├── VAS.parquet
│   ├── metadata.json
│   └── ...
└── events/               # Event store (if file-based)
    └── etf_events.db
```

### Data Formats

#### Parquet Files

Each ETF has a parquet file with:
- Date index
- OHLCV columns
- Technical indicators
- Lagged features
- Forward returns

#### Metadata JSON

```json
{
  "export_date": "2024-11-14T18:30:00",
  "total_etfs": 210,
  "tickers": ["VAS", "VGS", ...],
  "data_product": {
    "total_data_points": 456789,
    "earliest_date": "2010-01-01",
    "latest_date": "2024-11-14"
  }
}
```

## Scheduling

### Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily update at 6 PM
0 18 * * * cd /path/to/ultracore && python -m ultracore.market_data.etf.cli update

# Or run scheduler as service
0 17 * * * cd /path/to/ultracore && python -m ultracore.market_data.etf.cli scheduler &
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/etf-data-system.service
[Unit]
Description=ETF Data System Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ultracore-fix
ExecStart=/usr/bin/python3 -m ultracore.market_data.etf.cli scheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable etf-data-system
sudo systemctl start etf-data-system

# Check status
sudo systemctl status etf-data-system
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 6:00 PM
4. Action: Start a program
   - Program: `python`
   - Arguments: `-m ultracore.market_data.etf.cli update`
   - Start in: `C:\path\to\ultracore`

## ML/RL Training Examples

### Example 1: Price Prediction

```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Get ML features
system = get_etf_system()
df = system.get_ml_features("VAS", include_technical=True)

# Prepare data
features = ['open', 'high', 'low', 'close', 'volume', 
            'sma_20', 'sma_50', 'rsi', 'macd']
target = 'returns_forward_1'

df_clean = df[features + [target]].dropna()

X = df_clean[features]
y = df_clean[target]

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"R² Score: {score:.4f}")
```

### Example 2: Portfolio Optimization (RL)

```python
import gym
from stable_baselines3 import PPO

# Get data for multiple ETFs
data_product = system.get_data_product()
etfs = ["VAS", "VGS", "IVV", "VHY"]

# Create custom gym environment
class PortfolioEnv(gym.Env):
    def __init__(self, etf_data):
        self.etf_data = etf_data
        # Define action and observation space
        self.action_space = gym.spaces.Box(low=0, high=1, shape=(len(etfs),))
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(len(etfs) * 10,))
    
    def step(self, action):
        # Implement portfolio rebalancing logic
        pass
    
    def reset(self):
        # Reset to initial state
        pass

# Train RL agent
env = PortfolioEnv(data_product)
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)
```

### Example 3: Correlation Analysis

```python
# Get data for multiple ETFs
data_product = system.get_data_product()
etfs = ["VAS", "VGS", "IVV", "VHY", "VAF"]

# Get returns
returns_df = data_product.get_multi_etf_data(
    tickers=etfs,
    column="adj_close"
).pct_change()

# Calculate correlation matrix
corr_matrix = returns_df.corr()
print(corr_matrix)

# Visualize
import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title("ETF Correlation Matrix")
plt.show()
```

## Monitoring & Maintenance

### Health Checks

```python
# Check system health
status = system.get_system_status()

if not status['initialized']:
    print("⚠️ System not initialized")

if status['agent_statistics']['success_rate'] < 95:
    print("⚠️ Low success rate")

# Check data quality
for ticker in data_product.get_all_tickers():
    quality = data_product.calculate_data_quality(ticker)
    if quality.overall_score() < 0.8:
        print(f"⚠️ Low quality for {ticker}: {quality.overall_score():.2%}")
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/etf-data-system.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Common Issues

#### 1. Yahoo Finance API Errors

**Problem:** `No data returned from Yahoo Finance`

**Solution:**
- Check internet connection
- Verify ticker format (should have .AX suffix)
- Try manual download: `yfinance.download("VAS.AX")`
- Check if ETF is delisted

#### 2. Missing Data

**Problem:** Gaps in historical data

**Solution:**
- Re-run initialization with `--force`
- Check data quality metrics
- Verify trading days (weekends/holidays have no data)

#### 3. Slow Performance

**Problem:** Collection takes too long

**Solution:**
- Increase batch size: `agent.batch_size = 20`
- Use parallel processing
- Check network speed
- Reduce retry attempts for faster failure

#### 4. Memory Issues

**Problem:** Out of memory errors

**Solution:**
- Process ETFs in smaller batches
- Export to parquet more frequently
- Clear aggregate cache: `agent.etf_aggregates.clear()`

## Performance

### Benchmarks

- **Initial Collection**: ~3-5 minutes for 200+ ETFs
- **Daily Update**: ~1-2 minutes for 200+ ETFs
- **Single ETF**: ~0.5-1 second
- **ML Feature Generation**: ~0.1 second per ETF
- **Parquet Export**: ~0.05 second per ETF

### Optimization Tips

1. **Use Parquet**: 10x faster than CSV, smaller file size
2. **Batch Processing**: Process multiple ETFs in parallel
3. **Caching**: Keep frequently accessed data in memory
4. **Incremental Updates**: Only download recent data
5. **Async Operations**: Use asyncio for I/O-bound tasks

## Future Enhancements

- [ ] Real-time streaming data
- [ ] Additional data sources (ASX direct, Bloomberg)
- [ ] More technical indicators
- [ ] Fundamental data (P/E ratios, dividends)
- [ ] News sentiment analysis
- [ ] Options data
- [ ] Backtesting framework
- [ ] Web dashboard
- [ ] API endpoints (REST/GraphQL)
- [ ] Cloud deployment (AWS/Azure/GCP)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit pull request

## License

Proprietary - UltraCore

## Support

For issues or questions:
- GitHub Issues: https://github.com/TuringDynamics3000/UltraCore/issues
- Documentation: This file
- Contact: info@ultracore.com

---

**Built with ❤️ using UltraCore's Data Mesh, Agentic AI, Event Sourcing, and ML/RL frameworks**
