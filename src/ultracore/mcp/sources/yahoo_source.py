"""
Yahoo Finance Data Source

Implementation of Yahoo Finance data source using Manus API.
"""

import sys
sys.path.append('/home/ubuntu/UltraCore/src')

from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

from ultracore.mcp.sources.base_source import BaseDataSource


class YahooFinanceSource(BaseDataSource):
    """
    Yahoo Finance data source using Manus API.
    
    Provides access to ASX ETF data via the Manus Yahoo Finance collector.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Yahoo Finance source"""
        super().__init__("yahoo", config)
        
        # Data directory
        self.data_dir = Path(self.config.get('data_dir', 'data/etf/historical'))
        
        # Lazy load collector
        self._collector = None
    
    @property
    def collector(self):
        """Lazy load Manus Yahoo collector"""
        if self._collector is None:
            try:
                from ultracore.market_data.etf.services.manus_yahoo_collector import ManusYahooCollector
                self._collector = ManusYahooCollector()
            except Exception as e:
                print(f"Warning: Could not load Manus Yahoo collector: {e}")
                self._collector = None
        return self._collector
    
    def get_historical_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data for a ticker.
        
        First tries to load from local Parquet files, falls back to API if needed.
        """
        # Try loading from local cache first
        ticker_clean = ticker.replace('.AX', '')
        parquet_file = self.data_dir / f"{ticker_clean}.parquet"
        
        if parquet_file.exists():
            df = pd.read_parquet(parquet_file)
            
            # Filter by date range if specified
            if start_date:
                df = df[df.index >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df.index <= pd.to_datetime(end_date)]
            
            return df
        
        # Fall back to API if collector available
        if self.collector:
            try:
                ticker_with_suffix = ticker if ticker.endswith('.AX') else f"{ticker}.AX"
                df = self.collector.collect_etf_data(ticker_clean)
                
                if df is not None and not df.empty:
                    # Filter by date range
                    if start_date:
                        df = df[df.index >= pd.to_datetime(start_date)]
                    if end_date:
                        df = df[df.index <= pd.to_datetime(end_date)]
                    
                    return df
            except Exception as e:
                print(f"Error fetching data from API: {e}")
        
        # Return empty DataFrame if all else fails
        return pd.DataFrame()
    
    def get_latest_price(self, ticker: str) -> Dict[str, Any]:
        """Get latest price for a ticker"""
        df = self.get_historical_data(ticker)
        
        if df.empty:
            return {
                'ticker': ticker,
                'price': None,
                'change': None,
                'change_percent': None,
                'timestamp': None,
                'error': 'No data available'
            }
        
        # Get last two rows for change calculation
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest
        
        price = float(latest['Close'])
        prev_price = float(previous['Close'])
        change = price - prev_price
        change_percent = (change / prev_price * 100) if prev_price > 0 else 0
        
        return {
            'ticker': ticker,
            'price': round(price, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'timestamp': str(latest.name),
            'volume': int(latest['Volume']) if 'Volume' in latest else None
        }
    
    def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """Get metadata about a ticker"""
        df = self.get_historical_data(ticker)
        
        if df.empty:
            return {
                'ticker': ticker,
                'error': 'No data available'
            }
        
        # Calculate basic statistics
        returns = df['Close'].pct_change().dropna()
        
        return {
            'ticker': ticker,
            'name': f"{ticker} ETF",  # Could be enhanced with actual name lookup
            'exchange': 'ASX',
            'inception_date': str(df.index[0])[:10] if len(df) > 0 else None,
            'latest_date': str(df.index[-1])[:10] if len(df) > 0 else None,
            'data_points': len(df),
            'latest_price': round(float(df.iloc[-1]['Close']), 2),
            'avg_volume': int(df['Volume'].mean()) if 'Volume' in df else None,
            'volatility_annual': round(returns.std() * np.sqrt(252) * 100, 2),
            'return_ytd': round(((df.iloc[-1]['Close'] / df.iloc[0]['Close']) - 1) * 100, 2)
        }
    
    def get_coverage(self) -> List[str]:
        """Get market coverage"""
        return ['ASX']
    
    def supports_ticker(self, ticker: str) -> bool:
        """Check if ticker is supported (ASX ETFs)"""
        # Check if data file exists
        ticker_clean = ticker.replace('.AX', '')
        parquet_file = self.data_dir / f"{ticker_clean}.parquet"
        return parquet_file.exists()
    
    def list_available_tickers(self) -> List[str]:
        """List all available tickers"""
        if not self.data_dir.exists():
            return []
        
        tickers = []
        for file in self.data_dir.glob('*.parquet'):
            tickers.append(file.stem)
        
        return sorted(tickers)
