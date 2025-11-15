"""
Beta Agent - Policy Gradient (REINFORCE) for POD2 Income

Objective: Maximize after-tax income
Algorithm: REINFORCE (Monte Carlo Policy Gradient)
Target: >4% yield, moderate growth
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple
from .base_agent import BaseRLAgent
import sys
sys.path.append('/home/ubuntu/UltraCore/src')
from ultracore.rl.models.policy_network import ContinuousPolicyNetwork


class BetaAgent(BaseRLAgent):
    """
    Beta agent using Policy Gradient (REINFORCE) for income maximization.
    
    Uses continuous policy network to output portfolio weights.
    Optimizes for dividend income and capital gains with tax efficiency.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (64, 32),
        learning_rate: float = 0.001,
        discount_factor: float = 0.99
    ):
        """
        Initialize Beta agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of assets
            hidden_dims: Hidden layer dimensions
            learning_rate: Learning rate
            discount_factor: Discount factor (gamma)
        """
        super().__init__(
            name='Beta',
            state_dim=state_dim,
            action_dim=action_dim,
            objective='income',
            learning_rate=learning_rate,
            discount_factor=discount_factor
        )
        
        # Policy network
        self.policy_net = ContinuousPolicyNetwork(state_dim, action_dim, hidden_dims)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        # Episode buffer
        self.episode_states = []
        self.episode_actions = []
        self.episode_rewards = []
        self.episode_log_probs = []
    
    def select_action(self, state: np.ndarray, training: bool = True) -> np.ndarray:
        """
        Select action using policy network.
        
        Args:
            state: Current state
            training: Whether in training mode
        
        Returns:
            Action (portfolio weights)
        """
        action, log_prob = self.policy_net.sample_action(state)
        
        # Store for training
        if training:
            self.episode_states.append(state)
            self.episode_actions.append(action)
            self.episode_log_probs.append(log_prob)
        
        return action
    
    def store_reward(self, reward: float):
        """Store reward for current step"""
        self.episode_rewards.append(reward)
    
    def train(self) -> Dict[str, float]:
        """
        Train agent using REINFORCE algorithm.
        
        Updates policy network using Monte Carlo returns.
        
        Returns:
            Dict of training metrics
        """
        if len(self.episode_rewards) == 0:
            return {}
        
        # Calculate discounted returns
        returns = []
        G = 0
        for reward in reversed(self.episode_rewards):
            G = reward + self.discount_factor * G
            returns.insert(0, G)
        
        returns = torch.FloatTensor(returns)
        
        # Normalize returns (improves stability)
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # Recalculate log probs with gradients enabled
        states = torch.FloatTensor(np.array(self.episode_states))
        actions = torch.FloatTensor(np.array(self.episode_actions))
        log_probs = self.policy_net.get_log_prob(states, actions)
        
        # Calculate policy gradient loss
        loss = -(log_probs * returns.detach()).mean()
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        
        self.optimizer.step()
        
        # Log episode
        episode_return = sum(self.episode_rewards)
        episode_length = len(self.episode_rewards)
        self.log_episode(episode_return, episode_length)
        
        # Clear episode buffer
        metrics = {
            'loss': loss.item(),
            'episode_return': episode_return,
            'episode_length': episode_length,
            'mean_return': returns.mean().item()
        }
        
        self.episode_states = []
        self.episode_actions = []
        self.episode_rewards = []
        self.episode_log_probs = []
        
        self.training_steps += 1
        
        return metrics
    
    def save(self, path: str):
        """Save agent including policy network"""
        import pickle
        from pathlib import Path
        
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        state_dict = {
            'name': self.name,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'policy_net_state': self.policy_net.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths,
            'training_steps': self.training_steps
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state_dict, f)
    
    def load(self, path: str):
        """Load agent including policy network"""
        import pickle
        
        with open(path, 'rb') as f:
            state_dict = pickle.load(f)
        
        self.name = state_dict['name']
        self.state_dim = state_dict['state_dim']
        self.action_dim = state_dict['action_dim']
        self.learning_rate = state_dict['learning_rate']
        self.discount_factor = state_dict['discount_factor']
        
        # Reconstruct network
        self.policy_net = ContinuousPolicyNetwork(self.state_dim, self.action_dim)
        self.policy_net.load_state_dict(state_dict['policy_net_state'])
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.optimizer.load_state_dict(state_dict['optimizer_state'])
        
        self.episode_rewards = state_dict.get('episode_rewards', [])
        self.episode_lengths = state_dict.get('episode_lengths', [])
        self.training_steps = state_dict.get('training_steps', 0)
