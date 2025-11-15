"""UltraOptimiser Integration - Portfolio Optimization"""
from typing import Dict, List, Optional
from decimal import Decimal
import numpy as np
import logging

from typing import Any
from .etf_data_provider import ETFDataProvider

logger = logging.getLogger(__name__)


class OptimisationService:
    """Base class for optimisation services."""
    async def optimize(self, **kwargs) -> Dict:
        raise NotImplementedError


class UltraOptimiserAdapter:
    """
    Adapter for UltraOptimiser integration.
    
    UltraOptimiser Achievements (Existing):
    - Expected return: 8.89% p.a.
    - Sharpe ratio: 0.66
    - Maximum drawdown: -15.23%
    - Win rate: 62.5%
    
    Integration:
    - Portfolio construction
    - Asset allocation optimization
    - Risk-adjusted returns
    - Rebalancing recommendations
    """
    
    def __init__(self, optimiser: OptimisationService, etf_data_dir: str = "/data/etf"):
        self.optimiser = optimiser
        self.etf_data = ETFDataProvider(data_dir=etf_data_dir)
        logger.info("UltraOptimiser initialized with ETF data provider")
    
    async def optimize(self, **kwargs) -> Dict:
        """
        Direct optimization method that delegates to the optimiser service.
        
        This method provides a direct pass-through to the underlying
        UltraOptimiser service for flexibility.
        """
        return await self.optimiser.optimize(**kwargs)
    
    async def optimize_portfolio(
        self,
        risk_tolerance: str,
        time_horizon_years: int,
        current_holdings: Dict[str, Decimal],
        available_cash: Decimal,
        constraints: Dict = None
    ) -> Dict:
        """
        Optimize portfolio using UltraOptimiser.
        
        Returns target allocation with expected returns and risk.
        """
        
        # Map risk tolerance to UltraOptimiser risk level
        risk_mapping = {
            "low": 0.3,      # Conservative: 30% risk budget
            "medium": 0.6,   # Balanced: 60% risk budget
            "high": 0.9      # Growth: 90% risk budget
        }
        
        risk_budget = risk_mapping.get(risk_tolerance, 0.6)
        
        # Build universe of securities
        universe = self._build_universe(risk_tolerance, time_horizon_years)
        
        # Check data availability
        availability = self.etf_data.check_data_availability(universe)
        available_etfs = [etf for etf, avail in availability.items() if avail]
        
        if not available_etfs:
            logger.warning("No ETF data available, using default optimization")
            available_etfs = universe  # Fallback
        
        logger.info(f"Optimizing with {len(available_etfs)} ETFs: {available_etfs}")
        
        # Get real market data
        expected_returns = self.etf_data.calculate_expected_returns(available_etfs, lookback_years=3)
        cov_matrix = self.etf_data.calculate_covariance_matrix(available_etfs, lookback_years=3)
        
        # Run optimization with real data
        optimization_result = self.etf_data.optimize_portfolio_mean_variance(
            tickers=available_etfs,
            risk_budget=risk_budget,
            lookback_years=3
        )
        
        # Calculate rebalancing trades
        rebalancing_trades = self._calculate_rebalancing_trades(
            current_holdings=current_holdings,
            target_weights=optimization_result["optimal_weights"],
            available_cash=available_cash
        )
        
        result = {
            "optimal_weights": optimization_result["optimal_weights"],
            "expected_return": optimization_result["expected_return"],
            "volatility": optimization_result["volatility"],
            "sharpe_ratio": optimization_result["sharpe_ratio"],
            "rebalancing_trades": rebalancing_trades,
            "optimization_score": optimization_result["sharpe_ratio"] * 100,
            "universe": available_etfs,
            "data_source": "real_market_data"
        }
        
        return {
            "target_allocation": result["optimal_weights"],
            "expected_return": result["expected_return"],
            "expected_volatility": result["volatility"],
            "sharpe_ratio": result["sharpe_ratio"],
            "recommended_trades": result["rebalancing_trades"],
            "optimization_score": result["optimization_score"]
        }
    
    def _build_universe(
        self,
        risk_tolerance: str,
        time_horizon_years: int
    ) -> List[str]:
        """
        Build investment universe based on risk profile.
        
        Australian Securities:
        - Conservative: Cash, bonds, defensive stocks
        - Balanced: Mix of growth and defensive
        - Growth: Growth stocks, international exposure
        """
        
        # Core Australian ETFs (actual ASX codes)
        universe = []
        
        if risk_tolerance in ["low", "medium"]:
            # Conservative/Defensive
            universe.extend([
                "VAS",   # Vanguard Australian Shares
                "VGB",   # Vanguard Australian Government Bonds
                "VAF",   # Vanguard Australian Fixed Interest
                "VHY",   # Vanguard Australian Shares High Yield
            ])
        
        if risk_tolerance in ["medium", "high"]:
            # Balanced/Growth
            universe.extend([
                "VGS",   # Vanguard MSCI International Shares
                "VGE",   # Vanguard FTSE Emerging Markets
                "VDHG",  # Vanguard Diversified High Growth
                "IOZ",   # iShares Core S&P/ASX 200
            ])
        
        if risk_tolerance == "high":
            # Aggressive/Growth
            universe.extend([
                "NDQ",   # BetaShares NASDAQ 100
                "ASIA",  # BetaShares Asia Technology Tigers
                "HACK",  # BetaShares Global Cybersecurity
            ])
        
        return universe
    
    async def check_rebalancing_needed(
        self,
        current_allocation: Dict[str, Decimal],
        target_allocation: Dict[str, Decimal],
        threshold: Decimal = Decimal("0.05")
    ) -> Dict:
        """
        Check if portfolio needs rebalancing.
        
        Triggers rebalancing if allocation drift > threshold.
        """
        
        needs_rebalancing = False
        drift_details = {}
        
        for asset, target_weight in target_allocation.items():
            current_weight = current_allocation.get(asset, Decimal("0"))
            drift = abs(current_weight - target_weight)
            
            drift_details[asset] = {
                "current": float(current_weight),
                "target": float(target_weight),
                "drift": float(drift)
            }
            
            if drift > threshold:
                needs_rebalancing = True
        
        return {
            "needs_rebalancing": needs_rebalancing,
            "threshold": float(threshold),
            "drift_details": drift_details,
            "recommendation": "Rebalance recommended" if needs_rebalancing else "Portfolio within tolerance"
        }
    
    def _calculate_rebalancing_trades(
        self,
        current_holdings: Dict[str, Decimal],
        target_weights: Dict[str, float],
        available_cash: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Calculate specific trades needed to rebalance portfolio
        
        Args:
            current_holdings: Current holdings {ticker: value}
            target_weights: Target allocation {ticker: weight}
            available_cash: Available cash for investing
        
        Returns:
            List of trades with ticker, action (buy/sell), amount
        """
        # Calculate total portfolio value
        total_value = sum(current_holdings.values()) + available_cash
        
        trades = []
        
        for ticker, target_weight in target_weights.items():
            target_value = float(total_value) * target_weight
            current_value = float(current_holdings.get(ticker, Decimal("0")))
            
            difference = target_value - current_value
            
            if abs(difference) > 100:  # Only trade if difference > $100
                action = "buy" if difference > 0 else "sell"
                trades.append({
                    "ticker": ticker,
                    "action": action,
                    "amount": abs(difference),
                    "current_value": current_value,
                    "target_value": target_value
                })
        
        return trades
    
    def get_portfolio_analytics(
        self,
        holdings: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for current portfolio
        
        Args:
            holdings: Current holdings {ticker: value}
        
        Returns:
            Portfolio analytics including risk metrics, correlations, etc.
        """
        tickers = list(holdings.keys())
        
        if not tickers:
            return {"error": "No holdings provided"}
        
        # Calculate weights
        total_value = sum(holdings.values())
        weights = {ticker: float(value / total_value) for ticker, value in holdings.items()}
        
        # Get risk metrics for each holding
        risk_metrics = {}
        for ticker in tickers:
            try:
                risk_metrics[ticker] = self.etf_data.calculate_risk_metrics(ticker, lookback_years=3)
            except Exception as e:
                logger.error(f"Error calculating risk metrics for {ticker}: {e}")
        
        # Get correlation matrix
        try:
            correlation_matrix = self.etf_data.calculate_correlation_matrix(tickers, lookback_years=3)
        except Exception as e:
            logger.error(f"Error calculating correlation matrix: {e}")
            correlation_matrix = None
        
        # Calculate portfolio-level metrics
        expected_returns = self.etf_data.calculate_expected_returns(tickers, lookback_years=3)
        portfolio_return = sum(weights[t] * expected_returns.get(t, 0.08) for t in tickers)
        
        # Portfolio volatility
        cov_matrix = self.etf_data.calculate_covariance_matrix(tickers, lookback_years=3)
        weights_array = np.array([weights[t] for t in tickers])
        portfolio_variance = np.dot(weights_array, np.dot(cov_matrix.values, weights_array))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Portfolio Sharpe ratio
        risk_free_rate = 0.03
        portfolio_sharpe = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            "weights": weights,
            "total_value": float(total_value),
            "expected_return": float(portfolio_return),
            "volatility": float(portfolio_volatility),
            "sharpe_ratio": float(portfolio_sharpe),
            "risk_metrics_by_holding": risk_metrics,
            "correlation_matrix": correlation_matrix.to_dict() if correlation_matrix is not None else None,
            "diversification_score": self._calculate_diversification_score(correlation_matrix) if correlation_matrix is not None else None
        }
    
    def _calculate_diversification_score(self, correlation_matrix) -> float:
        """
        Calculate diversification score (0-100)
        Lower average correlation = better diversification
        """
        if correlation_matrix is None or correlation_matrix.empty:
            return 50.0
        
        # Get upper triangle of correlation matrix (excluding diagonal)
        n = len(correlation_matrix)
        if n < 2:
            return 100.0
        
        correlations = []
        for i in range(n):
            for j in range(i+1, n):
                correlations.append(correlation_matrix.iloc[i, j])
        
        avg_correlation = np.mean(correlations)
        
        # Convert to score: 0 correlation = 100, 1 correlation = 0
        score = (1 - avg_correlation) * 100
        
        return float(max(0, min(100, score)))
