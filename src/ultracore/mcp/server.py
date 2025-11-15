"""
UltraCore Financial Data MCP Server

Main MCP server implementation providing unified access to financial data.
"""

import sys
sys.path.append('/home/ubuntu/UltraCore/src')

from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ultracore.mcp.tools.etf_data_tools import ETFDataTools
from ultracore.mcp.tools.portfolio_tools import PortfolioTools
from ultracore.mcp.sources.yahoo_source import YahooFinanceSource


# Initialize server
app = Server("ultracore-financial-data")

# Initialize tools
yahoo_source = YahooFinanceSource({'data_dir': 'data/etf/historical'})
etf_tools = ETFDataTools([yahoo_source])
portfolio_tools = PortfolioTools("data/etf")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools"""
    return [
        # ETF Data Tools
        Tool(
            name="get_etf_data",
            description="Get historical OHLCV data for an ETF",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "ETF ticker symbol"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "period": {"type": "string", "description": "Period (e.g., '1y', '5y', 'max')"},
                    "source": {"type": "string", "description": "Data source (optional)"}
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_multiple_etfs",
            description="Get data for multiple ETFs at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array", "items": {"type": "string"}, "description": "List of ETF tickers"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "period": {"type": "string"},
                    "source": {"type": "string"}
                },
                "required": ["tickers"]
            }
        ),
        Tool(
            name="get_etf_info",
            description="Get metadata about an ETF",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "ETF ticker symbol"},
                    "source": {"type": "string"}
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_latest_price",
            description="Get latest/current price for an ETF",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "ETF ticker symbol"},
                    "source": {"type": "string"}
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_market_snapshot",
            description="Get current prices for multiple ETFs",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array", "items": {"type": "string"}},
                    "source": {"type": "string"}
                },
                "required": ["tickers"]
            }
        ),
        Tool(
            name="list_available_etfs",
            description="List all available ETFs",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string"}
                }
            }
        ),
        
        # Portfolio Tools
        Tool(
            name="calculate_portfolio_metrics",
            description="Calculate risk/return metrics for a portfolio",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array", "items": {"type": "string"}},
                    "weights": {"type": "array", "items": {"type": "number"}},
                    "lookback_years": {"type": "integer", "default": 5}
                },
                "required": ["tickers", "weights"]
            }
        ),
        Tool(
            name="optimize_portfolio",
            description="Optimize portfolio allocation using UltraOptimiser",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array", "items": {"type": "string"}},
                    "objective": {"type": "string", "enum": ["sharpe", "volatility", "return"]},
                    "risk_budget": {"type": "number"},
                    "lookback_years": {"type": "integer", "default": 5}
                },
                "required": ["tickers"]
            }
        ),
        Tool(
            name="calculate_efficient_frontier",
            description="Calculate efficient frontier for a set of ETFs",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array", "items": {"type": "string"}},
                    "n_portfolios": {"type": "integer", "default": 100},
                    "lookback_years": {"type": "integer", "default": 5}
                },
                "required": ["tickers"]
            }
        ),
        Tool(
            name="rebalance_portfolio",
            description="Calculate rebalancing trades for a portfolio",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_holdings": {"type": "object"},
                    "target_weights": {"type": "object"},
                    "total_value": {"type": "number"}
                },
                "required": ["current_holdings", "target_weights", "total_value"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute MCP tool"""
    
    # ETF Data Tools
    if name == "get_etf_data":
        result = etf_tools.get_etf_data(**arguments)
    elif name == "get_multiple_etfs":
        result = etf_tools.get_multiple_etfs(**arguments)
    elif name == "get_etf_info":
        result = etf_tools.get_etf_info(**arguments)
    elif name == "get_latest_price":
        result = etf_tools.get_latest_price(**arguments)
    elif name == "get_market_snapshot":
        result = etf_tools.get_market_snapshot(**arguments)
    elif name == "list_available_etfs":
        result = etf_tools.list_available_etfs(**arguments)
    
    # Portfolio Tools
    elif name == "calculate_portfolio_metrics":
        result = portfolio_tools.calculate_portfolio_metrics(**arguments)
    elif name == "optimize_portfolio":
        result = portfolio_tools.optimize_portfolio(**arguments)
    elif name == "calculate_efficient_frontier":
        result = portfolio_tools.calculate_efficient_frontier(**arguments)
    elif name == "rebalance_portfolio":
        result = portfolio_tools.rebalance_portfolio(**arguments)
    
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=str(result))]


async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
