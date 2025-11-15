"""
Portfolio Tools

MCP tools for portfolio optimization and analytics.
"""

import sys
sys.path.append('/home/ubuntu/UltraCore/src')

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from ultracore.domains.wealth.integration.etf_data_provider import ETFDataProvider


class PortfolioTools:
    """Collection of MCP tools for portfolio optimization and analytics"""
    
    def __init__(self, data_dir: str = "data/etf"):
        """
        Initialize portfolio tools.
        
        Args:
            data_dir: Directory containing ETF data
        """
        self.data_dir = data_dir
        self._data_provider = None
    
    @property
    def data_provider(self):
        """Lazy load ETF data provider"""
        if self._data_provider is None:
            self._data_provider = ETFDataProvider(data_dir=self.data_dir)
        return self._data_provider
    
    def calculate_portfolio_metrics(
        self,
        tickers: List[str],
        weights: List[float],
        lookback_years: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate risk/return metrics for a portfolio.
        
        Args:
            tickers: List of ETF tickers
            weights: Portfolio weights (must sum to 1.0)
            lookback_years: Years of historical data to use
        
        Returns:
            Dict with portfolio metrics
        """
        try:
            # Validate inputs
            if len(tickers) != len(weights):
                return {'error': 'Tickers and weights must have same length'}
            
            if abs(sum(weights) - 1.0) > 0.01:
                return {'error': f'Weights must sum to 1.0 (got {sum(weights)})'}
            
            # Load data
            etf_data = {}
            for ticker in tickers:
                data = self.data_provider.load_etf_data(ticker)
                if data is None or data.empty:
                    return {'error': f'No data available for {ticker}'}
                # Limit to lookback period
                if lookback_years:
                    cutoff_date = data.index[-1] - pd.Timedelta(days=lookback_years*365)
                    data = data[data.index >= cutoff_date]
                etf_data[ticker] = data
            
            # Calculate returns
            returns_df = pd.DataFrame()
            for ticker in tickers:
                returns_df[ticker] = etf_data[ticker]['Close'].pct_change()
            
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 252:  # Need at least 1 year of data
                return {'error': 'Insufficient data for analysis'}
            
            # Portfolio returns
            weights_array = np.array(weights)
            portfolio_returns = (returns_df * weights_array).sum(axis=1)
            
            # Calculate metrics
            mean_return = portfolio_returns.mean() * 252  # Annualized
            volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
            sharpe_ratio = mean_return / volatility if volatility > 0 else 0
            
            # Max drawdown
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Correlation matrix
            corr_matrix = returns_df.corr().round(2).to_dict()
            
            # Value at Risk (VaR) - 95% confidence
            var_95 = np.percentile(portfolio_returns, 5)
            
            # Conditional VaR (CVaR)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            return {
                'tickers': tickers,
                'weights': {t: round(w, 4) for t, w in zip(tickers, weights)},
                'expected_return': round(mean_return * 100, 2),  # Percentage
                'volatility': round(volatility * 100, 2),  # Percentage
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown * 100, 2),  # Percentage
                'var_95': round(var_95 * 100, 2),  # Percentage
                'cvar_95': round(cvar_95 * 100, 2),  # Percentage
                'correlation_matrix': corr_matrix,
                'data_points': len(returns_df),
                'lookback_years': lookback_years
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def optimize_portfolio(
        self,
        tickers: List[str],
        objective: str = "sharpe",
        risk_budget: Optional[float] = None,
        lookback_years: int = 5,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize portfolio allocation.
        
        Args:
            tickers: List of ETF tickers
            objective: Optimization objective ("sharpe", "volatility", "return")
            risk_budget: Target volatility (optional)
            lookback_years: Years of historical data
            constraints: Additional constraints (min_weight, max_weight)
        
        Returns:
            Dict with optimal portfolio
        """
        try:
            # Use ETF data provider's optimization
            if objective == "sharpe" and risk_budget:
                result = self.data_provider.optimize_portfolio_mean_variance(
                    tickers=tickers,
                    risk_budget=risk_budget,
                    lookback_years=lookback_years
                )
            else:
                # Fallback to simple optimization
                result = self.data_provider.optimize_portfolio_mean_variance(
                    tickers=tickers,
                    risk_budget=0.20,  # Default 20% volatility
                    lookback_years=lookback_years
                )
            
            if 'error' in result:
                return result
            
            return {
                'tickers': tickers,
                'objective': objective,
                'optimal_weights': {t: round(w, 4) for t, w in result['optimal_weights'].items()},
                'expected_return': round(result['expected_return'] * 100, 2),
                'volatility': round(result['volatility'] * 100, 2),
                'sharpe_ratio': round(result['sharpe_ratio'], 2),
                'optimization_status': result.get('optimization_status', 'success'),
                'lookback_years': lookback_years
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_efficient_frontier(
        self,
        tickers: List[str],
        n_portfolios: int = 100,
        lookback_years: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate efficient frontier for a set of ETFs.
        
        Args:
            tickers: List of ETF tickers
            n_portfolios: Number of portfolios to generate
            lookback_years: Years of historical data
        
        Returns:
            Dict with efficient frontier data
        """
        try:
            # Load data
            etf_data = {}
            for ticker in tickers:
                data = self.data_provider.load_etf_data(ticker)
                if data is None or data.empty:
                    return {'error': f'No data available for {ticker}'}
                # Limit to lookback period
                if lookback_years:
                    cutoff_date = data.index[-1] - pd.Timedelta(days=lookback_years*365)
                    data = data[data.index >= cutoff_date]
                etf_data[ticker] = data
            
            # Calculate returns
            returns_df = pd.DataFrame()
            for ticker in tickers:
                returns_df[ticker] = etf_data[ticker]['Close'].pct_change()
            
            returns_df = returns_df.dropna()
            
            # Generate random portfolios
            n_assets = len(tickers)
            results = []
            
            for _ in range(n_portfolios):
                # Random weights
                weights = np.random.random(n_assets)
                weights /= weights.sum()
                
                # Portfolio metrics
                portfolio_return = (returns_df * weights).sum(axis=1)
                mean_return = portfolio_return.mean() * 252
                volatility = portfolio_return.std() * np.sqrt(252)
                sharpe = mean_return / volatility if volatility > 0 else 0
                
                results.append({
                    'weights': weights.tolist(),
                    'return': round(mean_return * 100, 2),
                    'volatility': round(volatility * 100, 2),
                    'sharpe': round(sharpe, 2)
                })
            
            # Find max Sharpe and min volatility
            max_sharpe = max(results, key=lambda x: x['sharpe'])
            min_vol = min(results, key=lambda x: x['volatility'])
            
            return {
                'tickers': tickers,
                'n_portfolios': n_portfolios,
                'portfolios': results,
                'max_sharpe_portfolio': max_sharpe,
                'min_volatility_portfolio': min_vol,
                'lookback_years': lookback_years
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def rebalance_portfolio(
        self,
        current_holdings: Dict[str, float],
        target_weights: Dict[str, float],
        total_value: float
    ) -> Dict[str, Any]:
        """
        Calculate rebalancing trades.
        
        Args:
            current_holdings: Current shares held {ticker: shares}
            target_weights: Target portfolio weights {ticker: weight}
            total_value: Total portfolio value
        
        Returns:
            Dict with rebalancing trades
        """
        try:
            # Get current prices
            tickers = list(target_weights.keys())
            prices = {}
            
            for ticker in tickers:
                latest = self.data_provider.get_latest_price(ticker)
                if latest is None:
                    return {'error': f'Cannot get price for {ticker}'}
                prices[ticker] = latest
            
            # Calculate current values and weights
            current_values = {t: current_holdings.get(t, 0) * prices[t] for t in tickers}
            current_total = sum(current_values.values())
            current_weights = {t: v / current_total if current_total > 0 else 0 
                             for t, v in current_values.items()}
            
            # Calculate target values
            target_values = {t: total_value * w for t, w in target_weights.items()}
            
            # Calculate trades
            trades = {}
            for ticker in tickers:
                current_shares = current_holdings.get(ticker, 0)
                target_shares = target_values[ticker] / prices[ticker]
                trade_shares = target_shares - current_shares
                
                if abs(trade_shares) > 0.01:  # Minimum trade threshold
                    trades[ticker] = {
                        'action': 'buy' if trade_shares > 0 else 'sell',
                        'shares': round(abs(trade_shares), 2),
                        'value': round(abs(trade_shares) * prices[ticker], 2),
                        'price': round(prices[ticker], 2)
                    }
            
            # Calculate costs
            transaction_cost = len(trades) * 10  # $10 per trade
            
            return {
                'current_weights': {t: round(w, 4) for t, w in current_weights.items()},
                'target_weights': {t: round(w, 4) for t, w in target_weights.items()},
                'trades': trades,
                'total_trades': len(trades),
                'transaction_cost': transaction_cost,
                'total_value': round(total_value, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
