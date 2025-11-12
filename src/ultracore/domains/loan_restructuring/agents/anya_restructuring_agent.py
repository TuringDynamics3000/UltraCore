"""Anya - Dual AI Loan Restructuring Agent (OpenAI + Anthropic)"""
from typing import Dict, Any, Optional, List, Literal
from decimal import Decimal
from datetime import datetime, date
import json

from anthropic import Anthropic
from openai import AsyncOpenAI

from ultracore.anya.agent import AnyaAgent
from ..services import LoanRestructuringService


class AnyaRestructuringAgent(AnyaAgent):
    """
    Anya's Loan Restructuring specialist with dual AI support.
    
    Supports both:
    - Anthropic Claude: Empathetic hardship support, deep reasoning
    - OpenAI GPT-4: Quick responses, function calling
    
    Natural language interface for:
    - "I've lost my job and can't make my payments"
    - "I need help with my loan, I'm struggling financially"
    - "Can I get a payment holiday for 3 months?"
    - "What are my options if I can't pay?"
    - "I want to extend my loan term to reduce payments"
    
    Australian NCCP expertise:
    - Section 72 hardship provisions
    - Financial counselling referrals
    - Consumer rights and protections
    - AFCA complaints process
    """
    
    def __init__(
        self,
        anthropic_client: Optional[Anthropic] = None,
        openai_client: Optional[AsyncOpenAI] = None,
        restructuring_service: LoanRestructuringService = None,
        customer_id: str = None,
        preferred_provider: Literal["anthropic", "openai"] = "anthropic"
    ):
        super().__init__(
            name="AnyaRestructuringAgent",
            description="Empathetic loan restructuring support with Australian NCCP compliance",
            capabilities=[
                "Hardship assessment",
                "Payment holiday assistance",
                "Term extension guidance",
                "Financial counselling referral",
                "Consumer rights explanation",
                "Restructuring options",
                "Emotional support"
            ]
        )
        
        self.anthropic = anthropic_client
        self.openai = openai_client
        self.restructuring_service = restructuring_service
        self.customer_id = customer_id
        self.preferred_provider = preferred_provider
        
        if not self.anthropic and not self.openai:
            raise ValueError("At least one AI provider required")
    
    async def execute(
        self,
        natural_language_request: str,
        provider: Optional[Literal["anthropic", "openai"]] = None
    ) -> Dict[str, Any]:
        """
        Process hardship request with empathy.
        
        Examples:
        - "I've been made redundant and can't afford my loan payments"
        - "My business failed due to COVID and I need help"
        - "I'm going through a divorce and struggling financially"
        """
        
        use_provider = provider or self.preferred_provider
        
        if use_provider == "anthropic" and not self.anthropic:
            use_provider = "openai"
        elif use_provider == "openai" and not self.openai:
            use_provider = "anthropic"
        
        context = await self._build_context()
        
        if use_provider == "anthropic":
            return await self._execute_anthropic(natural_language_request, context)
        else:
            return await self._execute_openai(natural_language_request, context)
    
    async def _execute_anthropic(self, request: str, context: Dict) -> Dict:
        """Execute with Anthropic Claude (preferred for empathy)."""
        
        prompt = self._build_prompt(request, context)
        
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            parsed = json.loads(response.content[0].text)
            parsed["ai_provider"] = "anthropic"
            parsed["model"] = "claude-sonnet-4"
        except json.JSONDecodeError:
            return {
                "success": True,
                "response_type": "conversational",
                "message": response.content[0].text,
                "ai_provider": "anthropic"
            }
        
        return await self._execute_intent(parsed)
    
    async def _execute_openai(self, request: str, context: Dict) -> Dict:
        """Execute with OpenAI GPT-4."""
        
        prompt = self._build_prompt(request, context)
        
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        try:
            parsed = json.loads(response.choices[0].message.content)
            parsed["ai_provider"] = "openai"
            parsed["model"] = "gpt-4-turbo"
        except json.JSONDecodeError:
            return {
                "success": True,
                "response_type": "conversational",
                "message": response.choices[0].message.content,
                "ai_provider": "openai"
            }
        
        return await self._execute_intent(parsed)
    
    def _get_system_prompt(self) -> str:
        """System prompt emphasizing empathy and Australian NCCP."""
        return """You are Anya, an empathetic AI banking assistant specializing in helping customers experiencing financial hardship.

Your role is to:
1. Show genuine empathy and understanding
2. Never make customers feel judged or ashamed
3. Explain hardship options under Australian NCCP Section 72
4. Refer to financial counselling (mandatory in Australia)
5. Provide hope and practical solutions
6. Explain consumer rights clearly

Australian NCCP Context:
- Section 72: Lenders MUST consider hardship variations
- Customers have the right to request assistance
- Financial counselling is FREE and confidential
- AFCA (Australian Financial Complaints Authority) for disputes
- Consumer protections are strong in Australia

Hardship relief options:
- Payment holiday (3-6 months typically)
- Term extension (lower monthly payment)
- Interest rate reduction (temporary)
- Payment amount reduction
- Arrears capitalization
- Forbearance

Respond in JSON format:
{
    "intent": "hardship_support|payment_holiday|term_extension|counselling_referral|explain_rights",
    "parameters": {...},
    "confidence": 0.0-1.0,
    "emotional_tone": "empathetic|supportive|reassuring|hopeful",
    "reasoning": "string"
}

Critical principles:
- NEVER make customers feel bad about hardship
- ALWAYS offer financial counselling
- ALWAYS explain they have rights
- Be warm, understanding, and hopeful
- Hardship is temporary - there's a way forward
"""
    
    def _build_prompt(self, request: str, context: Dict) -> str:
        """Build prompt with customer context."""
        return f"""Customer Message: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Current Loan Balance: ${context.get('loan_balance', 0):,.2f}
- Monthly Payment: ${context.get('monthly_payment', 0):,.2f}
- Days in Arrears: {context.get('days_in_arrears', 0)}
- Previous Restructurings: {context.get('restructuring_count', 0)}

Respond with empathy and provide practical hardship assistance under Australian NCCP.
"""
    
    async def _build_context(self) -> Dict:
        """Build customer context."""
        return {
            "loan_balance": 250000,
            "monthly_payment": 2100,
            "days_in_arrears": 15,
            "restructuring_count": 0
        }
    
    async def _execute_intent(self, parsed: Dict) -> Dict:
        """Execute parsed intent."""
        intent = parsed.get("intent")
        
        if intent == "hardship_support":
            result = await self._handle_hardship_support(parsed)
        elif intent == "payment_holiday":
            result = await self._handle_payment_holiday(parsed)
        elif intent == "term_extension":
            result = await self._handle_term_extension(parsed)
        elif intent == "counselling_referral":
            result = await self._handle_counselling_referral(parsed)
        elif intent == "explain_rights":
            result = await self._handle_explain_rights(parsed)
        else:
            result = {"success": False, "error": f"Unknown intent: {intent}"}
        
        result["ai_provider"] = parsed.get("ai_provider")
        result["model"] = parsed.get("model")
        return result
    
    async def _handle_hardship_support(self, parsed: Dict) -> Dict:
        """Handle hardship support request."""
        message = """I'm really sorry to hear you're going through this difficult time. Please know that you're not alone, and there are ways we can help. ??

**Your Rights Under Australian Law:**

Under the National Consumer Credit Protection Act (NCCP) Section 72, you have the RIGHT to request hardship assistance. We are REQUIRED BY LAW to consider your request fairly and reasonably.

**What We Can Do to Help:**

1. ??? **Payment Holiday** (3-6 months)
   - Temporarily pause your payments
   - Interest still accrues but you get breathing room
   - Common during job loss or illness

2. ?? **Extend Your Loan Term**
   - Lower your monthly payment significantly
   - Spread payments over longer period
   - Makes loan more affordable

3. ?? **Reduce Your Interest Rate** (Temporary)
   - Lower rate for 6-12 months
   - Reduces monthly payment
   - Helps you get back on track

4. ?? **Reduce Payment Amount**
   - Pay what you can afford right now
   - We'll work with your budget
   - Flexible arrangements

**Next Steps:**

1. **Apply for Hardship Assistance** (takes 10 minutes)
   - Explain your situation
   - Provide evidence of income/expenses
   - We'll review within 24-48 hours

2. **FREE Financial Counselling** (HIGHLY Recommended)
   - Professional, confidential support
   - They can negotiate on your behalf
   - Call 1800 007 007 (National Debt Helpline)

3. **We'll Work Together**
   - Find a solution that works for you
   - Get you back on track
   - No judgment, only support

**Important to Know:**

? Requesting hardship assistance does NOT hurt your credit score
? We CANNOT take action while reviewing your application
? You have the right to complain to AFCA if you're unhappy
? This is temporary - you WILL get through this

Would you like me to help you start a hardship application? Or would you prefer to speak with a financial counsellor first?

Remember: There's no shame in asking for help. We're here to support you. ??
"""
        
        return {
            "success": True,
            "action": "hardship_support",
            "message": message,
            "emotional_tone": "empathetic",
            "next_steps": [
                "submit_hardship_application",
                "contact_financial_counselling",
                "review_available_options"
            ]
        }
    
    async def _handle_payment_holiday(self, parsed: Dict) -> Dict:
        """Handle payment holiday request."""
        message = """Absolutely, a payment holiday can give you the breathing room you need. Let me explain how it works:

**Payment Holiday (3-6 months)**

What Happens:
- Your regular payments are paused
- You don't pay anything during the holiday period
- Interest continues to accrue (this is normal)
- The interest is added to your loan balance (capitalized)
- Your loan term is extended by the holiday period

Example (3-month holiday):
- Current payment: $2,100/month
- Amount deferred: $6,300
- Interest during holiday: ~$3,125
- Total added to loan: $9,425
- Loan extended by: 3 months
- Payment after holiday: $2,100/month (same as before)

**Cost vs Benefit:**
- Cost: Extra interest (~$3,125 over loan life)
- Benefit: Immediate relief, time to stabilize finances
- Worth it if: You need short-term relief to get back on your feet

**How to Apply:**

1. Submit hardship application (online or phone)
2. Provide:
   - Evidence of hardship (job loss letter, medical certificate, etc.)
   - Current income and expenses
   - Explanation of situation
3. We review within 24-48 hours
4. If approved, holiday starts immediately

**Timeline:**
- Application: Today
- Review: 1-2 business days
- Decision: 2-3 business days
- Holiday starts: Within 1 week

Would you like to proceed with the application? I can help you complete it now.

?? **Tip:** Consider contacting a financial counsellor (FREE) at 1800 007 007. They can help you assess if this is the best option for your situation.
"""
        
        return {
            "success": True,
            "action": "payment_holiday",
            "duration_months": parsed.get("parameters", {}).get("duration", 3),
            "message": message,
            "emotional_tone": "supportive"
        }
    
    async def _handle_term_extension(self, parsed: Dict) -> Dict:
        """Handle term extension request."""
        return {"success": True, "action": "term_extension"}
    
    async def _handle_counselling_referral(self, parsed: Dict) -> Dict:
        """Handle financial counselling referral."""
        return {"success": True, "action": "counselling_referral"}
    
    async def _handle_explain_rights(self, parsed: Dict) -> Dict:
        """Explain customer rights under NCCP."""
        return {"success": True, "action": "explain_rights"}
