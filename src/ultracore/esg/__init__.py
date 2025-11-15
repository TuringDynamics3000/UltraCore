"""
UltraCore ESG Module

This module provides ESG (Environmental, Social, and Governance) capabilities
for the UltraCore platform, including:

- Event-sourced ESG data management
- ESG-aware Reinforcement Learning agents (Epsilon Agent)
- MCP tools for AI-powered ESG analysis
- Real-time ESG reporting and analytics

The ESG module leverages UltraCore's unique architecture:
- Kafka-first event sourcing for real-time ESG data streams
- Data Mesh for unified financial + ESG data products
- Agentic AI with RL for ESG alpha generation
- MCP Server for exposing ESG capabilities to AI agents
"""

from ultracore.esg.agents.epsilon_agent import EpsilonAgent, EsgAwareQNetwork
from ultracore.esg.agents.esg_portfolio_env import EsgPortfolioEnv
from ultracore.esg.data.esg_data_loader import EsgDataLoader
from ultracore.esg.mcp.esg_tools import EsgMcpTools, register_esg_tools
from ultracore.esg.events.schemas import (
    EsgDataRawEvent,
    EsgDataNormalizedEvent,
    EsgPortfolioEvent,
    EsgCorporateActionEvent,
    EsgRegulatoryUpdateEvent,
    EsgPreference,
    EsgProvider,
    EsgMetricType,
    PortfolioEventType,
    CorporateActionType,
)
from ultracore.esg.events.producer import EsgEventProducer, get_esg_producer

__version__ = "0.1.0"

__all__ = [
    # Agents
    "EpsilonAgent",
    "EsgAwareQNetwork",
    "EsgPortfolioEnv",
    
    # Data
    "EsgDataLoader",
    
    # MCP Tools
    "EsgMcpTools",
    "register_esg_tools",
    
    # Events
    "EsgDataRawEvent",
    "EsgDataNormalizedEvent",
    "EsgPortfolioEvent",
    "EsgCorporateActionEvent",
    "EsgRegulatoryUpdateEvent",
    "EsgPreference",
    "EsgProvider",
    "EsgMetricType",
    "PortfolioEventType",
    "CorporateActionType",
    "EsgEventProducer",
    "get_esg_producer",
]
