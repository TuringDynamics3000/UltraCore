"""
MCP (Model Context Protocol) Tools for Client Management
Enables AI assistants to interact with client management system
"""

from typing import Dict, Any, List
from ultracore.modules.clients.service import client_service
from ultracore.agents.client_agent import client_agent

class ClientManagementMCPTools:
    """
    MCP tools for AI assistants to manage clients
    """
    
    @staticmethod
    def get_available_tools() -> List[Dict[str, Any]]:
        """List all available MCP tools"""
        return [
            {
                "name": "create_client",
                "description": "Create a new client in the system",
                "parameters": {
                    "client_type": "Type of client (individual/company/trust/smsf)",
                    "email": "Client email address",
                    "first_name": "First name (for individuals)",
                    "last_name": "Last name (for individuals)",
                    "risk_profile": "Risk profile (conservative/moderate/aggressive)"
                }
            },
            {
                "name": "get_client_info",
                "description": "Retrieve client information",
                "parameters": {
                    "client_id": "Client ID"
                }
            },
            {
                "name": "assess_client_risk",
                "description": "AI-powered risk assessment for client",
                "parameters": {
                    "client_id": "Client ID"
                }
            },
            {
                "name": "recommend_portfolio",
                "description": "Get AI portfolio recommendations",
                "parameters": {
                    "client_id": "Client ID"
                }
            },
            {
                "name": "verify_kyc",
                "description": "Verify KYC documents with AI",
                "parameters": {
                    "client_id": "Client ID",
                    "documents": "List of documents to verify"
                }
            },
            {
                "name": "get_portfolio_value",
                "description": "Calculate total portfolio value",
                "parameters": {
                    "client_id": "Client ID"
                }
            }
        ]
    
    @staticmethod
    async def create_client(
        client_type: str,
        email: str,
        **kwargs
    ) -> Dict[str, Any]:
        """MCP tool: Create client"""
        client = await client_service.create_client(
            client_type=client_type,
            email=email,
            **kwargs
        )
        return {
            "success": True,
            "client_id": client.id,
            "client": client.dict()
        }
    
    @staticmethod
    async def get_client_info(client_id: str) -> Dict[str, Any]:
        """MCP tool: Get client info"""
        client = await client_service.get_client(client_id)
        if not client:
            return {"success": False, "error": "Client not found"}
        
        return {
            "success": True,
            "client": client.dict()
        }
    
    @staticmethod
    async def assess_client_risk(client_id: str) -> Dict[str, Any]:
        """MCP tool: Assess risk"""
        client = await client_service.get_client(client_id)
        if not client:
            return {"success": False, "error": "Client not found"}
        
        assessment = await client_agent.assess_client_risk(client.dict())
        
        return {
            "success": True,
            "client_id": client_id,
            "assessment": assessment
        }
    
    @staticmethod
    async def recommend_portfolio(client_id: str) -> Dict[str, Any]:
        """MCP tool: Get portfolio recommendations"""
        client = await client_service.get_client(client_id)
        if not client:
            return {"success": False, "error": "Client not found"}
        
        recommendation = await client_agent.recommend_portfolio(
            client.dict(),
            client.risk_profile
        )
        
        return {
            "success": True,
            "client_id": client_id,
            "recommendation": recommendation
        }
    
    @staticmethod
    async def verify_kyc(
        client_id: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """MCP tool: Verify KYC"""
        result = await client_agent.verify_kyc_documents(
            client_id,
            documents
        )
        
        return {
            "success": True,
            "verification": result
        }
    
    @staticmethod
    async def get_portfolio_value(client_id: str) -> Dict[str, Any]:
        """MCP tool: Get portfolio value"""
        value = await client_service.calculate_portfolio_value(client_id)
        
        return {
            "success": True,
            "client_id": client_id,
            "total_value": value
        }

# Global instance
client_mcp_tools = ClientManagementMCPTools()
