"""
ESG-Aware Portfolio Environment for Reinforcement Learning

This environment extends the base PortfolioEnv to incorporate ESG metrics
into the state space and reward function, enabling RL agents to optimize
for both financial returns and ESG outcomes.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
import gymnasium as gym
from gymnasium import spaces

from ultracore.rl.environments.portfolio_env import PortfolioEnv
from ultracore.esg.data.esg_data_loader import EsgDataLoader


class EsgPortfolioEnv(PortfolioEnv):
    """
    ESG-aware portfolio environment that extends the base PortfolioEnv.
    
    Key enhancements:
    - State space includes ESG metrics for each asset
    - Reward function incorporates ESG objectives
    - Actions are constrained by ESG preferences
    - Supports dynamic ESG events (e.g., rating downgrades)
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        esg_data: pd.DataFrame,
        initial_balance: float = 100000.0,
        transaction_cost: float = 0.001,
        esg_weight: float = 0.3,  # Weight of ESG vs financial objectives
        min_esg_rating: Optional[str] = None,
        max_carbon_intensity: Optional[float] = None,
        excluded_sectors: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the ESG-aware portfolio environment.
        
        Args:
            data: Price data for assets (OHLCV)
            esg_data: ESG metrics for assets (ratings, scores, carbon intensity, etc.)
            initial_balance: Starting cash balance
            transaction_cost: Cost per transaction (as fraction of trade value)
            esg_weight: Weight of ESG objectives in reward (0-1, where 0=pure financial, 1=pure ESG)
            min_esg_rating: Minimum ESG rating required (e.g., "BBB")
            max_carbon_intensity: Maximum carbon intensity allowed (tCO2e/$M revenue)
            excluded_sectors: List of sectors to exclude (e.g., ["Tobacco", "Weapons"])
        """
        super().__init__(data, initial_balance, transaction_cost, **kwargs)
        
        self.esg_data = esg_data
        self.esg_weight = esg_weight
        self.min_esg_rating = min_esg_rating
        self.max_carbon_intensity = max_carbon_intensity
        self.excluded_sectors = excluded_sectors or []
        
        # ESG rating mapping (for numerical comparison)
        self.rating_map = {
            'AAA': 7, 'AA': 6, 'A': 5, 'BBB': 4, 'BB': 3, 'B': 2, 'CCC': 1
        }
        
        # Extend observation space to include ESG metrics
        self._update_observation_space()
        
    def _update_observation_space(self):
        """Extend observation space to include ESG features"""
        # Original observation space: [prices, holdings, cash, ...]
        # New observation space: [prices, holdings, cash, ..., esg_ratings, carbon_intensity, ...]
        
        n_assets = len(self.data.columns) // 5  # OHLCV = 5 features per asset
        n_esg_features = 3  # rating, carbon_intensity, controversy_score
        
        original_dim = self.observation_space.shape[0]
        new_dim = original_dim + (n_assets * n_esg_features)
        
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(new_dim,),
            dtype=np.float32
        )
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation including ESG metrics"""
        # Get base observation from parent class
        base_obs = super()._get_observation()
        
        # Get ESG metrics for current timestep
        esg_obs = self._get_esg_observation()
        
        # Concatenate base and ESG observations
        return np.concatenate([base_obs, esg_obs])
    
    def _get_esg_observation(self) -> np.ndarray:
        """Extract ESG metrics for current timestep"""
        current_date = self.data.index[self.current_step]
        
        # Get ESG data for current date (or most recent available)
        esg_slice = self.esg_data[self.esg_data.index <= current_date].iloc[-1]
        
        # Extract key ESG features
        esg_features = []
        for asset in self.asset_names:
            # ESG rating (converted to numerical)
            rating = esg_slice.get(f'{asset}_rating', 'BBB')
            rating_numeric = self.rating_map.get(rating, 4) / 7.0  # Normalize to [0, 1]
            
            # Carbon intensity (normalized)
            carbon = esg_slice.get(f'{asset}_carbon_intensity', 100.0)
            carbon_normalized = min(carbon / 500.0, 1.0)  # Cap at 500 tCO2e/$M
            
            # Controversy score (0-10 scale, normalized)
            controversy = esg_slice.get(f'{asset}_controversy_score', 0.0)
            controversy_normalized = controversy / 10.0
            
            esg_features.extend([rating_numeric, carbon_normalized, controversy_normalized])
        
        return np.array(esg_features, dtype=np.float32)
    
    def _calculate_reward(self, action: np.ndarray) -> float:
        """
        Calculate reward incorporating both financial and ESG objectives.
        
        Reward = (1 - esg_weight) * financial_reward + esg_weight * esg_reward
        """
        # Financial reward (from parent class)
        financial_reward = self._calculate_financial_reward()
        
        # ESG reward
        esg_reward = self._calculate_esg_reward()
        
        # Combined reward
        total_reward = (1 - self.esg_weight) * financial_reward + self.esg_weight * esg_reward
        
        # Penalty for violating ESG constraints
        constraint_penalty = self._calculate_constraint_penalty()
        
        return total_reward - constraint_penalty
    
    def _calculate_financial_reward(self) -> float:
        """Calculate financial component of reward (portfolio return)"""
        if self.current_step == 0:
            return 0.0
        
        current_value = self._get_portfolio_value()
        previous_value = self.portfolio_value_history[-1] if self.portfolio_value_history else self.initial_balance
        
        return (current_value - previous_value) / previous_value
    
    def _calculate_esg_reward(self) -> float:
        """
        Calculate ESG component of reward.
        
        Rewards portfolios with:
        - Higher ESG ratings
        - Lower carbon intensity
        - Fewer controversies
        """
        current_date = self.data.index[self.current_step]
        esg_slice = self.esg_data[self.esg_data.index <= current_date].iloc[-1]
        
        # Calculate portfolio-weighted ESG metrics
        portfolio_rating = 0.0
        portfolio_carbon = 0.0
        portfolio_controversy = 0.0
        total_weight = 0.0
        
        for i, asset in enumerate(self.asset_names):
            weight = self.holdings[i] / sum(self.holdings) if sum(self.holdings) > 0 else 0.0
            
            if weight > 0:
                rating = esg_slice.get(f'{asset}_rating', 'BBB')
                rating_numeric = self.rating_map.get(rating, 4)
                
                carbon = esg_slice.get(f'{asset}_carbon_intensity', 100.0)
                controversy = esg_slice.get(f'{asset}_controversy_score', 0.0)
                
                portfolio_rating += weight * rating_numeric
                portfolio_carbon += weight * carbon
                portfolio_controversy += weight * controversy
                total_weight += weight
        
        # Normalize and combine ESG metrics
        rating_score = portfolio_rating / 7.0  # Normalize to [0, 1]
        carbon_score = max(0, 1 - portfolio_carbon / 500.0)  # Lower is better
        controversy_score = max(0, 1 - portfolio_controversy / 10.0)  # Lower is better
        
        # Weighted average of ESG components
        esg_reward = (rating_score + carbon_score + controversy_score) / 3.0
        
        return esg_reward
    
    def _calculate_constraint_penalty(self) -> float:
        """Calculate penalty for violating ESG constraints"""
        penalty = 0.0
        
        current_date = self.data.index[self.current_step]
        esg_slice = self.esg_data[self.esg_data.index <= current_date].iloc[-1]
        
        # Check minimum ESG rating constraint
        if self.min_esg_rating:
            min_rating_numeric = self.rating_map.get(self.min_esg_rating, 4)
            
            for i, asset in enumerate(self.asset_names):
                if self.holdings[i] > 0:
                    rating = esg_slice.get(f'{asset}_rating', 'BBB')
                    rating_numeric = self.rating_map.get(rating, 4)
                    
                    if rating_numeric < min_rating_numeric:
                        penalty += 0.5  # Large penalty for holding below-threshold assets
        
        # Check carbon intensity constraint
        if self.max_carbon_intensity:
            for i, asset in enumerate(self.asset_names):
                if self.holdings[i] > 0:
                    carbon = esg_slice.get(f'{asset}_carbon_intensity', 100.0)
                    
                    if carbon > self.max_carbon_intensity:
                        penalty += 0.3
        
        return penalty
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Reset the environment"""
        obs, info = super().reset(seed=seed, options=options)
        
        # Add ESG metrics to observation
        esg_obs = self._get_esg_observation()
        full_obs = np.concatenate([obs, esg_obs])
        
        # Add ESG info
        info['esg_portfolio_rating'] = 0.0
        info['esg_portfolio_carbon'] = 0.0
        
        return full_obs, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute one step in the environment"""
        # Execute action (buy/sell/hold)
        self._execute_action(action)
        
        # Move to next timestep
        self.current_step += 1
        
        # Calculate reward
        reward = self._calculate_reward(action)
        
        # Check if episode is done
        done = self.current_step >= len(self.data) - 1
        truncated = False
        
        # Get new observation
        obs = self._get_observation()
        
        # Info dict
        info = {
            'portfolio_value': self._get_portfolio_value(),
            'esg_reward_component': self._calculate_esg_reward(),
            'financial_reward_component': self._calculate_financial_reward(),
        }
        
        return obs, reward, done, truncated, info
