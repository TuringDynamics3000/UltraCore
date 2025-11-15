"""
Experience Replay Buffer

Stores and samples transitions for off-policy RL algorithms (DQN, DDPG, etc.)
"""

import numpy as np
from collections import deque
from typing import Tuple, List
import random


class ReplayBuffer:
    """
    Experience replay buffer for storing and sampling transitions.
    """
    
    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer.
        
        Args:
            capacity: Maximum number of transitions to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def push(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Add a transition to the buffer.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        """
        Sample a batch of transitions.
        
        Args:
            batch_size: Number of transitions to sample
        
        Returns:
            (states, actions, rewards, next_states, dones)
        """
        batch = random.sample(self.buffer, batch_size)
        
        states = np.array([t[0] for t in batch])
        actions = np.array([t[1] for t in batch])
        rewards = np.array([t[2] for t in batch])
        next_states = np.array([t[3] for t in batch])
        dones = np.array([t[4] for t in batch])
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self) -> int:
        """Return current size of buffer"""
        return len(self.buffer)
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()


class PrioritizedReplayBuffer(ReplayBuffer):
    """
    Prioritized experience replay buffer.
    
    Samples transitions with probability proportional to their TD error.
    """
    
    def __init__(self, capacity: int = 10000, alpha: float = 0.6):
        """
        Initialize prioritized replay buffer.
        
        Args:
            capacity: Maximum number of transitions
            alpha: Prioritization exponent (0 = uniform, 1 = full prioritization)
        """
        super().__init__(capacity)
        self.priorities = deque(maxlen=capacity)
        self.alpha = alpha
    
    def push(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        priority: float = None
    ):
        """Add transition with priority"""
        max_priority = max(self.priorities) if self.priorities else 1.0
        priority = priority if priority is not None else max_priority
        
        self.buffer.append((state, action, reward, next_state, done))
        self.priorities.append(priority)
    
    def sample(self, batch_size: int, beta: float = 0.4) -> Tuple[np.ndarray, ...]:
        """
        Sample batch with prioritization.
        
        Args:
            batch_size: Number of transitions
            beta: Importance sampling exponent (0 = no correction, 1 = full correction)
        
        Returns:
            (states, actions, rewards, next_states, dones, weights, indices)
        """
        # Calculate sampling probabilities
        priorities = np.array(self.priorities)
        probs = priorities ** self.alpha
        probs /= probs.sum()
        
        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        
        # Get transitions
        batch = [self.buffer[idx] for idx in indices]
        
        states = np.array([t[0] for t in batch])
        actions = np.array([t[1] for t in batch])
        rewards = np.array([t[2] for t in batch])
        next_states = np.array([t[3] for t in batch])
        dones = np.array([t[4] for t in batch])
        
        # Calculate importance sampling weights
        weights = (len(self.buffer) * probs[indices]) ** (-beta)
        weights /= weights.max()
        
        return states, actions, rewards, next_states, dones, weights, indices
    
    def update_priorities(self, indices: List[int], priorities: np.ndarray):
        """Update priorities for sampled transitions"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
