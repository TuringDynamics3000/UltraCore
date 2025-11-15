"""
Gamma Agent - DQN for POD3 Growth

Objective: Maximize Sharpe ratio
Algorithm: Deep Q-Network (DQN) with Experience Replay
Target: 15-25% volatility, high returns
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Tuple
from .base_agent import BaseRLAgent
import sys
sys.path.append('/home/ubuntu/UltraCore/src')
from ultracore.rl.models.q_network import PortfolioQNetwork
from ultracore.rl.utils.replay_buffer import ReplayBuffer


class GammaAgent(BaseRLAgent):
    """
    Gamma agent using DQN for Sharpe ratio maximization.
    
    Uses deep Q-network with experience replay and target network.
    Optimizes for risk-adjusted returns.
    """
    
    def __init__(
        self,
        state_dim: int,
        n_assets: int,
        n_levels: int = 11,
        hidden_dims: Tuple[int, ...] = (128, 64, 32),
        learning_rate: float = 0.001,
        discount_factor: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        buffer_size: int = 10000,
        batch_size: int = 32,
        target_update_freq: int = 100
    ):
        """
        Initialize Gamma agent.
        
        Args:
            state_dim: Dimension of state space
            n_assets: Number of assets
            n_levels: Number of allocation levels per asset
            hidden_dims: Hidden layer dimensions
            learning_rate: Learning rate
            discount_factor: Discount factor (gamma)
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay rate
            epsilon_min: Minimum epsilon
            buffer_size: Replay buffer size
            batch_size: Training batch size
            target_update_freq: Steps between target network updates
        """
        super().__init__(
            name='Gamma',
            state_dim=state_dim,
            action_dim=n_assets,
            objective='sharpe',
            learning_rate=learning_rate,
            discount_factor=discount_factor
        )
        
        self.n_assets = n_assets
        self.n_levels = n_levels
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        
        # Q-networks
        self.q_net = PortfolioQNetwork(state_dim, n_assets, n_levels, hidden_dims)
        self.target_net = PortfolioQNetwork(state_dim, n_assets, n_levels, hidden_dims)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=learning_rate)
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
        
        # Training counter
        self.update_counter = 0
    
    def select_action(self, state: np.ndarray, training: bool = True) -> np.ndarray:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode
        
        Returns:
            Action (portfolio weights)
        """
        epsilon = self.epsilon if training else 0.0
        action = self.q_net.get_action(state, epsilon)
        
        return action
    
    def store_transition(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """Store transition in replay buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train(self) -> Dict[str, float]:
        """
        Train agent using DQN algorithm.
        
        Samples batch from replay buffer and updates Q-network.
        
        Returns:
            Dict of training metrics
        """
        if len(self.replay_buffer) < self.batch_size:
            return {}
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        states = torch.FloatTensor(states)
        actions = torch.FloatTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)
        
        # Current Q-values
        q_values = self.q_net(states)  # [batch, n_assets, n_levels]
        
        # Convert actions (weights) to level indices
        action_levels = (actions * (self.n_levels - 1)).long()  # [batch, n_assets]
        
        # Gather Q-values for taken actions
        q_values_selected = torch.gather(
            q_values,
            dim=2,
            index=action_levels.unsqueeze(-1)
        ).squeeze(-1)  # [batch, n_assets]
        
        # Mean Q-value across assets (portfolio Q-value)
        q_values_portfolio = q_values_selected.mean(dim=1)  # [batch]
        
        # Target Q-values
        with torch.no_grad():
            next_q_values = self.target_net(next_states)  # [batch, n_assets, n_levels]
            next_q_max = next_q_values.max(dim=2)[0].mean(dim=1)  # [batch]
            
            target_q = rewards + (1 - dones) * self.discount_factor * next_q_max
        
        # Loss
        loss = nn.MSELoss()(q_values_portfolio, target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network
        self.update_counter += 1
        if self.update_counter % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.training_steps += 1
        
        return {
            'loss': loss.item(),
            'q_value': q_values_portfolio.mean().item(),
            'epsilon': self.epsilon,
            'buffer_size': len(self.replay_buffer)
        }
    
    def save(self, path: str):
        """Save agent including Q-networks"""
        import pickle
        from pathlib import Path
        
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        state_dict = {
            'name': self.name,
            'state_dim': self.state_dim,
            'n_assets': self.n_assets,
            'n_levels': self.n_levels,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'epsilon_decay': self.epsilon_decay,
            'epsilon_min': self.epsilon_min,
            'batch_size': self.batch_size,
            'target_update_freq': self.target_update_freq,
            'q_net_state': self.q_net.state_dict(),
            'target_net_state': self.target_net.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'update_counter': self.update_counter,
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths,
            'training_steps': self.training_steps
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state_dict, f)
    
    def load(self, path: str):
        """Load agent including Q-networks"""
        import pickle
        
        with open(path, 'rb') as f:
            state_dict = pickle.load(f)
        
        self.name = state_dict['name']
        self.state_dim = state_dict['state_dim']
        self.n_assets = state_dict['n_assets']
        self.n_levels = state_dict['n_levels']
        self.learning_rate = state_dict['learning_rate']
        self.discount_factor = state_dict['discount_factor']
        self.epsilon = state_dict['epsilon']
        self.epsilon_decay = state_dict['epsilon_decay']
        self.epsilon_min = state_dict['epsilon_min']
        self.batch_size = state_dict['batch_size']
        self.target_update_freq = state_dict['target_update_freq']
        self.update_counter = state_dict['update_counter']
        
        # Reconstruct networks
        self.q_net = PortfolioQNetwork(self.state_dim, self.n_assets, self.n_levels)
        self.q_net.load_state_dict(state_dict['q_net_state'])
        
        self.target_net = PortfolioQNetwork(self.state_dim, self.n_assets, self.n_levels)
        self.target_net.load_state_dict(state_dict['target_net_state'])
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=self.learning_rate)
        self.optimizer.load_state_dict(state_dict['optimizer_state'])
        
        self.episode_rewards = state_dict.get('episode_rewards', [])
        self.episode_lengths = state_dict.get('episode_lengths', [])
        self.training_steps = state_dict.get('training_steps', 0)
