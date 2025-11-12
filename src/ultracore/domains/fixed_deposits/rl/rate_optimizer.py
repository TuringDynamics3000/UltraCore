"""Dynamic Rate Optimizer using Reinforcement Learning"""
from typing import Dict, Optional
import numpy as np
from stable_baselines3 import PPO, A2C

from ultracore.ml.rl import BaseRLStrategy
from .fd_environment import FixedDepositEnvironment


class DynamicRateOptimizer(BaseRLStrategy):
    """
    RL-based dynamic interest rate optimizer for fixed deposits.
    
    Uses PPO (Proximal Policy Optimization) to learn optimal pricing
    strategies that balance:
    - Customer acquisition/retention
    - Profitability (NIM)
    - Competitive positioning
    - Liquidity management
    
    Adapts rates in real-time based on:
    - Market conditions
    - Competitor actions
    - Customer behavior
    - Economic indicators
    """
    
    def __init__(
        self,
        base_rate: float = 5.0,
        algorithm: str = "ppo"
    ):
        super().__init__(
            strategy_name="fd_rate_optimizer",
            version="1.0.0"
        )
        
        self.base_rate = base_rate
        self.algorithm = algorithm
        
        # Create environment
        self.env = FixedDepositEnvironment(base_rate=base_rate)
        
        # Initialize RL agent
        if algorithm == "ppo":
            self.model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                verbose=1
            )
        else:  # A2C
            self.model = A2C(
                "MlpPolicy",
                self.env,
                learning_rate=7e-4,
                n_steps=5,
                gamma=0.99,
                verbose=1
            )
    
    async def train(self, total_timesteps: int = 100000) -> Dict:
        """
        Train the RL agent to optimize rates.
        
        Args:
            total_timesteps: Number of environment steps for training
        
        Returns:
            Training metrics
        """
        print(f"Training {self.algorithm.upper()} agent for {total_timesteps} steps...")
        
        self.model.learn(total_timesteps=total_timesteps)
        
        # Evaluate trained policy
        mean_reward, std_reward = self._evaluate_policy(n_eval_episodes=10)
        
        return {
            "algorithm": self.algorithm,
            "total_timesteps": total_timesteps,
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward)
        }
    
    async def optimize_rate(
        self,
        market_conditions: Dict,
        customer_segment: str = "retail",
        term_months: int = 12
    ) -> Dict:
        """
        Get optimal interest rate for current conditions.
        
        Args:
            market_conditions: Current market state
            customer_segment: Target customer segment
            term_months: FD term in months
        
        Returns:
            Optimal rate and confidence
        """
        # Build observation from market conditions
        observation = self._build_observation(market_conditions)
        
        # Get RL agent's recommendation
        action, _states = self.model.predict(observation, deterministic=True)
        
        # Map action to rate adjustment
        rate_adjustment = (action - 10) * 0.05
        optimal_rate = self.base_rate + rate_adjustment
        
        # Get value estimate (confidence proxy)
        value = self.model.policy.predict_values(
            self.model.policy.obs_to_tensor(observation)[0]
        )
        confidence = float(1 / (1 + np.exp(-value)))  # Sigmoid for 0-1 range
        
        return {
            "optimal_rate": float(optimal_rate),
            "base_rate": float(self.base_rate),
            "adjustment": float(rate_adjustment),
            "confidence": confidence,
            "reasoning": self._explain_decision(rate_adjustment, market_conditions)
        }
    
    async def save(self, path: str):
        """Save trained model."""
        self.model.save(path)
    
    async def load(self, path: str):
        """Load trained model."""
        if self.algorithm == "ppo":
            self.model = PPO.load(path, env=self.env)
        else:
            self.model = A2C.load(path, env=self.env)
    
    def _evaluate_policy(self, n_eval_episodes: int = 10) -> tuple:
        """Evaluate trained policy."""
        rewards = []
        
        for _ in range(n_eval_episodes):
            obs = self.env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                action, _states = self.model.predict(obs, deterministic=True)
                obs, reward, done, info = self.env.step(action)
                episode_reward += reward
            
            rewards.append(episode_reward)
        
        return np.mean(rewards), np.std(rewards)
    
    def _build_observation(self, market_conditions: Dict) -> np.ndarray:
        """Build observation vector from market conditions."""
        # Extract market data
        competitor_rates = market_conditions.get("competitor_rates", [5.0] * 5)
        liquidity = market_conditions.get("liquidity_position", 0.5)
        inflation = market_conditions.get("inflation_rate", 2.5)
        deposits = market_conditions.get("segment_deposits", [10.0, 25.0, 50.0])
        time_to_review = market_conditions.get("time_to_review", 30)
        
        obs = np.concatenate([
            competitor_rates,
            [liquidity],
            [inflation],
            np.array(deposits) / 100,
            [time_to_review / 30]
        ])
        
        return obs.astype(np.float32)
    
    def _explain_decision(self, adjustment: float, conditions: Dict) -> str:
        """Explain rate adjustment decision."""
        if adjustment > 0.2:
            return "Increasing rate to attract deposits due to high liquidity and competitive pressure"
        elif adjustment < -0.2:
            return "Decreasing rate to improve NIM as deposits are sufficient"
        else:
            return "Maintaining competitive rate positioning"
