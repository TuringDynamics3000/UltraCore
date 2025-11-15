"""
Base RL Agent

Abstract base class for all RL agents in UltraOptimiser.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, List, Tuple, Optional
import pickle
from pathlib import Path


class BaseRLAgent(ABC):
    """
    Abstract base class for RL agents.
    
    All agents must implement:
    - select_action: Choose action given state
    - train: Update agent from experience
    - save: Save agent to disk
    - load: Load agent from disk
    """
    
    def __init__(
        self,
        name: str,
        state_dim: int,
        action_dim: int,
        objective: str,
        learning_rate: float = 0.001,
        discount_factor: float = 0.99
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (Alpha, Beta, Gamma, Delta)
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            objective: Optimization objective
            learning_rate: Learning rate
            discount_factor: Discount factor (gamma)
        """
        self.name = name
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.objective = objective
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Training metrics
        self.episode_rewards = []
        self.episode_lengths = []
        self.training_steps = 0
    
    @abstractmethod
    def select_action(self, state: np.ndarray, training: bool = True) -> np.ndarray:
        """
        Select action given current state.
        
        Args:
            state: Current state observation
            training: Whether in training mode (affects exploration)
        
        Returns:
            Action to take
        """
        pass
    
    @abstractmethod
    def train(self, *args, **kwargs) -> Dict[str, float]:
        """
        Train agent from experience.
        
        Returns:
            Dict of training metrics (loss, etc.)
        """
        pass
    
    def save(self, path: str):
        """
        Save agent to disk.
        
        Args:
            path: Path to save agent
        """
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        state_dict = {
            'name': self.name,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'objective': self.objective,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths,
            'training_steps': self.training_steps
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state_dict, f)
    
    def load(self, path: str):
        """
        Load agent from disk.
        
        Args:
            path: Path to load agent from
        """
        with open(path, 'rb') as f:
            state_dict = pickle.load(f)
        
        self.name = state_dict['name']
        self.state_dim = state_dict['state_dim']
        self.action_dim = state_dict['action_dim']
        self.objective = state_dict['objective']
        self.learning_rate = state_dict['learning_rate']
        self.discount_factor = state_dict['discount_factor']
        self.episode_rewards = state_dict.get('episode_rewards', [])
        self.episode_lengths = state_dict.get('episode_lengths', [])
        self.training_steps = state_dict.get('training_steps', 0)
    
    def log_episode(self, episode_reward: float, episode_length: int):
        """Log episode metrics"""
        self.episode_rewards.append(episode_reward)
        self.episode_lengths.append(episode_length)
    
    def get_metrics(self) -> Dict[str, float]:
        """Get training metrics"""
        if len(self.episode_rewards) == 0:
            return {}
        
        return {
            'mean_reward': np.mean(self.episode_rewards[-100:]),
            'mean_length': np.mean(self.episode_lengths[-100:]),
            'total_episodes': len(self.episode_rewards),
            'training_steps': self.training_steps
        }
