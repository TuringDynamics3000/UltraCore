"""RL-based Dynamic Incentive Optimizer for RD Completion"""
from typing import Dict, Optional
import numpy as np
from stable_baselines3 import PPO

from ultracore.ml.rl import BaseRLStrategy
from .rd_environment import RecurringDepositEnvironment


class DynamicIncentiveOptimizer(BaseRLStrategy):
    """
    RL-based optimizer for RD completion incentives.
    
    Learns optimal strategies for:
    - Bonus interest rates for on-time payments
    - Completion bonuses at maturity
    - Missed payment penalty waivers
    - Loyalty rewards
    - Gamification elements
    
    Balances:
    - Customer retention and completion
    - Bank profitability
    - Customer satisfaction
    - Fair treatment
    """
    
    def __init__(self):
        super().__init__(
            strategy_name="rd_incentive_optimizer",
            version="1.0.0"
        )
        
        self.env = RecurringDepositEnvironment()
        
        self.model = PPO(
            "MlpPolicy",
            self.env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            verbose=1
        )
    
    async def train(self, total_timesteps: int = 100000) -> Dict:
        """Train RL agent to optimize incentives."""
        print(f"Training incentive optimizer for {total_timesteps} steps...")
        
        self.model.learn(total_timesteps=total_timesteps)
        
        mean_reward, std_reward = self._evaluate_policy(10)
        
        return {
            "total_timesteps": total_timesteps,
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward)
        }
    
    async def optimize_incentive(
        self,
        customer_segment: str,
        account_health: float,
        completion_risk: float,
        months_remaining: int
    ) -> Dict:
        """
        Get optimal incentive strategy.
        
        Returns:
            Recommended incentives and expected impact
        """
        # Build observation
        obs = np.array([
            account_health / 100,
            completion_risk,
            months_remaining / 60,
            0.5  # Placeholder for other features
        ], dtype=np.float32)
        
        # Get RL recommendation
        action, _states = self.model.predict(obs, deterministic=True)
        
        # Map action to incentive
        incentive = self._map_action_to_incentive(action, account_health, completion_risk)
        
        return incentive
    
    def _map_action_to_incentive(
        self,
        action: int,
        health: float,
        risk: float
    ) -> Dict:
        """Map RL action to concrete incentive."""
        
        if health < 50 or risk > 0.7:
            # High risk - aggressive incentive
            return {
                "type": "retention_package",
                "components": [
                    {"name": "waive_penalties", "value": "100%"},
                    {"name": "bonus_interest", "value": "1.0% additional"},
                    {"name": "completion_bonus", "value": ""},
                    {"name": "payment_holiday", "value": "1 month"}
                ],
                "cost_to_bank": 150.00,
                "expected_completion_lift": 0.35,
                "message": "Special support package to help you succeed"
            }
        elif health < 70 or risk > 0.5:
            # Moderate risk - balanced incentive
            return {
                "type": "encouragement_package",
                "components": [
                    {"name": "bonus_interest", "value": "0.5% additional"},
                    {"name": "completion_bonus", "value": ""},
                    {"name": "milestone_rewards", "value": "Badges"}
                ],
                "cost_to_bank": 75.00,
                "expected_completion_lift": 0.20,
                "message": "Rewards to keep you on track"
            }
        else:
            # Low risk - standard incentive
            return {
                "type": "standard_rewards",
                "components": [
                    {"name": "completion_bonus", "value": ""},
                    {"name": "loyalty_points", "value": "500 points"}
                ],
                "cost_to_bank": 30.00,
                "expected_completion_lift": 0.05,
                "message": "Thank you for your consistent savings"
            }
    
    def _evaluate_policy(self, n_episodes: int) -> tuple:
        """Evaluate trained policy."""
        rewards = []
        for _ in range(n_episodes):
            obs = self.env.reset()
            episode_reward = 0
            done = False
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, done, _ = self.env.step(action)
                episode_reward += reward
            rewards.append(episode_reward)
        return np.mean(rewards), np.std(rewards)
