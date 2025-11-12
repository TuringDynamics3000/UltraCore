"""Reinforcement Learning Environment for Fixed Deposit Rate Optimization"""
import gym
from gym import spaces
import numpy as np
from typing import Tuple, Dict
from decimal import Decimal


class FixedDepositEnvironment(gym.Env):
    """
    OpenAI Gym environment for learning optimal FD interest rate strategies.
    
    State Space:
    - Current market rates (competitor rates)
    - Customer segment characteristics
    - Economic indicators (inflation, RBA rate)
    - Bank's liquidity position
    - Historical renewal rates
    - Competitor actions
    - Time until maturity
    
    Action Space:
    - Interest rate adjustment (-0.5% to +0.5% from base rate)
    - Rate discretized in 0.05% increments
    
    Reward Function:
    - Positive: Customer deposits, renewals, profitability
    - Negative: Customer churn, excess liquidity cost, competitive loss
    - Balanced: Risk-adjusted profit maximization
    
    Goal: Learn to price FD rates that:
    1. Maximize deposits and renewals
    2. Maintain healthy net interest margin
    3. Stay competitive in market
    4. Optimize liquidity position
    """
    
    def __init__(
        self,
        base_rate: float = 5.0,
        competitors: int = 5,
        customer_segments: int = 3
    ):
        super(FixedDepositEnvironment, self).__init__()
        
        self.base_rate = base_rate
        self.competitors = competitors
        self.customer_segments = customer_segments
        
        # State space: [market_rates, liquidity, inflation, customer_features, time]
        # Shape: (competitors + liquidity + inflation + segments + time) = 5 + 1 + 1 + 3 + 1 = 11
        self.observation_space = spaces.Box(
            low=0,
            high=np.inf,
            shape=(11,),
            dtype=np.float32
        )
        
        # Action space: Rate adjustment in increments of 0.05%
        # Range: -0.5% to +0.5% = 21 discrete actions
        self.action_space = spaces.Discrete(21)
        
        # Initialize state
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        # Initial market conditions
        self.current_step = 0
        self.max_steps = 252  # 1 year of trading days
        
        # Competitor rates (normally distributed around base)
        self.competitor_rates = np.random.normal(
            self.base_rate,
            0.3,
            self.competitors
        )
        
        # Bank's liquidity position (0-1, higher = excess liquidity)
        self.liquidity_position = 0.5
        
        # Economic conditions
        self.inflation_rate = 2.5
        
        # Customer segment sizes (deposits in millions)
        self.segment_deposits = np.array([10.0, 25.0, 50.0])
        
        # Time to next rate review
        self.time_to_review = 30  # days
        
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one timestep.
        
        Args:
            action: Rate adjustment action (0-20 mapped to -0.5% to +0.5%)
        
        Returns:
            observation, reward, done, info
        """
        # Map action to rate adjustment
        rate_adjustment = (action - 10) * 0.05  # -0.5% to +0.5%
        new_rate = self.base_rate + rate_adjustment
        
        # Calculate reward components
        
        # 1. Customer acquisition/retention
        avg_competitor_rate = np.mean(self.competitor_rates)
        rate_competitiveness = new_rate - avg_competitor_rate
        
        # More competitive rate = more deposits
        if rate_competitiveness > 0:
            deposit_growth = min(0.05 * rate_competitiveness, 0.20)  # Max 20% growth
        else:
            deposit_growth = max(0.05 * rate_competitiveness, -0.30)  # Max 30% loss
        
        # 2. Net Interest Margin (NIM)
        # Bank's cost of funds
        cost_of_funds = 3.0  # Assume 3% cost
        nim = new_rate - cost_of_funds
        
        # Reward positive NIM, penalize negative
        nim_reward = nim if nim > 0 else nim * 2  # Double penalty for negative NIM
        
        # 3. Liquidity management
        # If excess liquidity, incentivize higher rates to deploy funds
        if self.liquidity_position > 0.7:
            liquidity_incentive = rate_adjustment * 0.1
        elif self.liquidity_position < 0.3:
            # Low liquidity, penalize high rates
            liquidity_incentive = -rate_adjustment * 0.2
        else:
            liquidity_incentive = 0
        
        # 4. Market positioning
        # Penalty for being significantly off-market (either way)
        if abs(rate_competitiveness) > 1.0:
            market_penalty = -0.5
        else:
            market_penalty = 0
        
        # Combined reward
        reward = (
            deposit_growth * 10 +  # Weight deposit growth heavily
            nim_reward * 5 +  # NIM is important
            liquidity_incentive * 3 +  # Liquidity management
            market_penalty  # Stay in market
        )
        
        # Update state
        self.current_step += 1
        
        # Simulate market dynamics
        self._update_market_conditions()
        
        # Update deposits based on rate decision
        self.segment_deposits *= (1 + deposit_growth)
        
        # Update liquidity (deposits increase liquidity)
        self.liquidity_position = min(1.0, self.liquidity_position + deposit_growth * 0.1)
        
        done = self.current_step >= self.max_steps
        
        info = {
            "new_rate": new_rate,
            "deposit_growth": deposit_growth,
            "nim": nim,
            "total_deposits": float(np.sum(self.segment_deposits)),
            "liquidity": self.liquidity_position
        }
        
        return self._get_observation(), reward, done, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current state observation."""
        obs = np.concatenate([
            self.competitor_rates,  # 5 values
            [self.liquidity_position],  # 1 value
            [self.inflation_rate],  # 1 value
            self.segment_deposits / 100,  # 3 values (normalized)
            [self.time_to_review / 30]  # 1 value (normalized)
        ])
        return obs.astype(np.float32)
    
    def _update_market_conditions(self):
        """Simulate market dynamics."""
        # Competitor rates drift
        self.competitor_rates += np.random.normal(0, 0.02, self.competitors)
        self.competitor_rates = np.clip(self.competitor_rates, 3.0, 8.0)
        
        # Inflation changes
        self.inflation_rate += np.random.normal(0, 0.05)
        self.inflation_rate = np.clip(self.inflation_rate, 0, 10)
        
        # Liquidity naturally decreases as funds are deployed
        self.liquidity_position = max(0, self.liquidity_position - 0.01)
        
        # Time countdown
        self.time_to_review = max(0, self.time_to_review - 1)
