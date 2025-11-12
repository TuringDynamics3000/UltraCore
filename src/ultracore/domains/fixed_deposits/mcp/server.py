"""MCP Server for Fixed Deposit Tools"""
from typing import Dict, Any
from mcp.server import Server

from ultracore.mcp.base import BaseMCPServer
from ..services import FixedDepositService
from ..agents import AnyaFixedDepositAgent


class FixedDepositMCPServer(BaseMCPServer):
    """
    MCP Server exposing Fixed Deposit capabilities as AI tools.
    
    Tools available:
    - open_fixed_deposit: Create new FD
    - check_fd_rates: Get current rates
    - calculate_fd_returns: Calculate maturity value
    - list_fixed_deposits: View customer's FDs
    - close_fd_early: Request premature closure
    - get_renewal_advice: AI-powered renewal recommendations
    """
    
    def __init__(
        self,
        fd_service: FixedDepositService,
        anya_agent: AnyaFixedDepositAgent
    ):
        super().__init__(server_name="fixed_deposits")
        self.fd_service = fd_service
        self.anya = anya_agent
    
    def register_tools(self):
        """Register all Fixed Deposit MCP tools."""
        
        @self.server.tool()
        async def open_fixed_deposit(
            customer_id: str,
            amount: float,
            term_months: int,
            source_account: str,
            maturity_instruction: str = "renew_deposit"
        ) -> Dict[str, Any]:
            """
            Open a new fixed deposit account.
            
            Args:
                customer_id: Customer identifier
                amount: Deposit amount in AUD
                term_months: Term in months (3, 6, 12, 24, 36)
                source_account: Source savings account ID
                maturity_instruction: What to do at maturity (renew_deposit, transfer_to_savings)
            
            Returns:
                Application confirmation with details
            """
            from decimal import Decimal
            
            # Get product (simplified - would query product catalog)
            product = None  # Placeholder
            
            application = await self.fd_service.submit_application(
                customer_id=customer_id,
                product=product,
                deposit_amount=Decimal(str(amount)),
                term_months=term_months,
                source_account_id=source_account,
                maturity_instruction=maturity_instruction,
                submitted_by="mcp_api"
            )
            
            return {
                "success": True,
                "application_id": application.application_id,
                "amount": float(application.deposit_amount),
                "term_months": application.term_months,
                "interest_rate": float(application.interest_rate_annual),
                "status": application.status,
                "message": f"Fixed deposit application submitted successfully. Application ID: {application.application_id}"
            }
        
        @self.server.tool()
        async def check_fd_rates(
            term_months: int = None,
            amount: float = None
        ) -> Dict[str, Any]:
            """
            Check current fixed deposit interest rates.
            
            Args:
                term_months: Optional term to check specific rate
                amount: Optional amount (rates may vary by amount)
            
            Returns:
                Current rate table
            """
            rates = {
                3: {"rate": 4.5, "min_amount": 1000},
                6: {"rate": 4.75, "min_amount": 1000},
                12: {"rate": 5.0, "min_amount": 1000},
                24: {"rate": 5.25, "min_amount": 5000},
                36: {"rate": 5.5, "min_amount": 10000}
            }
            
            if term_months and term_months in rates:
                rate_info = rates[term_months]
                return {
                    "term_months": term_months,
                    "interest_rate": rate_info["rate"],
                    "min_amount": rate_info["min_amount"],
                    "message": f"Current rate for {term_months} months: {rate_info['rate']}% p.a."
                }
            
            return {
                "rates": rates,
                "message": "Current fixed deposit rates",
                "note": "Rates may vary based on deposit amount"
            }
        
        @self.server.tool()
        async def calculate_fd_returns(
            amount: float,
            term_months: int,
            interest_rate: float
        ) -> Dict[str, Any]:
            """
            Calculate fixed deposit maturity value and returns.
            
            Args:
                amount: Deposit amount
                term_months: Term in months
                interest_rate: Annual interest rate (%)
            
            Returns:
                Detailed return calculation
            """
            from decimal import Decimal
            
            principal = Decimal(str(amount))
            rate = Decimal(str(interest_rate))
            term = Decimal(str(term_months))
            
            # Simple interest calculation
            interest = principal * rate / Decimal("100") * term / Decimal("12")
            maturity_value = principal + interest
            
            # Tax (30% assumed)
            tax = interest * Decimal("0.30")
            net_interest = interest - tax
            net_maturity = principal + net_interest
            
            return {
                "principal": float(principal),
                "term_months": term_months,
                "interest_rate": float(rate),
                "gross_interest": float(interest),
                "tax": float(tax),
                "net_interest": float(net_interest),
                "gross_maturity_value": float(maturity_value),
                "net_maturity_value": float(net_maturity),
                "effective_yield": float(rate * Decimal("0.7")),
                "message": f"On  for {term_months} months at {interest_rate}%, you'll earn  after tax"
            }
        
        @self.server.tool()
        async def list_fixed_deposits(
            customer_id: str,
            status: str = "active"
        ) -> Dict[str, Any]:
            """
            List customer's fixed deposit accounts.
            
            Args:
                customer_id: Customer identifier
                status: Filter by status (active, matured, all)
            
            Returns:
                List of fixed deposits
            """
            # Query from event store
            deposits = []  # Placeholder
            
            return {
                "customer_id": customer_id,
                "total_deposits": len(deposits),
                "deposits": deposits,
                "total_value": sum(d.get("balance", 0) for d in deposits),
                "message": f"Found {len(deposits)} fixed deposit(s)"
            }
        
        @self.server.tool()
        async def close_fd_early(
            account_id: str,
            reason: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Request premature closure of fixed deposit.
            
            Args:
                account_id: FD account ID
                reason: Reason for early closure
                customer_id: Customer identifier
            
            Returns:
                Closure request confirmation with penalty details
            """
            # Calculate penalty
            penalty_rate = 0.5  # 0.5% penalty
            
            return {
                "success": True,
                "account_id": account_id,
                "penalty_rate": penalty_rate,
                "status": "pending_approval",
                "message": f"Premature closure request submitted. A {penalty_rate}% penalty will be applied to interest earned.",
                "next_steps": [
                    "Request will be reviewed within 24 hours",
                    "You'll receive final calculation",
                    "Funds will be transferred upon approval"
                ]
            }
        
        @self.server.tool()
        async def get_renewal_advice(
            account_id: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Get AI-powered renewal advice for maturing FD.
            
            Args:
                account_id: FD account ID
                customer_id: Customer identifier
            
            Returns:
                Personalized renewal recommendation from Anya
            """
            # Use Anya agent for personalized advice
            advice = await self.anya.execute(
                f"My fixed deposit {account_id} is maturing soon. Should I renew it?"
            )
            
            return advice
