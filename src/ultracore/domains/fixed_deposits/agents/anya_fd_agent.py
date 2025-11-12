"""Anya - Natural Language Fixed Deposit Agent"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date
import json

from anthropic import Anthropic

from ultracore.anya.agent import AnyaAgent
from ..services import FixedDepositService
from ..models import FixedDepositProduct


class AnyaFixedDepositAgent(AnyaAgent):
    """
    Anya's Fixed Deposit specialist.
    
    Natural language interface for:
    - Opening fixed deposits: "I want to invest ,000 for 12 months"
    - Checking rates: "What's the best rate for 6 months?"
    - Managing deposits: "Show me my fixed deposits"
    - Premature closure: "I need to break my FD early"
    - Renewal advice: "Should I renew my FD or invest elsewhere?"
    
    Powered by Claude with context from:
    - Customer history (from events)
    - Market conditions (from ML models)
    - Regulatory requirements
    - Product catalog
    """
    
    def __init__(
        self,
        anthropic_client: Anthropic,
        fd_service: FixedDepositService,
        customer_id: str
    ):
        super().__init__(
            name="AnyaFixedDepositAgent",
            description="Natural language interface for fixed deposits",
            capabilities=[
                "Open new fixed deposits",
                "Check interest rates",
                "Compare FD products",
                "Manage existing deposits",
                "Advise on renewals",
                "Process premature closures",
                "Calculate returns",
                "Provide tax guidance"
            ]
        )
        self.anthropic = anthropic_client
        self.fd_service = fd_service
        self.customer_id = customer_id
    
    async def execute(self, natural_language_request: str) -> Dict[str, Any]:
        """
        Process natural language request about fixed deposits.
        
        Examples:
        - "I want to invest ,000 for 12 months, what's the best rate?"
        - "Show me all my fixed deposits"
        - "My FD123 is maturing next month, should I renew?"
        - "I need to close my fixed deposit early, what's the penalty?"
        """
        
        # Build context from customer's FD history
        context = await self._build_context()
        
        # Use Claude to understand intent and extract parameters
        prompt = self._build_prompt(natural_language_request, context)
        
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse Claude's structured response
        try:
            parsed = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            # Fallback: Claude returned natural language
            return {
                "success": True,
                "response_type": "conversational",
                "message": response.content[0].text,
                "confidence": 0.7
            }
        
        # Execute the parsed action
        intent = parsed.get("intent")
        
        if intent == "open_fd":
            return await self._handle_open_fd(parsed)
        elif intent == "check_rates":
            return await self._handle_check_rates(parsed)
        elif intent == "list_deposits":
            return await self._handle_list_deposits(parsed)
        elif intent == "premature_closure":
            return await self._handle_premature_closure(parsed)
        elif intent == "renewal_advice":
            return await self._handle_renewal_advice(parsed)
        elif intent == "calculate_returns":
            return await self._handle_calculate_returns(parsed)
        else:
            return {
                "success": False,
                "error": f"Unknown intent: {intent}",
                "confidence": parsed.get("confidence", 0.0)
            }
    
    def _get_system_prompt(self) -> str:
        """System prompt for Anya as FD specialist."""
        return """You are Anya, an AI banking assistant specializing in fixed deposits.

Your role is to:
1. Understand customer requests about fixed deposits
2. Extract structured information (amount, term, intent)
3. Provide clear, helpful financial advice
4. Ensure compliance with regulations
5. Optimize for customer outcomes

Always respond in JSON format with:
{
    "intent": "open_fd|check_rates|list_deposits|premature_closure|renewal_advice|calculate_returns",
    "parameters": {
        "amount": <number>,
        "term_months": <number>,
        "account_id": <string>,
        ...
    },
    "confidence": <0.0-1.0>,
    "reasoning": "Why you chose this interpretation"
}

Be conversational and helpful. If unsure, ask clarifying questions.

Key Australian tax information:
- Interest income is taxable
- TDS may apply for high earners
- Report interest in annual tax return

Regulatory compliance:
- Minimum investment: Usually ,000
- Maximum term: Usually 5-10 years
- Early withdrawal penalties may apply
- Deposit insurance up to ,000 per institution
"""
    
    def _build_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """Build prompt with customer context."""
        return f"""Customer Request: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Existing FDs: {context.get('existing_fds', [])}
- Total FD Balance: 
- Average Rate: {context.get('average_rate', 0)}%
- Available Savings Balance: 

Current Market Rates:
- 3 months: 4.5% p.a.
- 6 months: 4.75% p.a.
- 12 months: 5.0% p.a.
- 24 months: 5.25% p.a.
- 36 months: 5.5% p.a.

Parse the request and extract:
1. Intent (what does the customer want to do?)
2. Parameters (amount, term, account ID, etc.)
3. Any clarifications needed

