"""
UltraCore ESG Module Demo

This script demonstrates the key capabilities of the UltraCore ESG module,
showing how it surpasses competitors like Finastra through:

1. Real-time, event-sourced ESG data
2. Agentic AI with the Epsilon Agent
3. MCP tools for AI-powered analysis
4. ESG-aware portfolio optimization
"""

import sys
sys.path.insert(0, '/home/ubuntu/UltraCore/src')

from ultracore.esg import (
    EsgDataLoader,
    EsgMcpTools,
    EpsilonAgent,
    EsgPortfolioEnv,
    get_esg_producer,
    EsgDataNormalizedEvent,
    EsgProvider,
    EsgMetricType,
)
from datetime import datetime
import numpy as np


def demo_1_esg_data_streaming():
    """Demo 1: Real-time ESG data streaming with Kafka"""
    print("=" * 80)
    print("DEMO 1: Real-Time ESG Data Streaming (Kafka-First Architecture)")
    print("=" * 80)
    print()
    print("Unlike Finastra's batch-based approach, UltraCore streams ESG data in real-time.")
    print()
    
    # Get the ESG event producer
    producer = get_esg_producer()
    
    # Simulate receiving an ESG rating update
    event = EsgDataNormalizedEvent(
        isin="AU000000VAS3",
        timestamp=datetime.now(),
        provider=EsgProvider.MSCI,
        metric_type=EsgMetricType.RATING,
        metric_value=6.0,  # AA rating
        metric_unit="rating",
        metadata={"previous_rating": "A", "reason": "Improved carbon disclosure"}
    )
    
    producer.publish("esg-data-normalized", event, key="AU000000VAS3")
    
    print("✓ Published ESG rating update to Kafka")
    print(f"  ISIN: {event.isin}")
    print(f"  Provider: {event.provider}")
    print(f"  New Rating: AA (6.0)")
    print(f"  Reason: {event.metadata['reason']}")
    print()
    print("This event is now available to ALL consumers in real-time:")
    print("  - RL agents can react immediately")
    print("  - Compliance systems can check constraints")
    print("  - Reporting dashboards update instantly")
    print("  - Complete audit trail is preserved")
    print()


def demo_2_mcp_tools():
    """Demo 2: MCP Tools for AI-Powered ESG Analysis"""
    print("=" * 80)
    print("DEMO 2: MCP Tools - Exposing ESG as AI-Queryable Instruments")
    print("=" * 80)
    print()
    print("Finastra provides static reports. UltraCore provides TOOLS that AI agents can use.")
    print()
    
    # Initialize MCP tools
    esg_loader = EsgDataLoader()
    mcp_tools = EsgMcpTools(esg_loader)
    
    # Tool 1: Get ESG Profile
    print("Tool 1: get_esg_profile()")
    print("-" * 40)
    profile = mcp_tools.get_esg_profile("AU000000ETHI")
    print(f"  ISIN: {profile['isin']}")
    print(f"  Name: {profile['name']}")
    print(f"  MSCI Rating: {profile['msci_rating']}")
    print(f"  Carbon Intensity: {profile['carbon_intensity']} tCO2e/$M")
    print(f"  Board Diversity: {profile['board_diversity']}%")
    print()
    
    # Tool 2: Screen Portfolio
    print("Tool 2: screen_portfolio_esg()")
    print("-" * 40)
    portfolio = {
        "AU000000VAS3": 0.6,
        "AU000000VGS3": 0.4
    }
    criteria = {
        "min_esg_rating": "AA",
        "max_carbon_intensity": 150.0
    }
    
    result = mcp_tools.screen_portfolio_esg(portfolio, criteria)
    print(f"  Portfolio Compliant: {result['compliant']}")
    print(f"  Weighted ESG Rating: {result['portfolio_metrics']['weighted_esg_rating']}")
    print(f"  Weighted Carbon Intensity: {result['portfolio_metrics']['weighted_carbon_intensity']}")
    
    if result['violations']:
        print(f"\n  Violations Found: {len(result['violations'])}")
        for v in result['violations']:
            print(f"    - {v['type']}: {v['actual']} (threshold: {v['threshold']})")
    
    if result['recommendations']:
        print(f"\n  Recommendations:")
        for rec in result['recommendations']:
            print(f"    - {rec}")
    print()


