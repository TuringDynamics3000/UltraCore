"""Anya - AI Banking Assistant for Accounts (OpenAI)"""
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, date
import json

from openai import AsyncOpenAI

from ultracore.anya.agent import AnyaAgent
from ..services import AccountService


class AnyaAccountsAgent(AnyaAgent):
    """
    Anya's Accounts specialist powered by OpenAI.
    
    Natural language interface for:
    - "What's my account balance?"
    - "Show me my recent transactions"
    - "Why was I charged a fee?"
    - "How can I save more money?"
    - "What's the best account for me?"
    - "I want to open a savings account"
    
    Australian banking expertise:
    - BSB and account numbers
    - Interest rates and bonus conditions
    - Fee structures
    - Direct debits and regular payments
    - Financial wellness guidance
    """
    
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        account_service: AccountService = None,
        customer_id: str = None
    ):
        super().__init__(
            name="AnyaAccountsAgent",
            description="AI banking assistant for account management",
            capabilities=[
                "Balance inquiries",
                "Transaction history",
                "Account recommendations",
                "Savings advice",
                "Fee explanations",
                "Account opening",
                "Financial wellness"
            ]
        )
        
        self.openai = openai_client
        self.account_service = account_service
        self.customer_id = customer_id
    
    async def execute(
        self,
        natural_language_request: str
    ) -> Dict[str, Any]:
        """Process account-related request."""
        
        context = await self._build_context()
        prompt = self._build_prompt(natural_language_request, context)
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            parsed = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "success": True,
                "message": response.choices[0].message.content
            }
        
        return await self._execute_intent(parsed)
    
    def _get_system_prompt(self) -> str:
        """System prompt for Anya as banking assistant."""
        return """You are Anya, a friendly AI banking assistant specializing in account management.

Your role is to help customers:
1. Check balances and transactions
2. Understand fees and charges
3. Find the right account products
4. Save money and build wealth
5. Navigate Australian banking

Australian Banking Context:
- BSB codes (Bank State Branch) - XXX-XXX format
- Account numbers are 6-9 digits
- Savings accounts often have bonus interest conditions
- Many transactional accounts are fee-free
- NPP enables instant payments (24/7)
- Interest calculated daily, paid monthly

Respond in JSON format:
{
    "intent": "balance_inquiry|transaction_history|savings_advice|account_recommendation|fee_explanation",
    "parameters": {...},
    "confidence": 0.0-1.0,
    "emotional_tone": "helpful|encouraging|educational|supportive",
    "reasoning": "string"
}

Be friendly, clear, and empowering. Help customers make smart financial decisions.
"""
    
    def _build_prompt(self, request: str, context: Dict) -> str:
        """Build prompt with context."""
        return f"""Customer Request: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Accounts: {len(context.get('accounts', []))}
- Total Balance: ${context.get('total_balance', 0):,.2f}
- Savings Rate: {context.get('savings_rate', 0):.2f}%

Parse the request and provide helpful banking assistance.
"""
    
    async def _build_context(self) -> Dict:
        """Build customer context."""
        return {
            "accounts": [],
            "total_balance": 15000.00,
            "savings_rate": 4.5
        }
    
    async def _execute_intent(self, parsed: Dict) -> Dict:
        """Execute parsed intent."""
        intent = parsed.get("intent")
        
        if intent == "balance_inquiry":
            result = await self._handle_balance_inquiry(parsed)
        elif intent == "transaction_history":
            result = await self._handle_transaction_history(parsed)
        elif intent == "savings_advice":
            result = await self._handle_savings_advice(parsed)
        elif intent == "account_recommendation":
            result = await self._handle_account_recommendation(parsed)
        elif intent == "fee_explanation":
            result = await self._handle_fee_explanation(parsed)
        else:
            result = {"success": False, "error": f"Unknown intent: {intent}"}
        
        return result
    
    async def _handle_balance_inquiry(self, parsed: Dict) -> Dict:
        """Handle balance inquiry."""
        message = """**Your Account Balances** ??

**Transactional Account**
- BSB: 123-456
- Account: 12345678
- Balance: $3,245.67
- Available: $3,245.67

**High Interest Savings**
- BSB: 123-456
- Account: 87654321
- Balance: $12,500.00
- Available: $12,500.00
- Interest Rate: 4.5% p.a. ??

**Total Balance: $15,745.67**

Your savings are earning great interest! Keep it up! ??
"""
        
        return {
            "success": True,
            "action": "balance_inquiry",
            "message": message,
            "balances": {
                "transactional": 3245.67,
                "savings": 12500.00,
                "total": 15745.67
            }
        }
    
    async def _handle_savings_advice(self, parsed: Dict) -> Dict:
        """Handle savings advice request."""
        message = """**Smart Savings Tips for You** ??

Based on your accounts, here's how to maximize your savings:

**1. You're Doing Great!** ??
Your savings account ($12,500) is earning 4.5% p.a. - that's excellent!

**Bonus Interest Conditions:**
? Deposit $1,000+ per month
? Maximum 1 withdrawal per month
? Grow your balance

**Currently:** You're meeting all conditions! Keep it up to earn the full 4.5%

**2. Automate Your Savings** ??
Set up automatic transfers from your transactional account:
- $500 per month = $6,000+ saved per year
- Plus interest! (~$270 in year 1)

**3. Optimize Your Balance** ??
Your transactional account ($3,245) could work harder:
- Keep $500-1,000 for daily spending
- Move excess to high-interest savings
- Extra ~$100/year in interest!

**4. Build an Emergency Fund** ???
Aim for 3-6 months expenses in savings:
- Target: ~$15,000-30,000
- You're already at $12,500! Well done!

**Quick Action:**
Would you like me to set up automatic savings transfers of $500/month?
"""
        
        return {
            "success": True,
            "action": "savings_advice",
            "message": message,
            "recommendations": [
                "Maintain bonus conditions",
                "Automate savings",
                "Move excess funds to savings",
                "Build emergency fund"
            ]
        }
    
    async def _handle_account_recommendation(self, parsed: Dict) -> Dict:
        """Recommend accounts."""
        return {"success": True, "action": "account_recommendation"}
    
    async def _handle_transaction_history(self, parsed: Dict) -> Dict:
        """Show transaction history."""
        return {"success": True, "action": "transaction_history"}
    
    async def _handle_fee_explanation(self, parsed: Dict) -> Dict:
        """Explain fees."""
        return {"success": True, "action": "fee_explanation"}
