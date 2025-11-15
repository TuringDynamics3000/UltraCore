# UltraCore ESG Module

This directory contains the source code for the UltraCore ESG (Environmental, Social, and Governance) module. This module provides a comprehensive suite of tools for integrating ESG data into the UltraCore platform, enabling ESG-aware investment strategies and reporting.

## Key Features

*   **Event-Sourced ESG Data:** All ESG data is streamed in real-time through a set of dedicated Kafka topics, providing a complete and auditable history of all ESG-related information.
*   **ESG-Aware RL Agents:** The Epsilon Agent, a new reinforcement learning agent, is specifically designed to optimize portfolios for both financial returns and ESG outcomes.
*   **MCP Tools for ESG:** A new set of MCP tools exposes the ESG module's capabilities to Manus and other AI agents, enabling AI-powered ESG analysis and portfolio management.
*   **Real-Time Reporting:** The module provides real-time, on-demand, and interactive ESG analytics through a modern web interface.

## Directory Structure

*   `agents/`: Contains the Epsilon Agent and the ESG-aware portfolio environment.
*   `data/`: Contains the ESG data loader, which handles loading and caching of ESG data from the Data Mesh.
*   `events/`: Contains the ESG event schemas and the Kafka producer for publishing ESG events.
*   `mcp/`: Contains the MCP tools for ESG capabilities.
*   `reporting/`: Contains the code for the real-time ESG reporting dashboard.

## Getting Started

To get started with the ESG module, please refer to the main `README.md` file in the root of the repository.
