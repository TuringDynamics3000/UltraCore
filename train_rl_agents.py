"""
Train All RL Agents

Script to train all 4 RL agents on historical ETF data.
"""

import sys
sys.path.append('/home/ubuntu/UltraCore/src')

import pandas as pd
from pathlib import Path
from ultracore.rl.training.trainer import AgentTrainer


def load_etf_data(data_dir: str = 'data/etf/historical') -> dict:
    """
    Load all ETF data from parquet files.
    
    Args:
        data_dir: Directory containing ETF parquet files
    
    Returns:
        Dict of {ticker: DataFrame}
    """
    data_path = Path(data_dir)
    etf_data = {}
    
    print("Loading ETF data...")
    
    for file in data_path.glob('*.parquet'):
        ticker = file.stem
        df = pd.read_parquet(file)
        
        # Ensure required columns
        if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
            etf_data[ticker] = df
            print(f"  ✅ {ticker}: {len(df)} rows")
    
    print(f"\nLoaded {len(etf_data)} ETFs")
    
    return etf_data


def main():
    """Main training function"""
    
    print("=" * 80)
    print("RL AGENT TRAINING PIPELINE")
    print("=" * 80)
    
    # Load ETF data
    etf_data = load_etf_data()
    
    if len(etf_data) == 0:
        print("❌ No ETF data found!")
        return
    
    # Create trainer
    trainer = AgentTrainer(etf_data)
    
    # Train all agents (reduced episodes for demo - increase for production)
    n_episodes = 100  # Use 500-1000 for production
    
    print(f"\nTraining with {n_episodes} episodes per agent...")
    print("(This will take approximately 10-20 minutes)\n")
    
    agents = trainer.train_all_agents(n_episodes=n_episodes)
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print("\nTrained agents saved to: models/rl_agents/")
    print("  - alpha_agent.pkl (Q-Learning)")
    print("  - beta_agent.pkl (Policy Gradient)")
    print("  - gamma_agent.pkl (DQN)")
    print("  - delta_agent.pkl (A3C)")
    print("\nYou can now use these agents for portfolio optimization!")


if __name__ == '__main__':
    main()
