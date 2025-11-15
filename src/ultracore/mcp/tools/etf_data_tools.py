"""
ETF Data Tools

MCP tools for accessing ETF data from multiple sources.
"""

import sys
sys.path.append('/home/ubuntu/UltraCore/src')

from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime

from ultracore.mcp.sources.yahoo_source import YahooFinanceSource


class ETFDataTools:
    """Collection of MCP tools for ETF data access"""
    
    def __init__(self, data_sources: Optional[List] = None):
        """
        Initialize ETF data tools.
        
        Args:
            data_sources: List of data source instances
        """
        self.data_sources = data_sources or []
        
        # Add default Yahoo source if none provided
        if not self.data_sources:
            self.data_sources.append(YahooFinanceSource())
    
    def get_etf_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical OHLCV data for an ETF.
        
        Args:
            ticker: ETF ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period string (e.g., "1y", "5y", "max")
            source: Specific source to use (optional)
        
        Returns:
            Dict with ticker data
        """
        # Select data source
        data_source = self._select_source(ticker, source)
        
        if not data_source:
            return {
                'ticker': ticker,
                'error': 'No data source available for this ticker',
                'data': []
            }
        
        # Get data
        try:
            df = data_source.get_historical_data(ticker, start_date, end_date, period)
            
            if df.empty:
                return {
                    'ticker': ticker,
                    'error': 'No data available',
                    'data': []
                }
            
            # Convert to dict format
            data = []
            for idx, row in df.iterrows():
                data.append({
                    'date': str(idx)[:10],
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume']) if 'Volume' in row else None
                })
            
            return {
                'ticker': ticker,
                'source': data_source.name,
                'rows': len(data),
                'start_date': data[0]['date'] if data else None,
                'end_date': data[-1]['date'] if data else None,
                'data': data
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'data': []
            }
    
    def get_multiple_etfs(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get data for multiple ETFs at once.
        
        Args:
            tickers: List of ETF ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period string
            source: Specific source to use
        
        Returns:
            Dict with data for all tickers
        """
        results = {}
        
        for ticker in tickers:
            results[ticker] = self.get_etf_data(ticker, start_date, end_date, period, source)
        
        # Summary
        successful = sum(1 for r in results.values() if 'error' not in r)
        
        return {
            'tickers': tickers,
            'total': len(tickers),
            'successful': successful,
            'failed': len(tickers) - successful,
            'results': results
        }
    
    def get_etf_info(self, ticker: str, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata about an ETF.
        
        Args:
            ticker: ETF ticker symbol
            source: Specific source to use
        
        Returns:
            Dict with ETF metadata
        """
        data_source = self._select_source(ticker, source)
        
        if not data_source:
            return {
                'ticker': ticker,
                'error': 'No data source available'
            }
        
        try:
            return data_source.get_ticker_info(ticker)
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e)
            }
    
    def get_latest_price(self, ticker: str, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Get latest/current price for an ETF.
        
        Args:
            ticker: ETF ticker symbol
            source: Specific source to use
        
        Returns:
            Dict with latest price info
        """
        data_source = self._select_source(ticker, source)
        
        if not data_source:
            return {
                'ticker': ticker,
                'error': 'No data source available'
            }
        
        try:
            return data_source.get_latest_price(ticker)
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e)
            }
    
    def get_market_snapshot(
        self,
        tickers: List[str],
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current prices for multiple ETFs.
        
        Args:
            tickers: List of ETF ticker symbols
            source: Specific source to use
        
        Returns:
            Dict with prices for all tickers
        """
        results = {}
        
        for ticker in tickers:
            results[ticker] = self.get_latest_price(ticker, source)
        
        return {
            'tickers': tickers,
            'timestamp': datetime.now().isoformat(),
            'prices': results
        }
    
    def list_available_etfs(self, source: Optional[str] = None) -> Dict[str, Any]:
        """
        List all available ETFs.
        
        Args:
            source: Specific source to query
        
        Returns:
            Dict with list of available tickers
        """
        if source:
            data_source = next((s for s in self.data_sources if s.name == source), None)
            if not data_source:
                return {'error': f'Source {source} not found'}
            
            sources_to_check = [data_source]
        else:
            sources_to_check = self.data_sources
        
        all_tickers = set()
        by_source = {}
        
        for ds in sources_to_check:
            if hasattr(ds, 'list_available_tickers'):
                tickers = ds.list_available_tickers()
                all_tickers.update(tickers)
                by_source[ds.name] = tickers
        
        return {
            'total': len(all_tickers),
            'tickers': sorted(list(all_tickers)),
            'by_source': by_source
        }
    
    def _select_source(self, ticker: str, source_name: Optional[str] = None):
        """Select best data source for a ticker"""
        if source_name:
            # Use specific source if requested
            return next((s for s in self.data_sources if s.name == source_name), None)
        
        # Find best available source by priority
        available_sources = [
            s for s in self.data_sources
            if s.is_available() and s.supports_ticker(ticker)
        ]
        
        if not available_sources:
            return None
        
        # Sort by priority (lower number = higher priority)
        available_sources.sort(key=lambda s: s.priority)
        
        return available_sources[0]
