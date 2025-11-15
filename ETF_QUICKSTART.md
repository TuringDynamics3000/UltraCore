# ETF Data System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd /home/ubuntu/ultracore-fix
pip install yfinance pandas numpy click
```

### Step 2: Initialize the System

```bash
# Download all historical data for 200+ ASX ETFs
python -m ultracore.market_data.etf.cli initialize

# This will:
# - Download complete historical data for all ASX ETFs
# - Store data in /data/etf/
# - Export to Parquet format
# - Take ~3-5 minutes
```

### Step 3: Check Status

```bash
python -m ultracore.market_data.etf.cli status
```

### Step 4: View Your Data

```bash
# Show data for a specific ETF
python -m ultracore.market_data.etf.cli show VAS

# List all available ETFs
python -m ultracore.market_data.etf.cli list-etfs
```

### Step 5: Export for ML/RL Training

```bash
# Export all ETFs with ML features
python -m ultracore.market_data.etf.cli export --output /data/ml_training

# Export specific ETFs
python -m ultracore.market_data.etf.cli export --tickers VAS,VGS,IVV
```

## 📊 Use in Python

```python
from ultracore.market_data.etf.etf_data_system import get_etf_system

# Get system
system = get_etf_system()

# Get price data
df = system.get_etf_data("VAS", format="dataframe")
print(df.head())

# Get ML features (with technical indicators)
ml_df = system.get_ml_features("VAS", include_technical=True)
print(ml_df.columns)

# Train your model!
X = ml_df[features]
y = ml_df['returns_forward_1']
```

## 🔄 Daily Updates

### Option 1: Manual Update

```bash
python -m ultracore.market_data.etf.cli update
```

### Option 2: Automatic Scheduler

```bash
# Run scheduler (updates daily at 6 PM)
python -m ultracore.market_data.etf.cli scheduler
```

### Option 3: Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (updates at 6 PM daily)
0 18 * * * cd /home/ubuntu/ultracore-fix && python -m ultracore.market_data.etf.cli update
```

## 🎯 Common Use Cases

### 1. Price Prediction

```python
# Get ML features
df = system.get_ml_features("VAS", include_technical=True)

# Features: SMA, EMA, RSI, MACD, Bollinger Bands, lagged prices
# Target: returns_forward_1 (next day return)

from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
model.fit(X_train, y_train)
```

### 2. Portfolio Optimization

```python
# Get data for multiple ETFs
data_product = system.get_data_product()
returns = data_product.get_multi_etf_data(
    tickers=["VAS", "VGS", "IVV", "VAF"],
    column="adj_close"
).pct_change()

# Calculate optimal weights
# Use mean-variance optimization, RL, etc.
```

### 3. Correlation Analysis

```python
# Get returns for multiple ETFs
returns_df = data_product.get_multi_etf_data(
    tickers=["VAS", "VGS", "IVV"],
    column="adj_close"
).pct_change()

# Correlation matrix
corr = returns_df.corr()
print(corr)
```

## 📁 Data Location

```
/data/etf/
├── parquet/          # Parquet files (one per ETF)
│   ├── VAS.parquet
│   ├── VGS.parquet
│   └── ...
└── ml_export/        # ML training exports
    ├── VAS.parquet
    ├── metadata.json
    └── ...
```

## 🔧 Troubleshooting

### Issue: "No module named ultracore"

```bash
# Make sure you're in the right directory
cd /home/ubuntu/ultracore-fix

# Add to PYTHONPATH
export PYTHONPATH=/home/ubuntu/ultracore-fix/src:$PYTHONPATH
```

### Issue: "No data returned"

```bash
# Check internet connection
ping finance.yahoo.com

# Try manual download
python -c "import yfinance as yf; print(yf.download('VAS.AX', period='1d'))"
```

### Issue: "Permission denied"

```bash
# Create data directory with proper permissions
sudo mkdir -p /data/etf
sudo chown $USER:$USER /data/etf
```

## 📚 Learn More

- Full Documentation: `ETF_DATA_SYSTEM.md`
- Example Script: `examples/etf_data_example.py`
- CLI Help: `python -m ultracore.market_data.etf.cli --help`

## 🎉 You're Ready!

You now have:
- ✅ Complete historical data for 200+ ASX ETFs
- ✅ Daily automatic updates
- ✅ ML-ready features and technical indicators
- ✅ Parquet exports for fast loading
- ✅ Event sourcing for complete audit trail

Start building your ML/RL models! 🚀