def demo_3_epsilon_agent():
    """Demo 3: Epsilon Agent - ESG-Aware RL for Alpha Generation"""
    print("=" * 80)
    print("DEMO 3: Epsilon Agent - Agentic AI for ESG Alpha")
    print("=" * 80)
    print()
    print("This is where UltraCore creates an INSURMOUNTABLE advantage.")
    print("Finastra: Static rules and filters")
    print("UltraCore: Generative, goal-seeking RL agents")
    print()
    
    # Initialize Epsilon Agent
    state_dim = 50  # Financial features + ESG features
    action_dim = 10  # Number of assets
    esg_feature_dim = 30  # ESG features (3 per asset)
    
    agent = EpsilonAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        esg_feature_dim=esg_feature_dim,
        epsilon_start=0.0  # Deterministic for demo
    )
    
    # Create a mock state
    state = np.random.randn(state_dim)
    
    # Select action with ESG constraints
    esg_constraints = {
        "min_esg_rating": 0.6,  # Normalized (0-1)
        "max_carbon_intensity": 0.3  # Normalized (0-1)
    }
    
    action = agent.select_action(state, esg_constraints, deterministic=True)
    
    print("Epsilon Agent Action Selection:")
    print("-" * 40)
    print(f"  State Dimension: {state_dim} (financial + ESG features)")
    print(f"  Action Dimension: {action_dim} (portfolio weights)")
    print(f"  ESG Constraints Applied: {len(esg_constraints)}")
    print()
    print("  Selected Portfolio Weights:")
    for i, weight in enumerate(action[:5]):  # Show first 5
        print(f"    Asset {i+1}: {weight:.4f}")
    print(f"    ... (and {action_dim - 5} more)")
    print()
    
    # Explain the action
    explanation = agent.explain_action(state)
    print("Explainable AI - Why this action?")
    print("-" * 40)
    print(f"  Selected Action Index: {explanation['selected_action']}")
    print(f"  Top 3 Q-Values:")
    q_values = explanation['q_values']
    top_3_indices = np.argsort(q_values)[-3:][::-1]
    for idx in top_3_indices:
        print(f"    Action {idx}: Q-value = {q_values[idx]:.4f}")
    print()
    print("  ESG Scores for Selected Assets:")
    for i, score in enumerate(explanation['esg_scores'][:3]):
        print(f"    Asset {i+1}:")
        print(f"      ESG Rating: {score['esg_rating']:.2f}")
        print(f"      Carbon Intensity: {score['carbon_intensity']:.2f}")
        print(f"      Controversy Score: {score['controversy_score']:.2f}")
    print()


def demo_4_competitive_summary():
    """Demo 4: Competitive Summary"""
    print("=" * 80)
    print("COMPETITIVE SUMMARY: UltraCore vs. Finastra")
    print("=" * 80)
    print()
    
    comparison = [
        ("Architecture", "Database-centric SaaS", "Kafka-first Event Sourcing"),
        ("Data Model", "Siloed, proprietary", "Unified Data Mesh"),
        ("AI/ML", "Basic automation", "Generative RL Agents (Epsilon)"),
        ("Reporting", "Static, periodic", "Real-time, interactive"),
        ("Personalization", "Limited", "Hyper-personalized RL agents"),
        ("API", "REST only", "REST + MCP for AI agents"),
        ("Use Case", "Corporate loan pricing", "Holistic portfolio optimization"),
    ]
    
    print(f"{'Capability':<20} | {'Finastra':<25} | {'UltraCore':<35}")
    print("-" * 85)
    for capability, finastra, ultracore in comparison:
        print(f"{capability:<20} | {finastra:<25} | {ultracore:<35}")
    print()
    
    print("KEY DIFFERENTIATORS:")
    print()
    print("1. REAL-TIME ESG ALPHA")
    print("   UltraCore's RL agents can identify and exploit ESG-driven market")
    print("   inefficiencies in real-time, generating alpha that static systems miss.")
    print()
    print("2. COMPLETE AUDITABILITY")
    print("   Event sourcing provides a complete, immutable history of all ESG")
    print("   decisions, crucial for regulatory compliance and investor trust.")
    print()
    print("3. AGENTIC AI INTEGRATION")
    print("   MCP tools allow Manus and other AI agents to USE ESG capabilities,")
    print("   not just READ reports. This enables autonomous ESG management.")
    print()
    print("4. HYPER-PERSONALIZATION")
    print("   Each investor gets a unique Epsilon Agent trained for their specific")
    print("   risk tolerance and ESG preferences. Finastra offers one-size-fits-all.")
    print()


def main():
    """Run all demos"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " " * 20 + "ULTRACORE ESG MODULE DEMONSTRATION" + " " * 24 + "║")
    print("║" + " " * 78 + "║")
    print("║" + " " * 15 + "Surpassing Finastra with Agentic AI & Event Sourcing" + " " * 10 + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    demo_1_esg_data_streaming()
    input("Press Enter to continue to Demo 2...")
    print()
    
    demo_2_mcp_tools()
    input("Press Enter to continue to Demo 3...")
    print()
    
    demo_3_epsilon_agent()
    input("Press Enter to see competitive summary...")
    print()
    
    demo_4_competitive_summary()
    
    print()
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Train Epsilon Agent on historical ESG + financial data")
    print("  2. Integrate with MCP Server for Manus access")
    print("  3. Build interactive reporting dashboard")
    print("  4. Deploy to production with real Kafka infrastructure")
    print()


if __name__ == "__main__":
    main()
