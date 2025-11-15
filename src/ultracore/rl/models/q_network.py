"""
Q-Network

Deep Q-Network for value-based RL algorithms (DQN, Double DQN, Dueling DQN).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple


class QNetwork(nn.Module):
    """
    Q-Network that estimates Q-values for state-action pairs.
    
    Used for DQN and variants.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (128, 64, 32)
    ):
        """
        Initialize Q-network.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            hidden_dims: Tuple of hidden layer dimensions
        """
        super().__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Build network layers
        layers = []
        prev_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim
        
        self.feature_layers = nn.Sequential(*layers)
        self.q_head = nn.Linear(prev_dim, action_dim)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            Q-values [batch_size, action_dim]
        """
        features = self.feature_layers(state)
        q_values = self.q_head(features)
        
        return q_values
    
    def get_action(self, state: np.ndarray, epsilon: float = 0.0) -> int:
        """
        Get action using epsilon-greedy policy.
        
        Args:
            state: State array
            epsilon: Exploration rate
        
        Returns:
            Action index
        """
        if np.random.random() < epsilon:
            return np.random.randint(self.action_dim)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            q_values = self.forward(state_tensor)
        
        return q_values.argmax(dim=-1).item()


class DuelingQNetwork(nn.Module):
    """
    Dueling Q-Network that separates value and advantage streams.
    
    Improves learning by explicitly representing state value and action advantages.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (128, 64)
    ):
        """
        Initialize dueling Q-network.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            hidden_dims: Tuple of hidden layer dimensions
        """
        super().__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Shared feature layers
        layers = []
        prev_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim
        
        self.feature_layers = nn.Sequential(*layers)
        
        # Value stream
        self.value_stream = nn.Sequential(
            nn.Linear(prev_dim, prev_dim // 2),
            nn.ReLU(),
            nn.Linear(prev_dim // 2, 1)
        )
        
        # Advantage stream
        self.advantage_stream = nn.Sequential(
            nn.Linear(prev_dim, prev_dim // 2),
            nn.ReLU(),
            nn.Linear(prev_dim // 2, action_dim)
        )
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            Q-values [batch_size, action_dim]
        """
        features = self.feature_layers(state)
        
        # Value and advantage
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Combine: Q(s,a) = V(s) + (A(s,a) - mean(A(s,a)))
        q_values = value + (advantage - advantage.mean(dim=-1, keepdim=True))
        
        return q_values
    
    def get_action(self, state: np.ndarray, epsilon: float = 0.0) -> int:
        """
        Get action using epsilon-greedy policy.
        
        Args:
            state: State array
            epsilon: Exploration rate
        
        Returns:
            Action index
        """
        if np.random.random() < epsilon:
            return np.random.randint(self.action_dim)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            q_values = self.forward(state_tensor)
        
        return q_values.argmax(dim=-1).item()


class PortfolioQNetwork(nn.Module):
    """
    Q-Network specialized for portfolio optimization.
    
    Outputs Q-values for each asset allocation level.
    """
    
    def __init__(
        self,
        state_dim: int,
        n_assets: int,
        n_levels: int = 11,  # 0%, 10%, 20%, ..., 100%
        hidden_dims: Tuple[int, ...] = (128, 64, 32)
    ):
        """
        Initialize portfolio Q-network.
        
        Args:
            state_dim: Dimension of state space
            n_assets: Number of assets
            n_levels: Number of allocation levels per asset
            hidden_dims: Tuple of hidden layer dimensions
        """
        super().__init__()
        
        self.state_dim = state_dim
        self.n_assets = n_assets
        self.n_levels = n_levels
        
        # Build network layers
        layers = []
        prev_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim
        
        self.feature_layers = nn.Sequential(*layers)
        
        # Separate Q-head for each asset
        self.q_heads = nn.ModuleList([
            nn.Linear(prev_dim, n_levels) for _ in range(n_assets)
        ])
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            Q-values [batch_size, n_assets, n_levels]
        """
        features = self.feature_layers(state)
        
        # Get Q-values for each asset
        q_values = torch.stack([head(features) for head in self.q_heads], dim=1)
        
        return q_values
    
    def get_action(self, state: np.ndarray, epsilon: float = 0.0) -> np.ndarray:
        """
        Get portfolio allocation using epsilon-greedy policy.
        
        Args:
            state: State array
            epsilon: Exploration rate
        
        Returns:
            Portfolio weights array
        """
        if np.random.random() < epsilon:
            # Random allocation
            weights = np.random.random(self.n_assets)
            weights = weights / weights.sum()
            return weights
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            q_values = self.forward(state_tensor)  # [1, n_assets, n_levels]
        
        # Select best level for each asset
        best_levels = q_values.argmax(dim=-1).squeeze(0).numpy()  # [n_assets]
        
        # Convert levels to weights
        weights = best_levels / (self.n_levels - 1)  # Normalize to [0, 1]
        weights = weights / (weights.sum() + 1e-8)  # Normalize to sum to 1
        
        return weights
