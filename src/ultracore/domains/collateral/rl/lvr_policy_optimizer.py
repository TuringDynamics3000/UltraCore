"""RL-based Dynamic LVR Policy Optimizer"""
from typing import Dict, Optional
import numpy as np
from stable_baselines3 import PPO
import gym
from gym import spaces

from ultracore.ml.rl import BaseRLStrategy


class DynamicLVRPolicyOptimizer(BaseRLStrategy):
    """
    RL-based optimizer for dynamic LVR policies.
    
    Learns optimal LVR limits based on:
    - Collateral type and quality
    - Market conditions
    - Customer risk profile
    - Historical default rates
    - Property location
    - Economic indicators
    
    Balances:
    - Loan volume (higher LVR = more loans)
    - Risk (higher LVR = higher risk)
    - Profitability (LMI income vs default losses)
    - Competition (market rates)
    """
    
    def __init__(self):
        super().__init__(
            strategy_name="dynamic_lvr_policy",
            version="1.0.0"
        )
        
        self.env = self._create_environment()
        
        self.model = PPO(
            "MlpPolicy",
            self.env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            verbose=1
        )
    
    def _create_environment(self) -> gym.Env:
        """Create RL environment for LVR policy optimization."""
        
        class LVRPolicyEnvironment(gym.Env):
            """
            Environment for learning optimal LVR policies.
            
            State Space:
            - Collateral characteristics (type, value, location)
            - Customer risk profile
            - Market conditions
            - Economic indicators
            - Competition rates
            
            Action Space:
            - LVR limit adjustment (-10% to +10% from baseline)
            
            Reward:
            - Positive: Successful loans, LMI income
            - Negative: Defaults, LVR breaches
            - Balanced: Risk-adjusted profitability
            """
            
            def __init__(self):
                super(LVRPolicyEnvironment, self).__init__()
                
                # State: [collateral_quality, customer_risk, market_trend, 
                #         competition_lvr, property_location_risk, economic_health]
                self.observation_space = spaces.Box(
                    low=0,
                    high=1,
                    shape=(6,),
                    dtype=np.float32
                )
                
                # Action: LVR adjustment in 5% increments (-10% to +10%)
                self.action_space = spaces.Discrete(5)  # [-10, -5, 0, +5, +10]
                
                self.baseline_lvr = 0.80  # 80% baseline
                self.reset()
            
            def reset(self):
                """Reset to new scenario."""
                self.current_step = 0
                self.max_steps = 100
                
                # Random market scenario
                self.collateral_quality = np.random.uniform(0.5, 1.0)
                self.customer_risk = np.random.uniform(0.3, 0.9)
                self.market_trend = np.random.uniform(0.0, 1.0)
                self.competition_lvr = np.random.uniform(0.75, 0.85)
                self.location_risk = np.random.uniform(0.2, 0.8)
                self.economic_health = np.random.uniform(0.4, 0.95)
                
                return self._get_observation()
            
            def step(self, action: int):
                """Execute LVR policy decision."""
                # Map action to LVR adjustment
                adjustments = [-0.10, -0.05, 0.0, 0.05, 0.10]
                lvr_adjustment = adjustments[action]
                new_lvr = self.baseline_lvr + lvr_adjustment
                new_lvr = np.clip(new_lvr, 0.60, 0.95)
                
                # Calculate outcomes
                
                # 1. Loan volume (higher LVR = more loans approved)
                competitive_advantage = new_lvr - self.competition_lvr
                volume_multiplier = 1.0 + (competitive_advantage * 2)
                
                # 2. Default probability
                base_default_rate = 0.02
                lvr_risk = (new_lvr - 0.70) * 0.10  # Higher LVR = higher risk
                customer_risk_factor = (1.0 - self.customer_risk) * 0.05
                market_risk = (1.0 - self.market_trend) * 0.03
                
                default_probability = base_default_rate + lvr_risk + customer_risk_factor + market_risk
                default_probability = np.clip(default_probability, 0.01, 0.20)
                
                # 3. LMI income (if LVR > 80%)
                lmi_income = 0.0
                if new_lvr > 0.80:
                    lmi_rate = (new_lvr - 0.80) * 0.02  # 2% per 1% over 80%
                    lmi_income = lmi_rate * volume_multiplier * 100  # Per loan
                
                # 4. Loss given default
                loss_severity = max(0, new_lvr - 0.70)  # Loss if property sold
                
                # Calculate reward
                loan_income = volume_multiplier * 5  # Base income per loan
                expected_loss = default_probability * loss_severity * 100
                
                reward = loan_income + lmi_income - expected_loss
                
                # Market dynamics
                self.market_trend += np.random.normal(0, 0.02)
                self.market_trend = np.clip(self.market_trend, 0, 1)
                
                self.current_step += 1
                done = self.current_step >= self.max_steps
                
                info = {
                    "lvr": new_lvr,
                    "volume_multiplier": volume_multiplier,
                    "default_probability": default_probability,
                    "lmi_income": lmi_income,
                    "expected_loss": expected_loss
                }
                
                return self._get_observation(), reward, done, info
            
            def _get_observation(self):
                return np.array([
                    self.collateral_quality,
                    self.customer_risk,
                    self.market_trend,
                    self.competition_lvr,
                    self.location_risk,
                    self.economic_health
                ], dtype=np.float32)
        
        return LVRPolicyEnvironment()
    
    async def train(self, total_timesteps: int = 100000) -> Dict:
        """Train RL agent to optimize LVR policies."""
        print(f"Training dynamic LVR policy optimizer for {total_timesteps} steps...")
        
        self.model.learn(total_timesteps=total_timesteps)
        
        mean_reward, std_reward = self._evaluate_policy(10)
        
        return {
            "total_timesteps": total_timesteps,
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward)
        }
    
    async def optimize_lvr_limit(
        self,
        collateral_quality: float,
        customer_risk_score: float,
        market_conditions: Dict,
        location: str
    ) -> Dict:
        """
        Get optimal LVR limit for given conditions.
        
        Returns:
            Optimal LVR limit and confidence
        """
        # Build observation
        obs = np.array([
            collateral_quality,
            customer_risk_score,
            market_conditions.get("market_trend", 0.7),
            market_conditions.get("competition_lvr", 0.80),
            market_conditions.get("location_risk", 0.3),
            market_conditions.get("economic_health", 0.85)
        ], dtype=np.float32)
        
        # Get RL recommendation
        action, _states = self.model.predict(obs, deterministic=True)
        
        # Map action to LVR
        adjustments = [-0.10, -0.05, 0.0, 0.05, 0.10]
        lvr_adjustment = adjustments[action]
        optimal_lvr = 0.80 + lvr_adjustment
        optimal_lvr = float(np.clip(optimal_lvr, 0.60, 0.95))
        
        # Reasoning
        if lvr_adjustment > 0:
            reasoning = "Market conditions favorable - can offer competitive higher LVR"
        elif lvr_adjustment < 0:
            reasoning = "Risk factors present - recommend conservative LVR"
        else:
            reasoning = "Standard LVR appropriate for current conditions"
        
        return {
            "optimal_lvr": optimal_lvr,
            "adjustment": float(lvr_adjustment),
            "confidence": 0.78,
            "reasoning": reasoning,
            "lmi_required": optimal_lvr > 0.80,
            "estimated_default_risk": self._estimate_default_risk(optimal_lvr, customer_risk_score)
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
    
    def _estimate_default_risk(self, lvr: float, customer_risk: float) -> float:
        """Estimate default probability."""
        base_rate = 0.02
        lvr_factor = max(0, lvr - 0.70) * 0.10
        customer_factor = (1 - customer_risk) * 0.05
        return min(base_rate + lvr_factor + customer_factor, 0.20)
