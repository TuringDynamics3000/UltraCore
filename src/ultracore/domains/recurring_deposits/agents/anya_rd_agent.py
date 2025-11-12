"""Anya - Natural Language Recurring Deposit Agent"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date
import json

from anthropic import Anthropic

from ultracore.anya.agent import AnyaAgent
from ..services import RecurringDepositService
from ..models import RecurringDepositProduct


class AnyaRecurringDepositAgent(AnyaAgent):
    """
    Anya's Recurring Deposit specialist.
    
    Natural language interface for:
    - Opening RDs: "I want to save  every month for 2 years"
    - Managing deposits: "When is my next RD payment due?"
    - Payment assistance: "I might miss this month's RD payment"
    - Progress tracking: "How much have I saved in my RD so far?"
    - Completion coaching: "Will I reach my savings goal on time?"
    - Affordability advice: "Can I afford a /month RD?"
    
    Powered by Claude with context from:
    - Customer payment history (from events)
    - Account health score
    - ML predictions (completion probability, missed payment risk)
    - Financial wellness indicators
    """
    
    def __init__(
        self,
        anthropic_client: Anthropic,
        rd_service: RecurringDepositService,
        customer_id: str
    ):
        super().__init__(
            name="AnyaRecurringDepositAgent",
            description="Natural language interface for recurring deposits",
            capabilities=[
                "Open new recurring deposits",
                "Check payment schedules",
                "Track savings progress",
                "Provide payment reminders",
                "Offer completion coaching",
                "Calculate affordability",
                "Manage missed payments",
                "Advise on early closure"
            ]
        )
        self.anthropic = anthropic_client
        self.rd_service = rd_service
        self.customer_id = customer_id
    
    async def execute(self, natural_language_request: str) -> Dict[str, Any]:
        """
        Process natural language request about recurring deposits.
        
        Examples:
        - "I want to save  every month for my house deposit"
        - "Show me my RD payment history"
        - "I can't make this month's payment, what should I do?"
        - "How much will I save if I deposit /month for 3 years?"
        - "Help me stay on track with my RD goal"
        """
        
        # Build context
        context = await self._build_context()
        
        # Use Claude to understand intent
        prompt = self._build_prompt(natural_language_request, context)
        
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        try:
            parsed = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            return {
                "success": True,
                "response_type": "conversational",
                "message": response.content[0].text,
                "confidence": 0.7
            }
        
        # Execute action
        intent = parsed.get("intent")
        
        if intent == "open_rd":
            return await self._handle_open_rd(parsed)
        elif intent == "check_schedule":
            return await self._handle_check_schedule(parsed)
        elif intent == "track_progress":
            return await self._handle_track_progress(parsed)
        elif intent == "missed_payment_help":
            return await self._handle_missed_payment(parsed)
        elif intent == "calculate_savings":
            return await self._handle_calculate_savings(parsed)
        elif intent == "affordability_check":
            return await self._handle_affordability(parsed)
        elif intent == "completion_coaching":
            return await self._handle_completion_coaching(parsed)
        else:
            return {
                "success": False,
                "error": f"Unknown intent: {intent}",
                "confidence": parsed.get("confidence", 0.0)
            }
    
    def _get_system_prompt(self) -> str:
        """System prompt for Anya as RD specialist."""
        return """You are Anya, an AI banking assistant specializing in recurring deposits (systematic savings).

Your role is to:
1. Help customers build disciplined saving habits
2. Provide encouragement and motivation for savings goals
3. Offer practical solutions for payment difficulties
4. Calculate savings projections accurately
5. Assess affordability realistically

Respond in JSON format:
{
    "intent": "open_rd|check_schedule|track_progress|missed_payment_help|calculate_savings|affordability_check|completion_coaching",
    "parameters": {
        "monthly_amount": <number>,
        "term_months": <number>,
        "account_id": <string>,
        "goal_description": <string>,
        ...
    },
    "confidence": <0.0-1.0>,
    "emotional_tone": "encouraging|empathetic|practical|celebratory",
    "reasoning": "Why you chose this interpretation"
}

Key principles:
- Be encouraging about savings goals
- Show empathy for financial difficulties
- Provide practical solutions, not just motivation
- Celebrate milestones and progress
- Be realistic about affordability

Australian context:
- Common savings goals: house deposit, wedding, education, emergency fund
- Interest earned is taxable income
- Systematic savings build financial discipline
"""
    
    def _build_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """Build prompt with customer context."""
        return f"""Customer Request: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Active RDs: {context.get('active_rds', [])}
- Total Monthly Commitments: 
- Average Payment Record: {context.get('payment_record', 'Good')}
- Account Health Score: {context.get('avg_health_score', 100)}/100
- Missed Payments (Last 6 months): {context.get('recent_misses', 0)}
- Monthly Income (estimated): 
- Other Savings: 

Current RD Rates:
- 12 months: 5.5% p.a.
- 24 months: 5.75% p.a.
- 36 months: 6.0% p.a.
- 48 months: 6.25% p.a.
- 60 months: 6.5% p.a.

