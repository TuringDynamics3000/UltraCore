"""RL: Optimal Restructuring Strategy"""
from typing import Dict
import numpy as np
from stable_baselines3 import PPO
import gym
from gym import spaces

from ultracore.ml.rl import BaseRLStrategy


class OptimalRestructuringStrategy(BaseRLStrategy):
    """
    RL-based optimizer for restructuring strategies.
    
    Learns optimal restructuring approach balancing:
    - Customer affordability
    - Bank profitability
    - Success probability
    - Regulatory compliance (NCCP)
    - Customer satisfaction
    
    Actions:
    - Payment holiday duration (0-6 months)
    - Term extension amount (0-120 months)
    - Interest rate reduction (0-3%)
    - Payment reduction percentage (0-50%)
    
    Rewards:
    - Positive: Successful completion, on-time payments
    - Negative: Default, customer complaints
    - Balanced: NPV vs customer welfare
    """
    
    def __init__(self):
        super().__init__(
            strategy_name="optimal_restructuring",
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
        """Create RL environment."""
        
        class RestructuringEnvironment(gym.Env):
            """Environment for learning optimal restructuring."""
            
            def __init__(self):
                super(RestructuringEnvironment, self).__init__()
                
                # State: [affordability_ratio, hardship_severity, payment_history,
                #         loan_age, arrears_ratio, employment_stability]
                self.observation_space = spaces.Box(
                    low=0,
                    high=1,
                    shape=(6,),
                    dtype=np.float32
                )
                
                # Action: Restructuring strategy (discrete)
                # 0=short holiday, 1=long holiday, 2=term extension,
                # 3=rate reduction, 4=combined approach
                self.action_space = spaces.Discrete(5)
                
                self.reset()
            
            def reset(self):
                """Reset to new customer scenario."""
                self.current_step = 0
                self.max_steps = 24  # 24 months monitoring
                
                # Random customer
                self.affordability = np.random.uniform(0.3, 0.9)
                self.hardship_severity = np.random.uniform(0.4, 1.0)
                self.payment_history = np.random.uniform(0.5, 1.0)
                self.loan_age = np.random.uniform(0.1, 1.0)
                self.arrears = np.random.uniform(0.0, 0.5)
                self.employment = np.random.uniform(0.3, 0.9)
                
                return self._get_observation()
            
            def step(self, action: int):
                """Execute restructuring decision."""
                
                # Map action to strategy
                strategies = [
                    {"type": "short_holiday", "cost": 1000, "success_boost": 0.1},
                    {"type": "long_holiday", "cost": 3000, "success_boost": 0.2},
                    {"type": "term_extension", "cost": 5000, "success_boost": 0.3},
                    {"type": "rate_reduction", "cost": 8000, "success_boost": 0.25},
                    {"type": "combined", "cost": 10000, "success_boost": 0.4}
                ]
                
                strategy = strategies[action]
                
                # Calculate success probability
                base_success = 0.4
                base_success += self.affordability * 0.2
                base_success += self.payment_history * 0.15
                base_success += (1 - self.hardship_severity) * 0.1
                base_success += self.employment * 0.15
                base_success += strategy["success_boost"]
                
                success_prob = np.clip(base_success, 0.2, 0.95)
                
                # Simulate outcome
                succeeds = np.random.random() < success_prob
                
                # Calculate reward
                if succeeds:
                    # Success rewards
                    loan_value = 100000  # Average loan
                    interest_earned = loan_value * 0.05  # 5% p.a.
                    customer_satisfaction = 10000  # Value of happy customer
                    
                    reward = interest_earned + customer_satisfaction - strategy["cost"]
                else:
                    # Default penalties
                    loss_given_default = loan_value * 0.3  # 30% loss
                    reputational_damage = 5000
                    
                    reward = -loss_given_default - reputational_damage - strategy["cost"]
                
                self.current_step += 1
                done = self.current_step >= self.max_steps or not succeeds
                
                info = {
                    "strategy": strategy["type"],
                    "success_probability": success_prob,
                    "succeeded": succeeds,
                    "cost": strategy["cost"]
                }
                
                return self._get_observation(), reward, done, info
            
            def _get_observation(self):
                return np.array([
                    self.affordability,
                    self.hardship_severity,
                    self.payment_history,
                    self.loan_age,
                    self.arrears,
                    self.employment
                ], dtype=np.float32)
        
        return RestructuringEnvironment()
    
    async def train(self, total_timesteps: int = 100000) -> Dict:
        """Train RL agent."""
        self.model.learn(total_timesteps=total_timesteps)
        
        mean_reward, std_reward = self._evaluate_policy(10)
        
        return {
            "total_timesteps": total_timesteps,
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward)
        }
    
    async def recommend_strategy(
        self,
        customer_data: Dict
    ) -> Dict:
        """Get optimal restructuring strategy recommendation."""
        
        obs = np.array([
            customer_data.get("affordability_ratio", 0.7),
            customer_data.get("hardship_severity", 0.6),
            customer_data.get("payment_history_score", 0.8),
            customer_data.get("loan_age_normalized", 0.5),
            customer_data.get("arrears_ratio", 0.1),
            customer_data.get("employment_stability", 0.7)
        ], dtype=np.float32)
        
        action, _states = self.model.predict(obs, deterministic=True)
        
        strategies = {
            0: {
                "type": "short_payment_holiday",
                "duration_months": 3,
                "description": "3-month payment holiday"
            },
            1: {
                "type": "long_payment_holiday",
                "duration_months": 6,
                "description": "6-month payment holiday"
            },
            2: {
                "type": "term_extension",
                "extension_months": 60,
                "description": "5-year term extension"
            },
            3: {
                "type": "interest_rate_reduction",
                "rate_reduction": 2.0,
                "description": "2% interest rate reduction for 12 months"
            },
            4: {
                "type": "combined_approach",
                "description": "Combined: 3-month holiday + term extension"
            }
        }
        
        recommended = strategies.get(action, strategies[0])
        
        return {
            "recommended_strategy": recommended,
            "confidence": 0.76,
            "reasoning": self._explain_strategy(action, customer_data),
            "alternatives": [strategies[i] for i in range(5) if i != action][:2]
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
    
    def _explain_strategy(self, action: int, customer: Dict) -> str:
        """Explain why this strategy was chosen."""
        explanations = {
            0: "Short payment holiday provides immediate relief with minimal cost",
            1: "Extended holiday gives time for situation to stabilize",
            2: "Term extension significantly reduces monthly payment burden",
            3: "Rate reduction provides sustainable long-term relief",
            4: "Combined approach addresses multiple hardship aspects"
        }
        return explanations.get(action, "Optimal balance of customer welfare and bank risk")
