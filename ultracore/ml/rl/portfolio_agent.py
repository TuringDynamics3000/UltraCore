"""
Reinforcement Learning for Portfolio Optimization
Uses Deep Q-Learning (DQN) for optimal position sizing and rebalancing
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum

class Action(str, Enum):
    HOLD = "hold"
    BUY_SMALL = "buy_small"      # +5% position
    BUY_MEDIUM = "buy_medium"    # +10% position
    BUY_LARGE = "buy_large"      # +20% position
    SELL_SMALL = "sell_small"    # -5% position
    SELL_MEDIUM = "sell_medium"  # -10% position
    SELL_LARGE = "sell_large"    # -20% position
    REBALANCE = "rebalance"

class PortfolioRLAgent:
    """
    Reinforcement Learning Agent for Portfolio Management
    
    State: Portfolio positions, market data, risk metrics
    Actions: Buy/sell/hold/rebalance decisions
    Reward: Risk-adjusted returns (Sharpe ratio)
    """
    
    def __init__(self):
        self.learning_rate = 0.001
        self.gamma = 0.95  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        
        # Q-table (in production, use neural network)
        self.q_table = {}
        
        # Experience replay buffer
        self.memory = []
        self.memory_size = 10000
        
        # Training history
        self.episodes = []
        self.total_rewards = []
    
    def get_state(self, portfolio: Dict[str, Any]) -> str:
        """
        Convert portfolio to state representation
        State includes:
        - Position sizes
        - Returns
        - Volatility
        - Sharpe ratio
        - Diversification
        """
        
        # Extract features
        total_value = portfolio.get("total_value", 0)
        positions = portfolio.get("positions", [])
        
        # Calculate state features
        features = []
        
        # 1. Portfolio concentration (Herfindahl index)
        if positions and total_value > 0:
            weights = [p.get("market_value", 0) / total_value for p in positions]
            concentration = sum(w**2 for w in weights)
            features.append(round(concentration, 2))
        else:
            features.append(0)
        
        # 2. Number of positions
        features.append(len(positions))
        
        # 3. Total return
        total_cost = sum(p.get("cost_basis", 0) for p in positions)
        if total_cost > 0:
            total_return = (total_value - total_cost) / total_cost
            features.append(round(total_return, 2))
        else:
            features.append(0)
        
        # 4. Largest position weight
        if positions and total_value > 0:
            max_weight = max(
                p.get("market_value", 0) / total_value 
                for p in positions
            )
            features.append(round(max_weight, 2))
        else:
            features.append(0)
        
        # Convert to state string
        return "-".join(str(f) for f in features)
    
    def select_action(
        self,
        state: str,
        portfolio: Dict[str, Any]
    ) -> Action:
        """
        Select action using epsilon-greedy policy
        """
        
        # Exploration: random action
        if np.random.random() < self.epsilon:
            return np.random.choice(list(Action))
        
        # Exploitation: best action from Q-table
        if state in self.q_table:
            q_values = self.q_table[state]
            best_action = max(q_values, key=q_values.get)
            return Action(best_action)
        
        # If state not seen, default action
        return self._get_default_action(portfolio)
    
    def calculate_reward(
        self,
        previous_portfolio: Dict[str, Any],
        current_portfolio: Dict[str, Any],
        action: Action
    ) -> float:
        """
        Calculate reward for action taken
        
        Reward = Risk-adjusted returns - Transaction costs - Risk penalty
        """
        
        # 1. Portfolio return
        prev_value = previous_portfolio.get("total_value", 0)
        curr_value = current_portfolio.get("total_value", 0)
        
        if prev_value > 0:
            portfolio_return = (curr_value - prev_value) / prev_value
        else:
            portfolio_return = 0
        
        # 2. Risk penalty (volatility)
        positions = current_portfolio.get("positions", [])
        if len(positions) > 0:
            # Simple risk measure: concentration
            total_value = curr_value
            if total_value > 0:
                weights = [
                    p.get("market_value", 0) / total_value 
                    for p in positions
                ]
                concentration = sum(w**2 for w in weights)
                risk_penalty = concentration * 0.1  # Penalty for concentration
            else:
                risk_penalty = 0
        else:
            risk_penalty = 0
        
        # 3. Transaction cost
        if action in [Action.BUY_SMALL, Action.BUY_MEDIUM, Action.BUY_LARGE,
                      Action.SELL_SMALL, Action.SELL_MEDIUM, Action.SELL_LARGE]:
            transaction_cost = 0.001  # 0.1% transaction cost
        elif action == Action.REBALANCE:
            transaction_cost = 0.002  # Higher cost for rebalancing
        else:
            transaction_cost = 0
        
        # 4. Diversification bonus
        diversification_bonus = 0
        if 5 <= len(positions) <= 15:  # Optimal diversification
            diversification_bonus = 0.01
        
        # Total reward
        reward = (
            portfolio_return * 100  # Scale up returns
            - risk_penalty * 10     # Scale up risk penalty
            - transaction_cost * 100
            + diversification_bonus * 100
        )
        
        return round(reward, 4)
    
    def update_q_value(
        self,
        state: str,
        action: Action,
        reward: float,
        next_state: str
    ):
        """
        Update Q-value using Q-learning algorithm
        Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        """
        
        # Initialize Q-table for state if not exists
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in Action}
        
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in Action}
        
        # Current Q-value
        current_q = self.q_table[state][action]
        
        # Max Q-value for next state
        max_next_q = max(self.q_table[next_state].values())
        
        # Update Q-value
        new_q = current_q + self.learning_rate * (
            reward + self.gamma * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def train_episode(
        self,
        initial_portfolio: Dict[str, Any],
        market_simulation: List[Dict[str, Any]],
        steps: int = 100
    ) -> Dict[str, Any]:
        """
        Train agent for one episode
        """
        
        portfolio = initial_portfolio.copy()
        total_reward = 0
        actions_taken = []
        
        for step in range(steps):
            # Get current state
            state = self.get_state(portfolio)
            
            # Select action
            action = self.select_action(state, portfolio)
            
            # Execute action (simulate)
            new_portfolio = self._execute_action(
                portfolio,
                action,
                market_simulation[step % len(market_simulation)]
            )
            
            # Calculate reward
            reward = self.calculate_reward(portfolio, new_portfolio, action)
            total_reward += reward
            
            # Get next state
            next_state = self.get_state(new_portfolio)
            
            # Update Q-value
            self.update_q_value(state, action, reward, next_state)
            
            # Store experience
            self.memory.append({
                "state": state,
                "action": action,
                "reward": reward,
                "next_state": next_state
            })
            
            # Limit memory size
            if len(self.memory) > self.memory_size:
                self.memory.pop(0)
            
            # Move to next state
            portfolio = new_portfolio
            actions_taken.append(action)
        
        # Record episode
        self.episodes.append({
            "episode": len(self.episodes) + 1,
            "total_reward": total_reward,
            "actions_taken": actions_taken,
            "final_portfolio_value": portfolio.get("total_value", 0)
        })
        
        self.total_rewards.append(total_reward)
        
        return {
            "episode": len(self.episodes),
            "total_reward": total_reward,
            "avg_reward": np.mean(self.total_rewards[-100:]),
            "q_table_size": len(self.q_table)
        }
    
    def get_optimal_action(
        self,
        portfolio: Dict[str, Any]
    ) -> Tuple[Action, float]:
        """
        Get optimal action for current portfolio (exploitation only)
        """
        
        state = self.get_state(portfolio)
        
        if state in self.q_table:
            q_values = self.q_table[state]
            best_action = max(q_values, key=q_values.get)
            confidence = q_values[best_action]
            return Action(best_action), confidence
        
        return self._get_default_action(portfolio), 0.5
    
    def _execute_action(
        self,
        portfolio: Dict[str, Any],
        action: Action,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate action execution
        In production, this would trigger actual trades
        """
        
        new_portfolio = portfolio.copy()
        
        # Simulate market movement
        market_return = market_data.get("return", 0)
        total_value = portfolio.get("total_value", 0)
        
        new_portfolio["total_value"] = total_value * (1 + market_return)
        
        return new_portfolio
    
    def _get_default_action(self, portfolio: Dict[str, Any]) -> Action:
        """Get default action based on simple rules"""
        
        positions_count = len(portfolio.get("positions", []))
        
        if positions_count < 5:
            return Action.BUY_MEDIUM
        elif positions_count > 15:
            return Action.SELL_SMALL
        else:
            return Action.HOLD

# Global RL agent
portfolio_rl_agent = PortfolioRLAgent()
