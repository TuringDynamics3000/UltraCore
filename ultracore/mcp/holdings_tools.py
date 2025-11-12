"""
MCP Tools for Holdings Management
Enables AI assistants to interact with holdings system
"""

from typing import Dict, Any, List, Optional
from ultracore.modules.holdings.holdings_service import holdings_service
from ultracore.modules.holdings.position_tracker import position_tracker
from ultracore.modules.holdings.performance_analytics import performance_analytics
from ultracore.modules.holdings.rebalancing_engine import rebalancing_engine
from ultracore.agents.holdings_agent import holdings_agent

class HoldingsMCPTools:
    """
    MCP tools for AI assistants to manage holdings
    """
    
    @staticmethod
    def get_available_tools() -> List[Dict[str, Any]]:
        """List all available MCP tools"""
        return [
            {
                "name": "open_position",
                "description": "Open a new position in a portfolio",
                "parameters": {
                    "client_id": "Client ID",
                    "ticker": "Security ticker (e.g., VAS.AX)",
                    "quantity": "Number of shares",
                    "purchase_price": "Purchase price per share"
                }
            },
            {
                "name": "close_position",
                "description": "Close an existing position",
                "parameters": {
                    "position_id": "Position ID",
                    "sale_price": "Sale price per share"
                }
            },
            {
                "name": "get_portfolio_value",
                "description": "Get real-time portfolio valuation",
                "parameters": {
                    "client_id": "Client ID",
                    "real_time": "Use real-time pricing (true/false)"
                }
            },
            {
                "name": "get_position_details",
                "description": "Get detailed information about a position",
                "parameters": {
                    "position_id": "Position ID",
                    "include_lineage": "Include data lineage (true/false)"
                }
            },
            {
                "name": "monitor_portfolio",
                "description": "Run AI monitoring on portfolio",
                "parameters": {
                    "client_id": "Client ID"
                }
            },
            {
                "name": "analyze_performance",
                "description": "Calculate portfolio performance metrics",
                "parameters": {
                    "client_id": "Client ID"
                }
            },
            {
                "name": "get_rebalancing_recommendations",
                "description": "Get AI-powered rebalancing recommendations",
                "parameters": {
                    "client_id": "Client ID",
                    "target_allocation": "Target allocation dictionary"
                }
            },
            {
                "name": "identify_tax_loss_harvesting",
                "description": "Find tax loss harvesting opportunities",
                "parameters": {
                    "client_id": "Client ID",
                    "ticker": "Ticker to analyze"
                }
            },
            {
                "name": "calculate_cost_basis",
                "description": "Calculate cost basis for a position",
                "parameters": {
                    "ticker": "Security ticker",
                    "method": "Cost basis method (FIFO/LIFO/HIFO/etc)"
                }
            },
            {
                "name": "simulate_rebalancing",
                "description": "Simulate portfolio rebalancing",
                "parameters": {
                    "client_id": "Client ID",
                    "target_allocation": "Target allocation",
                    "dry_run": "Dry run mode (true/false)"
                }
            }
        ]
    
    @staticmethod
    async def open_position(
        client_id: str,
        ticker: str,
        quantity: float,
        purchase_price: float,
        purchase_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """MCP tool: Open position"""
        
        from datetime import datetime
        
        date = datetime.fromisoformat(purchase_date) if purchase_date else None
        
        result = await holdings_service.open_position(
            client_id=client_id,
            ticker=ticker,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=date
        )
        
        return {
            "success": True,
            "position_id": result["position_id"],
            "position": result["position"],
            "data_quality": result["mesh_quality"]
        }
    
    @staticmethod
    async def close_position(
        position_id: str,
        sale_price: float,
        sale_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """MCP tool: Close position"""
        
        from datetime import datetime
        
        date = datetime.fromisoformat(sale_date) if sale_date else None
        
        result = await holdings_service.close_position(
            position_id=position_id,
            sale_price=sale_price,
            sale_date=date
        )
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        return {
            "success": True,
            "position_id": position_id,
            "realized_gl": result["realized_gl"],
            "realized_gl_pct": result["realized_gl_pct"]
        }
    
    @staticmethod
    async def get_portfolio_value(
        client_id: str,
        real_time: bool = True
    ) -> Dict[str, Any]:
        """MCP tool: Get portfolio valuation"""
        
        valuation = await holdings_service.get_portfolio_value(
            client_id=client_id,
            real_time=real_time
        )
        
        return {
            "success": True,
            "client_id": client_id,
            "valuation": valuation
        }
    
    @staticmethod
    async def get_position_details(
        position_id: str,
        include_lineage: bool = False
    ) -> Dict[str, Any]:
        """MCP tool: Get position details"""
        
        position = await holdings_service.get_position(
            position_id=position_id,
            include_lineage=include_lineage
        )
        
        if not position:
            return {"success": False, "error": "Position not found"}
        
        return {
            "success": True,
            "position": position
        }
    
    @staticmethod
    async def monitor_portfolio(
        client_id: str
    ) -> Dict[str, Any]:
        """MCP tool: AI portfolio monitoring"""
        
        monitoring = await holdings_service.monitor_portfolio_with_ai(client_id)
        
        return {
            "success": True,
            "client_id": client_id,
            "monitoring": monitoring
        }
    
    @staticmethod
    async def analyze_performance(
        client_id: str
    ) -> Dict[str, Any]:
        """MCP tool: Performance analysis"""
        
        # Get portfolio history (would come from database in production)
        portfolio = await holdings_service.get_portfolio_value(client_id)
        
        # For demo, create sample history
        history = [
            {"date": "2024-01-01", "total_value": 100000},
            {"date": "2024-03-01", "total_value": 105000},
            {"date": "2024-06-01", "total_value": 110000},
            {"date": "2024-09-01", "total_value": 108000},
            {"date": "2024-12-01", "total_value": portfolio.get("total_value", 112000)}
        ]
        
        metrics = performance_analytics.calculate_comprehensive_metrics(history)
        
        return {
            "success": True,
            "client_id": client_id,
            "performance": metrics
        }
    
    @staticmethod
    async def get_rebalancing_recommendations(
        client_id: str,
        target_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """MCP tool: Get rebalancing recommendations"""
        
        recommendations = await holdings_service.get_rebalancing_recommendations(
            client_id=client_id,
            target_allocation=target_allocation
        )
        
        return {
            "success": True,
            "client_id": client_id,
            "recommendations": recommendations
        }
    
    @staticmethod
    async def identify_tax_loss_harvesting(
        client_id: str,
        ticker: str
    ) -> Dict[str, Any]:
        """MCP tool: Identify tax loss harvesting opportunities"""
        
        from ultracore.services.ultrawealth import ultrawealth_service
        
        # Get current price
        try:
            price_data = await ultrawealth_service.get_etf_price(ticker)
            current_price = price_data["price"]
        except:
            current_price = 0
        
        # Find opportunities
        opportunities = position_tracker.tax_loss_harvest_opportunities(
            ticker=ticker,
            current_price=current_price,
            min_loss=1000
        )
        
        return {
            "success": True,
            "client_id": client_id,
            "ticker": ticker,
            "opportunities": opportunities,
            "total_potential_loss": sum(o["potential_loss"] for o in opportunities),
            "total_tax_benefit": sum(o["tax_benefit"] for o in opportunities)
        }
    
    @staticmethod
    async def calculate_cost_basis(
        ticker: str,
        method: str = "fifo"
    ) -> Dict[str, Any]:
        """MCP tool: Calculate cost basis"""
        
        from ultracore.modules.holdings.position_tracker import CostBasisMethod
        
        position = position_tracker.get_position_summary(ticker)
        
        return {
            "success": True,
            "ticker": ticker,
            "method": method,
            "position": position
        }
    
    @staticmethod
    async def simulate_rebalancing(
        client_id: str,
        target_allocation: Dict[str, float],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """MCP tool: Simulate rebalancing"""
        
        # Get current portfolio
        portfolio = await holdings_service.get_portfolio_value(client_id)
        positions = portfolio.get("positions", [])
        total_value = portfolio.get("total_value", 0)
        
        # Generate rebalancing plan
        plan = await rebalancing_engine.generate_rebalancing_trades(
            current_positions=positions,
            target_allocation=target_allocation,
            total_value=total_value
        )
        
        # Execute if not dry run
        if not dry_run:
            result = await rebalancing_engine.execute_rebalancing(
                client_id=client_id,
                rebalancing_plan=plan,
                dry_run=False
            )
            
            return {
                "success": True,
                "client_id": client_id,
                "execution_result": result
            }
        
        return {
            "success": True,
            "client_id": client_id,
            "rebalancing_plan": plan,
            "note": "Dry run - no trades executed"
        }

# Global instance
holdings_mcp_tools = HoldingsMCPTools()
