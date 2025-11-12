"""Anya - AI Payments Assistant (OpenAI)"""
from typing import Dict, Any, Optional
from decimal import Decimal
import json

from openai import AsyncOpenAI

from ultracore.anya.agent import AnyaAgent
from ..services import PaymentService


class AnyaPaymentsAgent(AnyaAgent):
    """
    Anya's Payments specialist powered by OpenAI.
    
    Natural language interface for:
    - "Send $50 to john@example.com using PayID"
    - "Pay my electricity bill (BPAY 12345, ref 9876543210)"
    - "Send USD 1000 to my friend in the US"
    - "What's the fastest way to pay someone?"
    - "How do I register PayID?"
    
    Australian payment expertise:
    - NPP instant payments with PayID
    - BPAY bill payments
    - SWIFT international transfers
    - Payment limits and security
    - Fraud prevention
    """
    
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        payment_service: PaymentService = None,
        customer_id: str = None
    ):
        super().__init__(
            name="AnyaPaymentsAgent",
            description="AI assistant for payments (NPP/BPAY/SWIFT)",
            capabilities=[
                "NPP instant payments",
                "PayID setup",
                "BPAY bill payments",
                "International transfers",
                "Payment tracking",
                "Security advice"
            ]
        )
        
        self.openai = openai_client
        self.payment_service = payment_service
        self.customer_id = customer_id
    
    async def execute(
        self,
        natural_language_request: str
    ) -> Dict[str, Any]:
        """Process payment request."""
        
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
        """System prompt for Anya as payments expert."""
        return """You are Anya, an AI banking assistant specializing in payments.

Your role is to help customers:
1. Send payments quickly and securely
2. Understand payment options (NPP, BPAY, SWIFT)
3. Register and use PayID
4. Pay bills efficiently
5. Send money internationally

Australian Payment Systems:
- NPP: Instant payments (seconds), 24/7, uses PayID
- BPAY: Bill payments (1-3 days), biller codes + reference
- SWIFT: International (1-5 days), BIC codes, currencies

PayID:
- Email, mobile, or ABN
- Makes payments easy - no BSB/account needed
- Instant like NPP
- Free to register and use

Security:
- Always verify recipient details
- Watch for scams (too good to be true)
- Check payment limits
- Use PayID when possible (safer)

Respond in JSON format:
{
    "intent": "send_npp|send_bpay|send_swift|register_payid|payment_advice",
    "parameters": {...},
    "confidence": 0.0-1.0,
    "emotional_tone": "helpful|cautionary|encouraging",
    "reasoning": "string"
}

Be helpful, secure, and fast. Help customers move money safely.
"""
    
    def _build_prompt(self, request: str, context: Dict) -> str:
        """Build prompt with context."""
        return f"""Customer Request: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Daily Transfer Limit Remaining: ${context.get('daily_limit_remaining', 10000):,.2f}
- PayID Registered: {context.get('payid_registered', False)}

Parse the request and assist with payment.
"""
    
    async def _build_context(self) -> Dict:
        """Build customer context."""
        return {
            "daily_limit_remaining": 10000.00,
            "payid_registered": True
        }
    
    async def _execute_intent(self, parsed: Dict) -> Dict:
        """Execute parsed intent."""
        intent = parsed.get("intent")
        
        if intent == "send_npp":
            result = await self._handle_send_npp(parsed)
        elif intent == "send_bpay":
            result = await self._handle_send_bpay(parsed)
        elif intent == "send_swift":
            result = await self._handle_send_swift(parsed)
        elif intent == "register_payid":
            result = await self._handle_register_payid(parsed)
        elif intent == "payment_advice":
            result = await self._handle_payment_advice(parsed)
        else:
            result = {"success": False, "error": f"Unknown intent: {intent}"}
        
        return result
    
    async def _handle_send_npp(self, parsed: Dict) -> Dict:
        """Handle NPP payment request."""
        params = parsed.get("parameters", {})
        
        message = """**NPP Instant Payment** ?

I'll help you send an instant payment via NPP (New Payments Platform).

**What You Need:**
- Amount: ${amount}
- PayID (email/mobile) OR BSB + Account Number
- Description

**Benefits of NPP:**
? Instant (typically < 5 seconds)
? 24/7/365 availability
? Money arrives immediately
? Secure and reliable

**PayID is Easier!** ??
Instead of BSB + Account, just use:
- Email address (e.g., john@example.com)
- Mobile number (e.g., 0412 345 678)
- ABN (for businesses)

The payment still goes to their bank account - PayID is just an easier way to address it!

**Security Check:** ?
- Verify recipient name before confirming
- Never send money to someone you don't know
- If it seems too good to be true, it probably is

Ready to proceed? I'll need:
1. Recipient's PayID or BSB+Account
2. Amount
3. Description/reference
"""
        
        return {
            "success": True,
            "action": "send_npp",
            "message": message,
            "parameters": params,
            "next_step": "confirm_details"
        }
    
    async def _handle_send_bpay(self, parsed: Dict) -> Dict:
        """Handle BPAY payment request."""
        message = """**BPAY Bill Payment** ??

BPAY makes paying bills easy! Here's how it works:

**What You Need:**
- Biller Code (6 digits) - Find on your bill
- Reference Number - Your customer number at biller
- Amount

**Examples:**
- Sydney Water: Biller Code 12345
- AGL Energy: Biller Code 23456
- Telstra: Biller Code 34567

**Processing Time:** ??
- Submitted instantly (24/7)
- Biller receives: 1-3 business days
- Always pay before due date!

**Pro Tips:**
?? Save frequent billers for quick payments
?? Set up recurring BPAY for regular bills
?? Check your bill for exact biller code and reference

Ready to pay your bill? I'll need:
1. Biller Code (6 digits)
2. Reference Number (on your bill)
3. Amount
"""
        
        return {
            "success": True,
            "action": "send_bpay",
            "message": message,
            "next_step": "get_biller_details"
        }
    
    async def _handle_send_swift(self, parsed: Dict) -> Dict:
        """Handle SWIFT payment request."""
        message = """**International Payment (SWIFT)** ??

Sending money overseas? Here's what you need to know:

**Required Information:**
- Beneficiary Name
- Beneficiary Bank Account Number
- Bank SWIFT/BIC Code (8-11 characters)
- Bank Name and Address
- Bank Country
- Amount and Currency

**IBAN (if applicable):**
- Europe, Middle East: Usually requires IBAN
- US, Asia: Account number usually sufficient

**Timeline:** ??
- Processing: 1-5 business days
- Depends on countries and correspondent banks

**Costs:** ??
- Our fee: $25 AUD
- Correspondent bank fees: May apply (varies)
- Fee option: SHA (shared), OUR (we pay all), BEN (they pay all)

**Exchange Rates:** ??
- Live interbank rates
- Small margin applied
- Rate locked at submission

**Security:** ??
- Verify all beneficiary details carefully
- Check bank SWIFT code at swift.com
- Never send to someone you haven't verified

**Pro Tip:** Consider services like Wise or OFX for better rates on smaller amounts!

Ready to proceed? I'll need all the beneficiary and bank details.
"""
        
        return {
            "success": True,
            "action": "send_swift",
            "message": message,
            "next_step": "get_beneficiary_details"
        }
    
    async def _handle_register_payid(self, parsed: Dict) -> Dict:
        """Handle PayID registration."""
        message = """**Register PayID** ??

PayID makes receiving money super easy! Register your email or mobile number.

**Benefits:**
? Easy to remember (no BSB/account needed)
? Payments arrive instantly via NPP
? Free to register and use
? More secure (recipient verified before payment)

**What to Register:**
- Email address (personal or business)
- Mobile number (Australian numbers only)
- ABN (for businesses)

**How It Works:**
1. Choose your PayID (email or mobile)
2. Link it to your account
3. Verify it (we'll send a code)
4. Start receiving instant payments!

**Security:** ??
- Your PayID is public (others can see it)
- Your account details stay private
- You control which account it links to

**One PayID Per Account:**
- Each account can have one email PayID
- Each account can have one mobile PayID
- You can change or remove PayID anytime

Ready to register? Which would you like to use:
1. Email address
2. Mobile number
3. ABN (if business account)
"""
        
        return {
            "success": True,
            "action": "register_payid",
            "message": message,
            "next_step": "choose_payid_type"
        }
    
    async def _handle_payment_advice(self, parsed: Dict) -> Dict:
        """Provide payment advice."""
        return {
            "success": True,
            "action": "payment_advice",
            "message": "I can help you choose the best payment method!"
        }
