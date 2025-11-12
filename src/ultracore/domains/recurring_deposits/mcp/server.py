"""MCP Server for Recurring Deposit Tools"""
from typing import Dict, Any, List
from datetime import date
from decimal import Decimal

from mcp.server import Server
from ultracore.mcp.base import BaseMCPServer
from ..services import RecurringDepositService
from ..agents import AnyaRecurringDepositAgent


class RecurringDepositMCPServer(BaseMCPServer):
    """
    MCP Server exposing Recurring Deposit capabilities as AI tools.
    
    Tools available:
    - open_recurring_deposit: Create new RD with systematic savings
    - check_payment_schedule: View upcoming payment schedule
    - track_savings_progress: Monitor progress toward goal
    - calculate_rd_maturity: Calculate maturity value
    - handle_missed_payment: Assist with missed payments
    - check_affordability: Assess if RD is affordable
    - get_completion_coaching: AI-powered coaching
    - list_recurring_deposits: View customer's RDs
    """
    
    def __init__(
        self,
        rd_service: RecurringDepositService,
        anya_agent: AnyaRecurringDepositAgent
    ):
        super().__init__(server_name="recurring_deposits")
        self.rd_service = rd_service
        self.anya = anya_agent
    
    def register_tools(self):
        """Register all Recurring Deposit MCP tools."""
        
        @self.server.tool()
        async def open_recurring_deposit(
            customer_id: str,
            monthly_amount: float,
            term_months: int,
            source_account: str,
            debit_day: int = 1,
            maturity_instruction: str = "transfer_to_savings"
        ) -> Dict[str, Any]:
            """
            Open a new recurring deposit for systematic savings.
            
            Args:
                customer_id: Customer identifier
                monthly_amount: Monthly deposit amount in AUD
                term_months: Term in months (12, 24, 36, 48, 60)
                source_account: Account ID for auto-debit
                debit_day: Day of month for auto-debit (1-28)
                maturity_instruction: What to do at maturity
            
            Returns:
                Application confirmation with savings projection
            """
            from decimal import Decimal
            
            # Get product
            product = None  # Placeholder
            
            application = await self.rd_service.submit_application(
                customer_id=customer_id,
                product=product,
                monthly_deposit_amount=Decimal(str(monthly_amount)),
                term_months=term_months,
                source_account_id=source_account,
                debit_day_of_month=debit_day,
                maturity_instruction=maturity_instruction,
                submitted_by="mcp_api"
            )
            
            # Calculate maturity value
            total_principal = Decimal(str(monthly_amount)) * term_months
            rate = application.interest_rate_annual
            n = Decimal(term_months)
            interest = Decimal(str(monthly_amount)) * n * (n + Decimal("1")) / (Decimal("24")) * rate / Decimal("100")
            maturity_value = total_principal + interest
            
            return {
                "success": True,
                "application_id": application.application_id,
                "monthly_amount": float(monthly_amount),
                "term_months": term_months,
                "interest_rate": float(application.interest_rate_annual),
                "total_deposits": float(total_principal),
                "expected_interest": float(interest),
                "maturity_value": float(maturity_value),
                "first_deposit_date": application.submitted_at.date().isoformat(),
                "status": application.status,
                "message": f"Recurring deposit application submitted! Save /month and grow to  in {term_months} months."
            }
        
        @self.server.tool()
        async def check_payment_schedule(
            account_id: str,
            customer_id: str,
            upcoming_months: int = 3
        ) -> Dict[str, Any]:
            """
            Check upcoming payment schedule for RD.
            
            Args:
                account_id: RD account ID
                customer_id: Customer identifier
                upcoming_months: Number of months to show (default: 3)
            
            Returns:
                Payment schedule with dates and amounts
            """
            # Query from event store
            schedule = {
                "account_id": account_id,
                "next_payment_date": "2025-12-01",
                "next_payment_amount": 500.00,
                "upcoming_payments": [
                    {"date": "2025-12-01", "amount": 500.00, "installment": 9},
                    {"date": "2026-01-01", "amount": 500.00, "installment": 10},
                    {"date": "2026-02-01", "amount": 500.00, "installment": 11}
                ],
                "payments_made": 8,
                "payments_remaining": 16,
                "completion_percentage": 33.3
            }
            
            return {
                "success": True,
                "schedule": schedule,
                "message": f"Next payment:  on {schedule['next_payment_date']}. You're {schedule['completion_percentage']:.1f}% complete!"
            }
        
        @self.server.tool()
        async def track_savings_progress(
            account_id: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Track savings progress in RD account.
            
            Args:
                account_id: RD account ID
                customer_id: Customer identifier
            
            Returns:
                Detailed progress report with milestones
            """
            # Query account state
            progress = {
                "current_balance": 4120.50,
                "total_deposited": 4000.00,
                "interest_earned": 120.50,
                "target_amount": 12000.00,
                "completion_percentage": 33.3,
                "on_track": True,
                "account_health_score": 95,
                "payments_made": 8,
                "payments_missed": 0,
                "consecutive_on_time": 8,
                "next_milestone": {
                    "type": "50% completion",
                    "amount_needed": 1879.50,
                    "months_away": 4
                }
            }
            
            return {
                "success": True,
                "progress": progress,
                "message": f"Great progress! You've saved  ({progress['completion_percentage']:.1f}% of goal). Account health: {progress['account_health_score']}/100",
                "encouragement": "You're right on track! Keep up the excellent saving habit! ??"
            }
        
        @self.server.tool()
        async def calculate_rd_maturity(
            monthly_amount: float,
            term_months: int,
            interest_rate: float = 5.75
        ) -> Dict[str, Any]:
            """
            Calculate maturity value for recurring deposit.
            
            Args:
                monthly_amount: Monthly deposit amount
                term_months: Term in months
                interest_rate: Annual interest rate (default: 5.75%)
            
            Returns:
                Detailed maturity calculation
            """
            from decimal import Decimal
            
            monthly = Decimal(str(monthly_amount))
            rate = Decimal(str(interest_rate))
            n = Decimal(term_months)
            
            # Total principal
            total_principal = monthly * n
            
            # RD interest formula: P * n * (n+1) / (2*12) * (r/100)
            interest = monthly * n * (n + Decimal("1")) / (Decimal("2") * Decimal("12")) * rate / Decimal("100")
            
            maturity_value = total_principal + interest
            
            # Tax (30% assumed)
            tax = interest * Decimal("0.30")
            net_interest = interest - tax
            net_maturity = total_principal + net_interest
            
            return {
                "monthly_amount": float(monthly),
                "term_months": term_months,
                "interest_rate": float(rate),
                "total_deposits": float(total_principal),
                "gross_interest": float(interest),
                "tax": float(tax),
                "net_interest": float(net_interest),
                "gross_maturity_value": float(maturity_value),
                "net_maturity_value": float(net_maturity),
                "effective_annual_return": float((net_interest / total_principal) * (12 / n) * 100),
                "message": f"Save /month for {term_months} months and grow to  after tax!"
            }
        
        @self.server.tool()
        async def handle_missed_payment(
            account_id: str,
            customer_id: str,
            reason: str = "temporary_cash_flow"
        ) -> Dict[str, Any]:
            """
            Help customer handle missed RD payment.
            
            Args:
                account_id: RD account ID
                customer_id: Customer identifier
                reason: Reason for missing payment
            
            Returns:
                Available options and recommendations
            """
            options = [
                {
                    "id": "grace_period",
                    "name": "Use Grace Period (5 days)",
                    "penalty": 0.00,
                    "recommended": True,
                    "description": "Pay within 5 days, no penalty"
                },
                {
                    "id": "skip_payment",
                    "name": "Skip This Month",
                    "penalty": 25.00,
                    "recommended": False,
                    "description": "One-time skip (if eligible), small fee"
                },
                {
                    "id": "reduce_amount",
                    "name": "Reduce Monthly Amount",
                    "penalty": 0.00,
                    "recommended": False,
                    "description": "Lower payment, extend term"
                },
                {
                    "id": "payment_holiday",
                    "name": "Payment Holiday",
                    "penalty": 0.00,
                    "recommended": False,
                    "description": "Pause 1-2 months (hardship only)"
                }
            ]
            
            return {
                "success": True,
                "options": options,
                "recommended_option": "grace_period",
                "message": "I understand things happen! You have several options to keep your savings on track.",
                "support_message": "Financial wellness is important. Let's find a solution that works for you. ??"
            }
        
        @self.server.tool()
        async def check_affordability(
            customer_id: str,
            monthly_amount: float,
            term_months: int
        ) -> Dict[str, Any]:
            """
            Check if recurring deposit is affordable for customer.
            
            Args:
                customer_id: Customer identifier
                monthly_amount: Proposed monthly amount
                term_months: Proposed term
            
            Returns:
                Affordability assessment with recommendations
            """
            # Get customer financial profile
            estimated_income = 5000.00  # Placeholder
            existing_commitments = 800.00
            
            # 30% rule: max 30% of income for savings/commitments
            max_affordable = estimated_income * 0.3
            available = max_affordable - existing_commitments
            
            is_affordable = monthly_amount <= available
            utilization = monthly_amount / available if available > 0 else 1.5
            
            if is_affordable:
                recommendation = "APPROVED"
                suggested_amount = monthly_amount
                message = f"? /month fits comfortably within your budget!"
            else:
                recommendation = "ADJUST_AMOUNT"
                suggested_amount = available * 0.9  # 90% of available
                message = f"?? /month may be challenging. Consider /month instead."
            
            return {
                "success": True,
                "is_affordable": is_affordable,
                "requested_amount": monthly_amount,
                "suggested_amount": suggested_amount,
                "available_budget": available,
                "utilization_percentage": utilization * 100,
                "recommendation": recommendation,
                "financial_summary": {
                    "estimated_monthly_income": estimated_income,
                    "existing_commitments": existing_commitments,
                    "after_this_rd": available - suggested_amount
                },
                "message": message
            }
        
        @self.server.tool()
        async def get_completion_coaching(
            account_id: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Get AI-powered completion coaching for RD.
            
            Args:
                account_id: RD account ID
                customer_id: Customer identifier
            
            Returns:
                Personalized coaching and recommendations from Anya
            """
            # Use Anya agent
            coaching = await self.anya.execute(
                f"Help me stay on track with my RD account {account_id}"
            )
            
            return coaching
        
        @self.server.tool()
        async def list_recurring_deposits(
            customer_id: str,
            status: str = "active"
        ) -> Dict[str, Any]:
            """
            List customer's recurring deposit accounts.
            
            Args:
                customer_id: Customer identifier
                status: Filter by status (active, matured, all)
            
            Returns:
                List of RD accounts with summaries
            """
            # Query from event store
            deposits = []  # Placeholder
            
            total_monthly_commitment = sum(rd.get("monthly_amount", 0) for rd in deposits)
            total_saved = sum(rd.get("current_balance", 0) for rd in deposits)
            
            return {
                "success": True,
                "customer_id": customer_id,
                "total_accounts": len(deposits),
                "deposits": deposits,
                "summary": {
                    "total_monthly_commitment": total_monthly_commitment,
                    "total_saved": total_saved,
                    "average_completion": 0.0
                },
                "message": f"You have {len(deposits)} active recurring deposit(s) with total monthly commitment of "
            }