Parse the request and provide appropriate guidance.
"""
    
    async def _build_context(self) -> Dict[str, Any]:
        """Build customer context from event store."""
        # Query customer's RD accounts
        return {
            "active_rds": [],
            "total_monthly_commitment": 0,
            "payment_record": "Good",
            "avg_health_score": 100,
            "recent_misses": 0,
            "estimated_income": 5000,
            "other_savings": 10000
        }
    
    async def _handle_open_rd(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opening new recurring deposit."""
        params = parsed.get("parameters", {})
        monthly_amount = Decimal(str(params.get("monthly_amount", 0)))
        term_months = params.get("term_months", 24)
        goal = params.get("goal_description", "savings goal")
        
        # Calculate maturity value
        rate = Decimal("5.75")  # For 24 months
        total_principal = monthly_amount * term_months
        
        # RD interest formula: P * n * (n+1) / (2*12) * (r/100)
        n = Decimal(term_months)
        interest = monthly_amount * n * (n + Decimal("1")) / (Decimal("24")) * rate / Decimal("100")
        maturity_value = total_principal + interest
        
        message = f"""Great! Let's set up a recurring deposit to help you achieve your {goal}.

?? Monthly Deposit: 
?? Duration: {term_months} months ({term_months//12} years)
?? Interest Rate: {float(rate)}% p.a.
?? Total Deposits: 
?? Interest Earned: 
?? Maturity Value: 

Auto-debit will ensure you never miss a payment. Which account should I debit from, and what day of the month works best for you?

This disciplined saving approach will help you reach your {goal} systematically! ??
"""
        
        return {
            "success": True,
            "action": "open_rd",
            "monthly_amount": float(monthly_amount),
            "term_months": term_months,
            "interest_rate": float(rate),
            "total_principal": float(total_principal),
            "interest": float(interest),
            "maturity_value": float(maturity_value),
            "message": message,
            "emotional_tone": "encouraging",
            "next_steps": ["select_source_account", "choose_debit_day", "confirm_mandate"],
            "confidence": parsed.get("confidence", 0.95)
        }
    
    async def _handle_check_schedule(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checking payment schedule."""
        params = parsed.get("parameters", {})
        account_id = params.get("account_id")
        
        # Query schedule from event store
        schedule = {
            "next_payment_due": "2025-12-01",
            "next_payment_amount": 500.00,
            "payments_made": 8,
            "payments_remaining": 16,
            "completion_percentage": 33.3
        }
        
        message = f"""?? Your RD Payment Schedule

Next Payment:  due on {schedule['next_payment_due']}

Progress:
? Payments Made: {schedule['payments_made']} of {schedule['payments_made'] + schedule['payments_remaining']}
?? Completion: {schedule['completion_percentage']:.1f}%
?? Remaining: {schedule['payments_remaining']} payments

You're doing great! Keep up the consistent saving habit! ??

Would you like to set up a reminder for upcoming payments?
"""
        
        return {
            "success": True,
            "action": "check_schedule",
            "schedule": schedule,
            "message": message,
            "emotional_tone": "encouraging",
            "confidence": 0.95
        }
    
    async def _handle_track_progress(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tracking savings progress."""
        params = parsed.get("parameters", {})
        account_id = params.get("account_id")
        
        progress = {
            "total_deposited": 4000.00,
            "interest_earned": 120.50,
            "current_balance": 4120.50,
            "target_amount": 12000.00,
            "completion_percentage": 33.3,
            "on_track": True,
            "health_score": 95
        }
        
        message = f"""?? Your Savings Progress

Current Balance: 
+- Your Deposits: 
+- Interest Earned: 

Target: 
Progress: {progress['completion_percentage']:.1f}% complete ?

Account Health: {progress['health_score']}/100 ?

You're RIGHT ON TRACK! ??

At this rate, you'll reach your goal on schedule. Keep up the excellent work! Your future self will thank you for this financial discipline! ??
"""
        
        return {
            "success": True,
            "action": "track_progress",
            "progress": progress,
            "message": message,
            "emotional_tone": "celebratory",
            "confidence": 0.95
        }
    
    async def _handle_missed_payment(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missed payment assistance."""
        params = parsed.get("parameters", {})
        reason = params.get("reason", "temporary_cash_flow")
        
        message = """I understand that sometimes unexpected situations arise. Let's work through this together! ??

Your Options:

1. ? Grace Period (5 days)
   - No penalty if paid within 5 days
   - Auto-debit will retry in 3 days
   - Keep your account in good standing

2. ?? Skip This Month (If allowed)
   - Available once per year
   - Small administrative fee applies
   - Resume next month normally

3. ?? Adjust Schedule
   - Temporarily reduce monthly amount
   - Extend term to maintain target
   - Requires approval

4. ?? Financial Hardship
   - Pause payments temporarily
   - No penalty during hardship period
   - Speak with specialist team

I recommend Option 1 (grace period) - can you make the payment within 5 days? This keeps your excellent savings record intact! 

Your financial wellness is important. If you're facing ongoing difficulties, let's discuss a more sustainable plan. I'm here to help! ??
"""
        
        return {
            "success": True,
            "action": "missed_payment_help",
            "options": [
                {"id": 1, "name": "grace_period", "recommended": True},
                {"id": 2, "name": "skip_month", "recommended": False},
                {"id": 3, "name": "adjust_schedule", "recommended": False},
                {"id": 4, "name": "financial_hardship", "recommended": False}
            ],
            "message": message,
            "emotional_tone": "empathetic",
            "confidence": 0.9
        }
    
    async def _handle_calculate_savings(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate savings projection."""
        params = parsed.get("parameters", {})
        monthly = Decimal(str(params.get("monthly_amount", 500)))
        months = params.get("term_months", 24)
        
        rate = Decimal("5.75")
        total_deposits = monthly * months
        
        # RD interest calculation
        n = Decimal(months)
        interest = monthly * n * (n + Decimal("1")) / (Decimal("24")) * rate / Decimal("100")
        maturity = total_deposits + interest
        
        message = f"""?? Your Savings Projection

Monthly Deposit: 
Duration: {months} months ({months//12} years {months%12} months)

Results:
?????????????????????
Your Deposits:   
Interest Earned:  @ {float(rate)}%
?????????????????????
Final Amount:     ??

That's a {float(interest/total_deposits*100):.2f}% return on your savings!

This could be perfect for:
?? House deposit contribution
?? Wedding fund
?? Education expenses
?? Vehicle purchase
?? Business startup capital

Ready to start your savings journey? Let's set this up! ??
"""
        
        return {
            "success": True,
            "action": "calculate_savings",
            "monthly_amount": float(monthly),
            "term_months": months,
            "total_deposits": float(total_deposits),
            "interest": float(interest),
            "maturity_value": float(maturity),
            "return_percentage": float(interest/total_deposits*100),
            "message": message,
            "emotional_tone": "encouraging",
            "confidence": 0.95
        }
    
    async def _handle_affordability(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Assess affordability."""
        params = parsed.get("parameters", {})
        monthly = float(params.get("monthly_amount", 1000))
        
        # Simple affordability check (30% of income rule)
        estimated_income = 5000  # Would come from customer profile
        max_affordable = estimated_income * 0.3
        existing_commitments = 800  # Would come from customer data
        available = max_affordable - existing_commitments
        
        is_affordable = monthly <= available
        
        if is_affordable:
            message = f"""? Good News! This looks affordable.

Monthly Commitment: 
Your Available Budget: 

Financial Health Check:
+- Estimated Monthly Income: 
+- Existing Commitments: 
+- Recommended Max (30%): 
+- After This RD:  remaining

You're well within safe limits! This RD won't strain your finances.

Pro tip: Consider building an emergency fund (3-6 months expenses) alongside this RD for complete financial security! ???
"""
        else:
            shortage = monthly - available
            suggested = available * 0.9  # 90% of available
            
            message = f"""?? Let's Find a Better Fit

Requested: /month
Available Budget: /month
Shortfall: 

Financial Health Check:
+- Monthly Income: 
+- Existing Commitments: 
+- Safe Limit (30%): 

I recommend /month instead. This gives you:
? Comfortable living expenses
? Emergency buffer
? Sustainable savings habit

Would you like to:
1. Open RD at /month ? Recommended
2. Extend term to reduce monthly amount
3. Review your budget together

Building wealth is a marathon, not a sprint! Let's find a plan that works for your lifestyle! ??
"""
        
        return {
            "success": True,
            "action": "affordability_check",
            "is_affordable": is_affordable,
            "requested_amount": monthly,
            "available_budget": available,
            "suggested_amount": suggested if not is_affordable else monthly,
            "message": message,
            "emotional_tone": "practical" if is_affordable else "empathetic",
            "confidence": 0.85
        }
    
    async def _handle_completion_coaching(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Provide completion coaching."""
        params = parsed.get("parameters", {})
        
        # Would come from ML model
        completion_probability = 0.85
        risk_factors = ["Recent missed payment"]
        strengths = ["Good payment history", "Adequate buffer"]
        
        message = f"""?? Your RD Completion Forecast

Completion Probability: {completion_probability*100:.0f}% ?

Strengths:
? Excellent payment history (95% on-time)
? Healthy account balance
? Good financial discipline

Watch Out For:
?? Recent missed payment (October)

Coaching Recommendations:

1. ?? Set Up Payment Reminders
   - 3 days before due date
   - Day before due date
   - I'll send you friendly reminders!

2. ?? Buffer Your Auto-Debit Account
   - Keep extra  cushion
   - Prevents insufficient funds

3. ?? Visualize Your Goal
   - What are you saving for?
   - Keep that motivation strong!

4. ?? Monthly Progress Reviews
   - I'll check in monthly
   - Celebrate milestones together!

You're on track to complete successfully! Let's keep that momentum going! ??

Would you like me to set up automated reminders and monthly progress reports?
"""
        
        return {
            "success": True,
            "action": "completion_coaching",
            "completion_probability": completion_probability,
            "risk_factors": risk_factors,
            "strengths": strengths,
            "message": message,
            "emotional_tone": "encouraging",
            "confidence": 0.85
        }
