"""
Actor-Critic Network

Neural network for actor-critic RL algorithms (A2C, A3C, PPO).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple


class ActorCriticNetwork(nn.Module):
    """
    Actor-Critic network with shared feature layers.
    
    Actor outputs action probabilities, Critic outputs state value.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (128, 64)
    ):
        """
        Initialize actor-critic network.
        
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
        
        # Actor head (policy)
        self.actor_head = nn.Linear(prev_dim, action_dim)
        
        # Critic head (value)
        self.critic_head = nn.Linear(prev_dim, 1)
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            (action_probs, value) tensors
        """
        features = self.feature_layers(state)
        
        # Actor: action probabilities (softmax for portfolio weights)
        action_logits = self.actor_head(features)
        action_probs = F.softmax(action_logits, dim=-1)
        
        # Critic: state value
        value = self.critic_head(features)
        
        return action_probs, value
    
    def sample_action(self, state: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Sample action from policy and get value.
        
        Args:
            state: State array
        
        Returns:
            (action, log_prob, value)
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            action_probs, value = self.forward(state_tensor)
        
        # Sample from categorical distribution
        dist = torch.distributions.Categorical(action_probs)
        action_idx = dist.sample()
        log_prob = dist.log_prob(action_idx)
        
        # Convert to portfolio weights (one-hot for now)
        action = torch.zeros(self.action_dim)
        action[action_idx] = 1.0
        
        return action.numpy(), log_prob.item(), value.item()
    
    def evaluate_actions(
        self,
        states: torch.Tensor,
        actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluate actions for given states.
        
        Args:
            states: State tensor [batch_size, state_dim]
            actions: Action tensor [batch_size, action_dim]
        
        Returns:
            (log_probs, values, entropy) tensors
        """
        action_probs, values = self.forward(states)
        
        # Log probabilities
        log_probs = torch.log(torch.sum(action_probs * actions, dim=-1) + 1e-8)
        
        # Entropy (for exploration bonus)
        entropy = -(action_probs * torch.log(action_probs + 1e-8)).sum(dim=-1)
        
        return log_probs, values.squeeze(-1), entropy


class ContinuousActorCriticNetwork(nn.Module):
    """
    Continuous actor-critic network for portfolio weights.
    
    Actor outputs mean and std for Gaussian policy.
    Critic outputs state value.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: Tuple[int, ...] = (128, 64)
    ):
        """
        Initialize continuous actor-critic network.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space (number of assets)
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
        
        # Actor heads
        self.actor_mean_head = nn.Linear(prev_dim, action_dim)
        self.actor_log_std_head = nn.Linear(prev_dim, action_dim)
        
        # Critic head
        self.critic_head = nn.Linear(prev_dim, 1)
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            state: State tensor [batch_size, state_dim]
        
        Returns:
            (mean, std, value) tensors
        """
        features = self.feature_layers(state)
        
        # Actor: mean and std (apply softmax to mean for valid portfolio weights)
        mean_logits = self.actor_mean_head(features)
        mean = F.softmax(mean_logits, dim=-1)
        
        log_std = self.actor_log_std_head(features)
        std = torch.exp(torch.clamp(log_std, -20, 2))
        
        # Critic: state value
        value = self.critic_head(features)
        
        return mean, std, value
    
    def sample_action(self, state: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Sample action from Gaussian policy and get value.
        
        Args:
            state: State array
        
        Returns:
            (action, log_prob, value)
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            mean, std, value = self.forward(state_tensor)
        
        # Sample from Gaussian
        dist = torch.distributions.Normal(mean, std)
        action = dist.sample()
        
        # Normalize to valid portfolio weights
        action = F.softmax(action, dim=-1)
        
        # Calculate log probability
        log_prob = dist.log_prob(action).sum(dim=-1)
        
        return action.squeeze(0).numpy(), log_prob.item(), value.item()
    
    def evaluate_actions(
        self,
        states: torch.Tensor,
        actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluate actions for given states.
        
        Args:
            states: State tensor [batch_size, state_dim]
            actions: Action tensor [batch_size, action_dim]
        
        Returns:
            (log_probs, values, entropy) tensors
        """
        mean, std, values = self.forward(states)
        
        # Log probabilities
        dist = torch.distributions.Normal(mean, std)
        log_probs = dist.log_prob(actions).sum(dim=-1)
        
        # Entropy
        entropy = dist.entropy().sum(dim=-1)
        
        return log_probs, values.squeeze(-1), entropy