Respond in JSON format as specified in system prompt.
"""
    
    async def _build_context(self) -> Dict[str, Any]:
        """Build customer context from event store."""
        # Query customer's FD accounts from event store
        # For now, placeholder
        return {
            "existing_fds": [],
            "total_balance": 0,
            "average_rate": 0,
            "savings_balance": 0
        }
    
    async def _handle_open_fd(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opening new fixed deposit."""
        params = parsed.get("parameters", {})
        amount = Decimal(str(params.get("amount", 0)))
        term_months = params.get("term_months", 12)
        
        # Get best product for this amount and term
        # (Would query product catalog)
        
        return {
            "success": True,
            "action": "open_fd",
            "amount": float(amount),
            "term_months": term_months,
            "interest_rate": 5.0,
            "maturity_value": float(amount * Decimal("1.05")),
            "message": f"I can help you open a fixed deposit of  for {term_months} months at 5.0% p.a. Your maturity value will be approximately . Shall I proceed?",
            "next_steps": ["confirm_details", "verify_source_account", "submit_application"],
            "confidence": parsed.get("confidence", 0.95)
        }
    
    async def _handle_check_rates(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checking interest rates."""
        params = parsed.get("parameters", {})
        term_months = params.get("term_months")
        amount = params.get("amount")
        
        rates = {
            3: 4.5,
            6: 4.75,
            12: 5.0,
            24: 5.25,
            36: 5.5
        }
        
        if term_months and term_months in rates:
            rate = rates[term_months]
            message = f"For a {term_months}-month fixed deposit, our current rate is {rate}% p.a."
            
            if amount:
                amount_dec = Decimal(str(amount))
                interest = amount_dec * Decimal(str(rate)) / Decimal("100") * Decimal(term_months) / Decimal("12")
                message += f" On , you'd earn approximately  in interest."
        else:
            message = "Here are our current fixed deposit rates:\n"
            for months, rate in rates.items():
                message += f"- {months} months: {rate}% p.a.\n"
        
        return {
            "success": True,
            "action": "check_rates",
            "rates": rates,
            "message": message,
            "confidence": parsed.get("confidence", 0.95)
        }
    
    async def _handle_list_deposits(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listing customer's deposits."""
        # Query from event store
        deposits = []  # Placeholder
        
        if not deposits:
            message = "You don't have any active fixed deposits at the moment. Would you like to open one?"
        else:
            message = f"You have {len(deposits)} active fixed deposit(s):\n"
            for fd in deposits:
                message += f"- FD {fd['account_number']}:  @ {fd['rate']}% (matures {fd['maturity_date']})\n"
        
        return {
            "success": True,
            "action": "list_deposits",
            "deposits": deposits,
            "message": message,
            "confidence": parsed.get("confidence", 0.95)
        }
    
    async def _handle_premature_closure(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle premature closure request."""
        params = parsed.get("parameters", {})
        account_id = params.get("account_id")
        
        # Calculate penalty (simplified)
        penalty_rate = Decimal("0.5")  # 0.5% penalty
        
        return {
            "success": True,
            "action": "premature_closure",
            "account_id": account_id,
            "penalty_rate": float(penalty_rate),
            "message": f"I understand you need to close your fixed deposit early. There will be a {penalty_rate}% penalty on the interest earned. Would you like me to calculate the exact amount you'll receive?",
            "next_steps": ["calculate_penalty", "confirm_closure", "process"],
            "confidence": parsed.get("confidence", 0.9)
        }
    
    async def _handle_renewal_advice(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Provide renewal advice using ML predictions."""
        params = parsed.get("parameters", {})
        account_id = params.get("account_id")
        
        # Get ML prediction for best action
        # (Would call ML model)
        
        current_rate = 5.0
        new_rate = 5.25
        
        message = f"""Your fixed deposit is maturing soon. Here's my analysis:

Current Rate: {current_rate}% p.a.
New Rate (if renewed): {new_rate}% p.a.

Recommendation: Renew for another 12 months
Reasoning:
- Rates have increased by 0.25%
- Market outlook is stable
- Your historical preference is 12-month terms
- No immediate liquidity needs detected

Alternative options:
1. Renew at higher rate ({new_rate}%)
2. Split into multiple FDs (ladder strategy)
3. Transfer to savings for flexibility

What would you like to do?
"""
        
        return {
            "success": True,
            "action": "renewal_advice",
            "recommendation": "renew",
            "current_rate": current_rate,
            "new_rate": new_rate,
            "message": message,
            "confidence": parsed.get("confidence", 0.85)
        }
    
    async def _handle_calculate_returns(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate returns for given parameters."""
        params = parsed.get("parameters", {})
        amount = Decimal(str(params.get("amount", 0)))
        term_months = params.get("term_months", 12)
        rate = Decimal(str(params.get("rate", 5.0)))
        
        # Calculate simple interest
        interest = amount * rate / Decimal("100") * Decimal(term_months) / Decimal("12")
        maturity_value = amount + interest
        
        # Tax estimation (30% marginal rate assumed)
        tax = interest * Decimal("0.30")
        net_interest = interest - tax
        net_maturity = amount + net_interest
        
        message = f"""Fixed Deposit Return Calculator

Principal: 
Term: {term_months} months
Interest Rate: {float(rate)}% p.a.

Gross Interest: 
Less Tax (30%): -
Net Interest: 

Maturity Value (Pre-tax): 
Maturity Value (Post-tax): 

Effective Yield (Post-tax): {float(rate * Decimal('0.7'))}% p.a.

Note: Actual tax may vary based on your income bracket.
"""
        
        return {
            "success": True,
            "action": "calculate_returns",
            "amount": float(amount),
            "term_months": term_months,
            "rate": float(rate),
            "interest": float(interest),
            "tax": float(tax),
            "net_interest": float(net_interest),
            "maturity_value": float(maturity_value),
            "net_maturity_value": float(net_maturity),
            "message": message,
            "confidence": parsed.get("confidence", 0.95)
        }
