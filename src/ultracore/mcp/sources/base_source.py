"""
Base Data Source

Abstract base class for all financial data sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd


class BaseDataSource(ABC):
    """
    Abstract base class for financial data sources.
    
    All data sources must implement these methods to ensure
    consistent interface across different providers.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize data source.
        
        Args:
            name: Source name (e.g., "yahoo", "alpha_vantage")
            config: Source-specific configuration
        """
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.priority = self.config.get('priority', 99)
        self.rate_limit = self.config.get('rate_limit', 1000)
        self.cache_ttl = self.config.get('cache_ttl', 3600)
        
    @abstractmethod
    def get_historical_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data for a ticker.
        
        Args:
            ticker: Ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period string (e.g., "1y", "5y", "max")
        
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        pass
    
    @abstractmethod
    def get_latest_price(self, ticker: str) -> Dict[str, Any]:
        """
        Get latest/current price for a ticker.
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            Dict with keys: price, change, change_percent, timestamp
        """
        pass
    
    @abstractmethod
    def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get metadata/info about a ticker.
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            Dict with ticker metadata (name, issuer, inception, etc.)
        """
        pass
    
    def is_available(self) -> bool:
        """Check if data source is available/enabled"""
        return self.enabled
    
    def get_coverage(self) -> List[str]:
        """
        Get list of markets/exchanges covered by this source.
        
        Returns:
            List of market codes (e.g., ["ASX", "NYSE", "NASDAQ"])
        """
        return self.config.get('coverage', [])
    
    def supports_ticker(self, ticker: str) -> bool:
        """
        Check if this source supports a specific ticker.
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            True if supported, False otherwise
        """
        # Default implementation - can be overridden
        return True
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.enabled}, priority={self.priority})"
