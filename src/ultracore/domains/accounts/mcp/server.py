"""MCP Server for Accounts (OpenAI)"""
from typing import Dict, Any
from decimal import Decimal

from mcp.server import Server
from ultracore.mcp.base import BaseMCPServer
from ..services import AccountService
from ..agents import AnyaAccountsAgent


class AccountsMCPServer(BaseMCPServer):
    """MCP Server for account management."""
    
    def __init__(
        self,
        account_service: AccountService,
        anya_agent: AnyaAccountsAgent
    ):
        super().__init__(server_name="accounts")
        self.account_service = account_service
        self.anya = anya_agent
    
    def register_tools(self):
        """Register account tools."""
        
        @self.server.tool()
        async def get_balance(
            account_id: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """Get account balance."""
            balance = await self.account_service.ledger.get_balance(account_id)
            return {
                "account_id": account_id,
                "balance": float(balance),
                "currency": "AUD"
            }
        
        @self.server.tool()
        async def open_savings_account(
            customer_id: str,
            account_name: str,
            initial_deposit: float = 0.0
        ) -> Dict[str, Any]:
            """Open a new savings account."""
            account = await self.account_service.open_savings_account(
                customer_id=customer_id,
                account_name=account_name,
                base_rate=Decimal("2.5"),
                bonus_rate=Decimal("2.0")
            )
            
            return {
                "account_id": account.account_id,
                "bsb": account.bsb,
                "account_number": account.account_number,
                "interest_rate": float(account.total_interest_rate),
                "message": "Savings account opened successfully!"
            }
        
        @self.server.tool()
        async def ask_anya_about_accounts(
            customer_id: str,
            question: str
        ) -> Dict[str, Any]:
            """Ask Anya (AI assistant) about account-related questions."""
            self.anya.customer_id = customer_id
            response = await self.anya.execute(question)
            return response
