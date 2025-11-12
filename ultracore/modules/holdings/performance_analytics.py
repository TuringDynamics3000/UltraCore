"""
Performance Analytics Engine
Advanced portfolio performance metrics and analytics
"""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class PerformanceAnalytics:
    """
    Calculate comprehensive portfolio performance metrics
    
    Metrics:
    - Total return, CAGR
    - Sharpe ratio, Sortino ratio
    - Maximum drawdown
    - Alpha, Beta
    - Information ratio
    - Tracking error
    """
    
    def __init__(self):
        self.risk_free_rate = 0.04  # 4% annual
        self.benchmark_returns = None
    
    def calculate_total_return(
        self,
        start_value: float,
        end_value: float
    ) -> Dict[str, Any]:
        """Calculate total return"""
        
        if start_value == 0:
            return {"total_return": 0, "total_return_pct": 0}
        
        total_return = end_value - start_value
        total_return_pct = total_return / start_value
        
        return {
            "start_value": start_value,
            "end_value": end_value,
            "total_return": total_return,
            "total_return_pct": total_return_pct
        }
    
    def calculate_cagr(
        self,
        start_value: float,
        end_value: float,
        years: float
    ) -> float:
        """
        Calculate Compound Annual Growth Rate
        CAGR = (End Value / Start Value)^(1/years) - 1
        """
        
        if start_value == 0 or years == 0:
            return 0
        
        cagr = (end_value / start_value) ** (1 / years) - 1
        return cagr
    
    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sharpe Ratio
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev
        """
        
        if not returns or len(returns) < 2:
            return 0
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_dev = np.std(returns_array)
        
        if std_dev == 0:
            return 0
        
        sharpe = (mean_return - risk_free_rate) / std_dev
        return sharpe
    
    def calculate_sortino_ratio(
        self,
        returns: List[float],
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sortino Ratio
        Like Sharpe but only considers downside volatility
        """
        
        if not returns or len(returns) < 2:
            return 0
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        
        # Downside deviation (only negative returns)
        downside_returns = returns_array[returns_array < 0]
        
        if len(downside_returns) == 0:
            return float('inf')  # No downside
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0
        
        sortino = (mean_return - risk_free_rate) / downside_std
        return sortino
    
    def calculate_max_drawdown(
        self,
        values: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate maximum drawdown
        Max DD = (Trough - Peak) / Peak
        """
        
        if not values or len(values) < 2:
            return {
                "max_drawdown": 0,
                "max_drawdown_pct": 0,
                "peak_value": 0,
                "trough_value": 0
            }
        
        values_array = np.array(values)
        running_max = np.maximum.accumulate(values_array)
        drawdowns = (values_array - running_max) / running_max
        
        max_dd_idx = np.argmin(drawdowns)
        max_dd = drawdowns[max_dd_idx]
        
        # Find peak before this drawdown
        peak_idx = np.argmax(values_array[:max_dd_idx+1])
        
        return {
            "max_drawdown": max_dd * running_max[peak_idx],
            "max_drawdown_pct": max_dd,
            "peak_value": values_array[peak_idx],
            "peak_date_idx": peak_idx,
            "trough_value": values_array[max_dd_idx],
            "trough_date_idx": max_dd_idx
        }
    
    def calculate_alpha_beta(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate Alpha and Beta vs benchmark
        Alpha = Portfolio Return - (Risk Free Rate + Beta * (Benchmark Return - Risk Free Rate))
        Beta = Covariance(Portfolio, Benchmark) / Variance(Benchmark)
        """
        
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return {"alpha": 0, "beta": 0}
        
        portfolio_array = np.array(portfolio_returns)
        benchmark_array = np.array(benchmark_returns)
        
        # Calculate Beta
        covariance = np.cov(portfolio_array, benchmark_array)[0, 1]
        benchmark_variance = np.var(benchmark_array)
        
        if benchmark_variance == 0:
            beta = 0
        else:
            beta = covariance / benchmark_variance
        
        # Calculate Alpha
        portfolio_mean = np.mean(portfolio_array)
        benchmark_mean = np.mean(benchmark_array)
        
        alpha = portfolio_mean - (self.risk_free_rate + beta * (benchmark_mean - self.risk_free_rate))
        
        return {
            "alpha": alpha,
            "beta": beta,
            "r_squared": self._calculate_r_squared(portfolio_array, benchmark_array)
        }
    
    def calculate_information_ratio(
        self,
        portfolio_returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """
        Calculate Information Ratio
        IR = (Portfolio Return - Benchmark Return) / Tracking Error
        """
        
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return 0
        
        portfolio_array = np.array(portfolio_returns)
        benchmark_array = np.array(benchmark_returns)
        
        excess_returns = portfolio_array - benchmark_array
        mean_excess = np.mean(excess_returns)
        tracking_error = np.std(excess_returns)
        
        if tracking_error == 0:
            return 0
        
        information_ratio = mean_excess / tracking_error
        return information_ratio
    
    def calculate_volatility(
        self,
        returns: List[float],
        annualize: bool = True
    ) -> float:
        """Calculate volatility (standard deviation of returns)"""
        
        if not returns or len(returns) < 2:
            return 0
        
        volatility = np.std(returns)
        
        if annualize:
            # Annualize assuming daily returns
            volatility = volatility * np.sqrt(252)
        
        return volatility
    
    def calculate_var(
        self,
        returns: List[float],
        confidence: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk (VaR)
        95% confidence = worst 5% of outcomes
        """
        
        if not returns:
            return 0
        
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence) * 100)
        
        return var
    
    def calculate_comprehensive_metrics(
        self,
        portfolio_history: List[Dict[str, Any]],
        benchmark_returns: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate all performance metrics
        """
        
        if not portfolio_history or len(portfolio_history) < 2:
            return {"error": "Insufficient data"}
        
        # Extract values and calculate returns
        values = [h["total_value"] for h in portfolio_history]
        dates = [h["date"] for h in portfolio_history]
        
        returns = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                ret = (values[i] - values[i-1]) / values[i-1]
                returns.append(ret)
        
        # Calculate time period
        start_date = datetime.fromisoformat(dates[0])
        end_date = datetime.fromisoformat(dates[-1])
        years = (end_date - start_date).days / 365.25
        
        # Total return
        total_return = self.calculate_total_return(values[0], values[-1])
        
        # CAGR
        cagr = self.calculate_cagr(values[0], values[-1], years) if years > 0 else 0
        
        # Risk metrics
        sharpe = self.calculate_sharpe_ratio(returns)
        sortino = self.calculate_sortino_ratio(returns)
        volatility = self.calculate_volatility(returns)
        max_dd = self.calculate_max_drawdown(values)
        var_95 = self.calculate_var(returns, 0.95)
        
        metrics = {
            "period": {
                "start_date": dates[0],
                "end_date": dates[-1],
                "years": years,
                "data_points": len(values)
            },
            "returns": {
                "total_return": total_return["total_return"],
                "total_return_pct": total_return["total_return_pct"],
                "cagr": cagr,
                "mean_return": np.mean(returns) if returns else 0,
                "median_return": np.median(returns) if returns else 0
            },
            "risk": {
                "volatility": volatility,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "max_drawdown": max_dd["max_drawdown"],
                "max_drawdown_pct": max_dd["max_drawdown_pct"],
                "var_95": var_95
            }
        }
        
        # Add benchmark comparison if available
        if benchmark_returns and len(benchmark_returns) == len(returns):
            alpha_beta = self.calculate_alpha_beta(returns, benchmark_returns)
            info_ratio = self.calculate_information_ratio(returns, benchmark_returns)
            
            metrics["benchmark_comparison"] = {
                "alpha": alpha_beta["alpha"],
                "beta": alpha_beta["beta"],
                "r_squared": alpha_beta["r_squared"],
                "information_ratio": info_ratio
            }
        
        return metrics
    
    def _calculate_r_squared(
        self,
        portfolio_returns: np.ndarray,
        benchmark_returns: np.ndarray
    ) -> float:
        """Calculate R-squared (goodness of fit)"""
        
        if len(portfolio_returns) < 2:
            return 0
        
        correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]
        r_squared = correlation ** 2
        
        return r_squared

# Global instance
performance_analytics = PerformanceAnalytics()
