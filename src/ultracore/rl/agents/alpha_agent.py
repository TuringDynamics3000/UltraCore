"""
Alpha Agent - Q-Learning for POD1 Preservation

Objective: Minimize volatility, preserve capital
Algorithm: Tabular Q-Learning
Target: <10% volatility, positive returns
"""

import numpy as np
from typing import Dict, Tuple
from .base_agent import BaseRLAgent


class AlphaAgent(BaseRLAgent):
    """
    Alpha agent using Q-Learning for capital preservation.
    
    Uses discretized state space and tabular Q-learning.
    Suitable for low-dimensional problems with clear state boundaries.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        n_state_bins: int = 10,
        n_action_bins: int = 5,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        """
        Initialize Alpha agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of assets
            n_state_bins: Number of bins per state dimension
            n_action_bins: Number of allocation levels per asset (e.g., 5 = 0%, 25%, 50%, 75%, 100%)
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay rate
            epsilon_min: Minimum epsilon
        """
        super().__init__(
            name='Alpha',
            state_dim=state_dim,
            action_dim=action_dim,
            objective='volatility',
            learning_rate=learning_rate,
            discount_factor=discount_factor
        )
        
        self.n_state_bins = n_state_bins
        self.n_action_bins = n_action_bins
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table: state_bins^state_dim × action_bins^action_dim
        # For memory efficiency, use dict instead of full array
        self.q_table = {}
        
        # State bounds for discretization (learned online)
        self.state_mins = None
        self.state_maxs = None
    
    def _discretize_state(self, state: np.ndarray) -> Tuple[int, ...]:
        """
        Discretize continuous state to discrete bins.
        
        Args:
            state: Continuous state vector
        
        Returns:
            Tuple of discrete state indices
        """
        # Initialize bounds if first time
        if self.state_mins is None:
            self.state_mins = state.copy()
            self.state_maxs = state.copy()
        else:
            self.state_mins = np.minimum(self.state_mins, state)
            self.state_maxs = np.maximum(self.state_maxs, state)
        
        # Discretize each dimension
        discrete_state = []
        for i in range(len(state)):
            if self.state_maxs[i] > self.state_mins[i]:
                # Normalize to [0, 1]
                normalized = (state[i] - self.state_mins[i]) / (self.state_maxs[i] - self.state_mins[i])
                # Bin to [0, n_bins-1]
                bin_idx = int(normalized * (self.n_state_bins - 1))
                bin_idx = np.clip(bin_idx, 0, self.n_state_bins - 1)
            else:
                bin_idx = 0
            discrete_state.append(bin_idx)
        
        return tuple(discrete_state)
    
    def _discretize_action(self, action: np.ndarray) -> Tuple[int, ...]:
        """
        Discretize continuous action to discrete bins.
        
        Args:
            action: Continuous action vector (portfolio weights)
        
        Returns:
            Tuple of discrete action indices
        """
        discrete_action = []
        for weight in action:
            # Map [0, 1] to [0, n_action_bins-1]
            bin_idx = int(weight * (self.n_action_bins - 1))
            bin_idx = np.clip(bin_idx, 0, self.n_action_bins - 1)
            discrete_action.append(bin_idx)
        
        return tuple(discrete_action)
    
    def _continuous_action(self, discrete_action: Tuple[int, ...]) -> np.ndarray:
        """
        Convert discrete action to continuous weights.
        
        Args:
            discrete_action: Tuple of discrete action indices
        
        Returns:
            Continuous action vector (normalized weights)
        """
        # Convert bins to weights
        weights = np.array([idx / (self.n_action_bins - 1) for idx in discrete_action])
        
        # Normalize to sum to 1
        weights = weights / (weights.sum() + 1e-8)
        
        return weights
    
    def _get_q_value(self, state: Tuple[int, ...], action: Tuple[int, ...]) -> float:
        """Get Q-value for state-action pair"""
        key = (state, action)
        return self.q_table.get(key, 0.0)
    
    def _set_q_value(self, state: Tuple[int, ...], action: Tuple[int, ...], value: float):
        """Set Q-value for state-action pair"""
        key = (state, action)
        self.q_table[key] = value
    
    def select_action(self, state: np.ndarray, training: bool = True) -> np.ndarray:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode
        
        Returns:
            Action (portfolio weights)
        """
        discrete_state = self._discretize_state(state)
        
        # Epsilon-greedy exploration
        if training and np.random.random() < self.epsilon:
            # Random action
            discrete_action = tuple(np.random.randint(0, self.n_action_bins, size=self.action_dim))
        else:
            # Greedy action (max Q-value)
            best_action = None
            best_q = -np.inf
            
            # Try all possible actions (limited by n_action_bins)
            # For efficiency, sample random actions instead of exhaustive search
            n_samples = min(1000, self.n_action_bins ** self.action_dim)
            for _ in range(n_samples):
                action = tuple(np.random.randint(0, self.n_action_bins, size=self.action_dim))
                q = self._get_q_value(discrete_state, action)
                if q > best_q:
                    best_q = q
                    best_action = action
            
            discrete_action = best_action if best_action is not None else tuple([0] * self.action_dim)
        
        # Convert to continuous action
        continuous_action = self._continuous_action(discrete_action)
        
        return continuous_action
    
    def train(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ) -> Dict[str, float]:
        """
        Update Q-table using Q-learning update rule.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        
        Returns:
            Dict of training metrics
        """
        # Discretize
        discrete_state = self._discretize_state(state)
        discrete_action = self._discretize_action(action)
        discrete_next_state = self._discretize_state(next_state)
        
        # Current Q-value
        current_q = self._get_q_value(discrete_state, discrete_action)
        
        # Max Q-value for next state
        if done:
            max_next_q = 0.0
        else:
            # Sample actions to find max Q
            max_next_q = -np.inf
            for _ in range(100):  # Sample 100 random actions
                next_action = tuple(np.random.randint(0, self.n_action_bins, size=self.action_dim))
                q = self._get_q_value(discrete_next_state, next_action)
                max_next_q = max(max_next_q, q)
            
            if max_next_q == -np.inf:
                max_next_q = 0.0
        
        # Q-learning update
        target_q = reward + self.discount_factor * max_next_q
        new_q = current_q + self.learning_rate * (target_q - current_q)
        
        # Update Q-table
        self._set_q_value(discrete_state, discrete_action, new_q)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.training_steps += 1
        
        return {
            'q_value': new_q,
            'td_error': abs(target_q - current_q),
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table)
        }
    
    def save(self, path: str):
        """Save agent including Q-table"""
        import pickle
        
        state_dict = {
            'name': self.name,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'n_state_bins': self.n_state_bins,
            'n_action_bins': self.n_action_bins,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'epsilon_decay': self.epsilon_decay,
            'epsilon_min': self.epsilon_min,
            'q_table': self.q_table,
            'state_mins': self.state_mins,
            'state_maxs': self.state_maxs,
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths,
            'training_steps': self.training_steps
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state_dict, f)
    
    def load(self, path: str):
        """Load agent including Q-table"""
        import pickle
        
        with open(path, 'rb') as f:
            state_dict = pickle.load(f)
        
        self.name = state_dict['name']
        self.state_dim = state_dict['state_dim']
        self.action_dim = state_dict['action_dim']
        self.n_state_bins = state_dict['n_state_bins']
        self.n_action_bins = state_dict['n_action_bins']
        self.learning_rate = state_dict['learning_rate']
        self.discount_factor = state_dict['discount_factor']
        self.epsilon = state_dict['epsilon']
        self.epsilon_decay = state_dict['epsilon_decay']
        self.epsilon_min = state_dict['epsilon_min']
        self.q_table = state_dict['q_table']
        self.state_mins = state_dict.get('state_mins')
        self.state_maxs = state_dict.get('state_maxs')
        self.episode_rewards = state_dict.get('episode_rewards', [])
        self.episode_lengths = state_dict.get('episode_lengths', [])
        self.training_steps = state_dict.get('training_steps', 0)
