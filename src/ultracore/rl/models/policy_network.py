"""
Policy Network

Neural network for policy-based RL algorithms (REINFORCE, PPO, A3C).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple


class PolicyNetwork(nn.Module):
    """
    Policy network that outputs action probabilities.
    
    Used for policy gradient methods (REINFORCE, PPO, A3C).
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (64, 32)
    ):
        """
        Initialize policy network.
        
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
        self.action_head = nn.Linear(prev_dim, action_dim)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            Action probabilities [batch_size, action_dim]
        """
        features = self.feature_layers(state)
        action_logits = self.action_head(features)
        action_probs = F.softmax(action_logits, dim=-1)
        
        return action_probs
    
    def sample_action(self, state: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Sample action from policy.
        
        Args:
            state: State array
        
        Returns:
            (action, log_prob)
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            action_probs = self.forward(state_tensor)
        
        # Sample from categorical distribution
        dist = torch.distributions.Categorical(action_probs)
        action_idx = dist.sample()
        log_prob = dist.log_prob(action_idx)
        
        # Convert to portfolio weights (one-hot for now, can be continuous)
        action = torch.zeros(self.action_dim)
        action[action_idx] = 1.0
        
        return action.numpy(), log_prob.item()
    
    def get_log_prob(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """
        Get log probability of action given state.
        
        Args:
            state: State tensor [batch_size, state_dim]
            action: Action tensor [batch_size, action_dim]
        
        Returns:
            Log probabilities [batch_size]
        """
        action_probs = self.forward(state)
        
        # For continuous actions (portfolio weights), use action as probabilities
        log_probs = torch.log(torch.sum(action_probs * action, dim=-1) + 1e-8)
        
        return log_probs


class ContinuousPolicyNetwork(nn.Module):
    """
    Continuous policy network for portfolio weights.
    
    Outputs mean and std for Gaussian policy.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (64, 32)
    ):
        """
        Initialize continuous policy network.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space (number of assets)
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
        self.mean_head = nn.Linear(prev_dim, action_dim)
        self.log_std_head = nn.Linear(prev_dim, action_dim)
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            (mean, std) tensors [batch_size, action_dim]
        """
        features = self.feature_layers(state)
        
        # Mean (apply softmax to get valid portfolio weights)
        mean_logits = self.mean_head(features)
        mean = F.softmax(mean_logits, dim=-1)
        
        # Std (ensure positive)
        log_std = self.log_std_head(features)
        std = torch.exp(torch.clamp(log_std, -20, 2))
        
        return mean, std
    
    def sample_action(self, state: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Sample action from Gaussian policy.
        
        Args:
            state: State array
        
        Returns:
            (action, log_prob)
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            mean, std = self.forward(state_tensor)
        
        # Sample from Gaussian
        dist = torch.distributions.Normal(mean, std)
        action = dist.sample()
        
        # Normalize to valid portfolio weights
        action = F.softmax(action, dim=-1)
        
        # Calculate log probability
        log_prob = dist.log_prob(action).sum(dim=-1)
        
        return action.squeeze(0).numpy(), log_prob.item()
    
    def get_log_prob(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """
        Get log probability of action given state.
        
        Args:
            state: State tensor [batch_size, state_dim]
            action: Action tensor [batch_size, action_dim]
        
        Returns:
            Log probabilities [batch_size]
        """
        mean, std = self.forward(state)
        
        dist = torch.distributions.Normal(mean, std)
        log_probs = dist.log_prob(action).sum(dim=-1)
        
        return log_probs
