"""Anya - Natural Language Collateral Management Agent"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date
import json

from anthropic import Anthropic

from ultracore.anya.agent import AnyaAgent
from ..services import CollateralService
from ..integrations.ppsr import PPSRClient


class AnyaCollateralAgent(AnyaAgent):
    """
    Anya's Collateral Management specialist.
    
    Natural language interface for:
    - Registering collateral: "Register my 2022 Toyota Camry as security"
    - Checking PPSR: "Is there any existing security on VIN ABC123?"
    - LVR monitoring: "What's the current LVR on my home loan?"
    - Valuation updates: "My property was just revalued at "
    - Insurance compliance: "Do I need insurance on my equipment loan?"
    - Release requests: "I've paid off my car loan, release the security"
    
    Australian compliance expertise:
    - PPSR registration requirements
    - PPSA enforcement rules
    - State land title systems
    - LMI requirements
    - Valuation standards
    """
    
    def __init__(
        self,
        anthropic_client: Anthropic,
        collateral_service: CollateralService,
        ppsr_client: PPSRClient,
        customer_id: str
    ):
        super().__init__(
            name="AnyaCollateralAgent",
            description="Natural language interface for collateral management",
            capabilities=[
                "Register collateral",
                "Search PPSR",
                "Monitor LVR",
                "Track valuations",
                "Check insurance compliance",
                "Release collateral",
                "Explain security requirements"
            ]
        )
        self.anthropic = anthropic_client
        self.collateral_service = collateral_service
        self.ppsr = ppsr_client
        self.customer_id = customer_id
    
    async def execute(self, natural_language_request: str) -> Dict[str, Any]:
        """
        Process natural language request about collateral.
        
        Examples:
        - "I need to register my car as security for my loan"
        - "Check if my house is already mortgaged"
        - "What happens if my property value drops?"
        - "How do I get my car title back after paying off the loan?"
        - "Explain PPSR to me in simple terms"
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
        
        if intent == "register_collateral":
            return await self._handle_register_collateral(parsed)
        elif intent == "ppsr_search":
            return await self._handle_ppsr_search(parsed)
        elif intent == "check_lvr":
            return await self._handle_check_lvr(parsed)
        elif intent == "insurance_check":
            return await self._handle_insurance_check(parsed)
        elif intent == "release_request":
            return await self._handle_release_request(parsed)
        elif intent == "explain_ppsr":
            return await self._handle_explain_ppsr(parsed)
        elif intent == "valuation_update":
            return await self._handle_valuation_update(parsed)
        else:
            return {
                "success": False,
                "error": f"Unknown intent: {intent}",
                "confidence": parsed.get("confidence", 0.0)
            }
    
    def _get_system_prompt(self) -> str:
        """System prompt for Anya as collateral specialist."""
        return """You are Anya, an AI banking assistant specializing in collateral management and security interests in Australia.

Your role is to:
1. Help customers understand collateral requirements
2. Guide through PPSR (Personal Property Securities Register) processes
3. Monitor LVR (Loan-to-Value Ratio) compliance
4. Explain security interests in plain language
5. Track insurance requirements
6. Facilitate collateral release

Australian context expertise:
- PPSA (Personal Property Securities Act 2009)
- PPSR registration and priority rules
- State land title systems (Torrens)
- LMI (Lenders Mortgage Insurance) for LVR > 80%
- Valuation requirements and standards
- Consumer protections under NCCP

Respond in JSON format:
{
    "intent": "register_collateral|ppsr_search|check_lvr|insurance_check|release_request|explain_ppsr|valuation_update",
    "parameters": {
        "collateral_type": <string>,
        "description": <string>,
        "value": <number>,
        "vin": <string>,
        ...
    },
    "confidence": <0.0-1.0>,
    "emotional_tone": "informative|reassuring|cautionary|supportive",
    "reasoning": "Why you chose this interpretation"
}

Key principles:
- Always explain Australian legal requirements clearly
- Be transparent about PPSR and security interests
- Warn about LVR breaches proactively
- Emphasize importance of insurance
- Simplify legal jargon

Australian compliance notes:
- PPSR registration establishes priority (first to register wins)
- Must discharge PPSR within 5 business days of loan repayment
- Real property uses state land title system, not PPSR
- LVR > 80% typically requires Lenders Mortgage Insurance
- Professional valuation required for properties > 
"""
    
    def _build_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """Build prompt with customer context."""
        return f"""Customer Request: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Active Collateral: {len(context.get('active_collateral', []))}
- Loans with Security: {context.get('secured_loans', [])}
- Average LVR: {context.get('average_lvr', 0):.1f}%
- Insurance Compliant: {context.get('insurance_compliant', True)}
- State: {context.get('state', 'NSW')}

Current Market Context:
- Sydney median house price: ,123,000
- Melbourne median house price: ,000
- Brisbane median house price: ,000
- Property market: {context.get('market_trend', 'stable')}

PPSR Info:
- https://www.ppsr.gov.au/
- Registration time establishes priority
- Search before taking security
- Discharge within 5 days of repayment

Parse the request and provide appropriate guidance.
"""
    
    async def _build_context(self) -> Dict[str, Any]:
        """Build customer context."""
        return {
            "active_collateral": [],
            "secured_loans": [],
            "average_lvr": 75.0,
            "insurance_compliant": True,
            "state": "NSW",
            "market_trend": "stable"
        }
    
    async def _handle_register_collateral(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collateral registration request."""
        params = parsed.get("parameters", {})
        collateral_type = params.get("collateral_type", "motor_vehicle")
        description = params.get("description", "")
        estimated_value = Decimal(str(params.get("value", 0)))
        
        # Check if PPSR required
        ppsr_required = collateral_type not in ["real_property_residential", "real_property_commercial"]
        
        message = f"""Great! Let's register your {collateral_type.replace('_', ' ')} as security.

?? Registration Details:
- Type: {collateral_type.replace('_', ' ').title()}
- Description: {description}
- Estimated Value: 

"""
        
        if ppsr_required:
            message += """?? PPSR Registration Required:

Your security interest will be registered on Australia's Personal Property Securities Register (PPSR). This is important because:

? Protects the bank's security interest
? Establishes priority (first to register = first priority)
? Required for enforcement if you default
? Public record (others can search it)

What happens next:
1. PPSR search to check existing securities
2. Complete security agreement
3. Register on PPSR (establishes priority timestamp)
4. You'll receive registration number

?? PPSR registration is typically instant, and the registration time establishes our priority position.

"""
        else:
            message += """?? Real Property Security:

For real property, we use the state land title system (not PPSR):

? Mortgage registered on Certificate of Title
? Caveat lodged for security
? Priority established by registration time
? State Land Registry: {state} Land Registry

What happens next:
1. Land title search
2. Professional valuation (required for loans > )
3. Mortgage documentation
4. Registration on title

"""
        
        # Check LVR and LMI requirement
        loan_amount = params.get("loan_amount", estimated_value * Decimal("0.8"))
        lvr = (loan_amount / estimated_value * Decimal("100")) if estimated_value > 0 else Decimal("0")
        
        if lvr > Decimal("80.0"):
            message += f"""?? Lenders Mortgage Insurance (LMI):

Your LVR is {float(lvr):.1f}%, which exceeds 80%. You'll need LMI to protect the bank against default risk.

- LMI Cost: Approximately  (one-time)
- Protects lender if property sold for less than loan amount
- Can be added to loan or paid upfront

"""
        
        message += """Would you like me to proceed with registration?

I'll need:
"""
        
        if ppsr_required:
            message += """- Serial number (VIN for vehicles)
- Purchase date and price
- Any existing finance/security
"""
        else:
            message += """- Property address
- Certificate of Title details
- Recent valuation (if available)
"""
        
        return {
            "success": True,
            "action": "register_collateral",
            "collateral_type": collateral_type,
            "estimated_value": float(estimated_value),
            "ppsr_required": ppsr_required,
            "lvr": float(lvr),
            "lmi_required": lvr > Decimal("80.0"),
            "message": message,
            "emotional_tone": "informative",
            "next_steps": ["verify_details", "ppsr_search", "complete_documentation"],
            "confidence": parsed.get("confidence", 0.9)
        }
    
    async def _handle_ppsr_search(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PPSR search request."""
        params = parsed.get("parameters", {})
        search_type = params.get("search_type", "serial_number")
        
        message = """?? PPSR Search

I'll search the Personal Property Securities Register to check for existing security interests.

Why this matters:
- Reveals existing loans/finance on the asset
- Shows your priority position
- Identifies fraud risk
- Required before taking security

What I'm searching:
"""
        
        if search_type == "serial_number":
            serial = params.get("serial_number", "")
            message += f"""- Serial Number: {serial}
- Type: Motor Vehicle (VIN search)

Searching for any registered security interests...
"""
            
            # Mock search results
            results = {
                "registrations_found": 0,
                "clear_title": True,
                "can_proceed": True
            }
            
        else:
            name = params.get("name", "")
            message += f"""- Name: {name}
- Search Type: Grantor search

Searching for any security interests against this person/company...
"""
            
            results = {
                "registrations_found": 0,
                "clear_title": True,
                "can_proceed": True
            }
        
        if results["clear_title"]:
            message += """
? CLEAR TITLE!

Good news! No existing security interests found. This means:
- No other lenders have security on this asset
- We can proceed with first-priority security
- Lower risk for the bank
- Better loan terms possible

Next steps:
1. Complete security documentation
2. Register our security interest on PPSR
3. Finalize loan

The asset is clear and ready to be used as security! ??
"""
        else:
            message += f"""
?? EXISTING SECURITY FOUND!

Found {results['registrations_found']} existing security interest(s):

This means:
- Another lender has security on this asset
- We'd be in second (or lower) priority
- Higher risk for the bank
- May need additional security

Options:
1. Pay out existing loan first
2. Provide additional collateral
3. Accept second-priority position (higher interest rate)

I recommend contacting the existing lender to discuss payout. Would you like help with that?
"""
        
        return {
            "success": True,
            "action": "ppsr_search",
            "search_results": results,
            "message": message,
            "emotional_tone": "informative",
            "confidence": 0.95
        }
    
    async def _handle_check_lvr(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LVR check request."""
        params = parsed.get("parameters", {})
        
        # Mock data
        current_value = Decimal("850000")
        loan_balance = Decimal("637500")
        lvr = (loan_balance / current_value * Decimal("100"))
        policy_max = Decimal("80.0")
        
        message = f"""?? Loan-to-Value Ratio (LVR) Analysis

Your Current Position:
?????????????????????
Property Value:  
Loan Balance:    
Current LVR:     {float(lvr):.1f}%
Policy Maximum:  {float(policy_max):.1f}%
?????????????????????

"""
        
        if lvr <= policy_max:
            buffer = policy_max - lvr
            value_drop_ok = current_value * buffer / Decimal("100")
            
            message += f"""? LVR COMPLIANT!

You're well within policy limits with a {float(buffer):.1f}% buffer.

This means:
- Your security position is strong
- Property value could drop by  and still be compliant
- No additional security required
- Good position for refinancing if needed

Keep it up! Your equity is building nicely! ??

"""
        else:
            breach = lvr - policy_max
            additional_required = loan_balance - (current_value * policy_max / Decimal("100"))
            
            message += f"""?? LVR BREACH DETECTED!

Your LVR exceeds policy limits by {float(breach):.1f}%.

What this means:
- Security position is weaker
- Bank may require action
- Refinancing may be difficult

Options to remedy:
1. Pay down loan by  ? Recommended
2. Provide additional collateral
3. Accept higher interest rate
4. Obtain updated valuation (if you think property value is higher)

I recommend option 1. Making additional payments will restore your compliant position and improve your equity. Would you like to set up extra repayments?

Don't worry - we're here to help you through this! ??
"""
        
        return {
            "success": True,
            "action": "check_lvr",
            "current_lvr": float(lvr),
            "policy_max_lvr": float(policy_max),
            "is_compliant": lvr <= policy_max,
            "buffer_percentage": float(policy_max - lvr) if lvr <= policy_max else 0,
            "message": message,
            "emotional_tone": "supportive" if lvr > policy_max else "reassuring",
            "confidence": 0.95
        }
    
    async def _handle_insurance_check(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle insurance compliance check."""
        params = parsed.get("parameters", {})
        collateral_type = params.get("collateral_type", "motor_vehicle")
        
        message = f"""??? Insurance Requirements

For {collateral_type.replace('_', ' ').title()} collateral, insurance is:

"""
        
        if collateral_type == "motor_vehicle":
            message += """? MANDATORY - Comprehensive Insurance Required

Why comprehensive cover is required:
- Protects the bank's security interest
- Covers damage, theft, total loss
- Bank must be noted as interested party
- Coverage must match or exceed loan amount

Your Requirements:
- Policy Type: Comprehensive motor vehicle insurance
- Sum Insured: Minimum market value of vehicle
- Interested Party: [Bank Name] must be noted
- Premium: Keep paid and current

?? Important:
If insurance lapses:
1. You breach your loan agreement
2. Bank may arrange insurance (at your cost)
3. Higher premiums (forced insurance)
4. Potential loan default

Current Status: [Would check actual status]

?? Pro Tip: Shop around for quotes, but make sure bank is noted as interested party on any new policy!
"""
        elif collateral_type == "real_property_residential":
            message += """? MANDATORY - Building Insurance Required

Why building insurance is required:
- Protects against fire, flood, storm damage
- Covers total reconstruction if needed
- Bank's security could be worthless without it
- Bank must be noted as mortgagee

Your Requirements:
- Policy Type: Home & Contents (Building portion mandatory)
- Sum Insured: Full replacement value
- Mortgagee: [Bank Name] must be noted
- Premium: Keep paid and current

?? Important:
If insurance lapses:
1. Breach of mortgage terms
2. Bank may arrange forced insurance
3. More expensive premiums
4. Risk of mortgage call (in extreme cases)

?? Pro Tip: 
- Review sum insured annually (building costs increase!)
- Consider flood cover if in flood-prone area
- Contents insurance is optional but recommended
"""
        
        message += """

Want me to check your current insurance status?
"""
        
        return {
            "success": True,
            "action": "insurance_check",
            "collateral_type": collateral_type,
            "insurance_mandatory": True,
            "message": message,
            "emotional_tone": "informative",
            "confidence": 0.95
        }
    
    async def _handle_release_request(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collateral release request."""
        params = parsed.get("parameters", {})
        
        message = """?? Congratulations on Paying Off Your Loan!

Let's get your security released. Here's the process:

?? PPSR Discharge Process:

Step 1: Verification ?
- Confirm loan fully repaid
- Check no outstanding fees/charges
- Verify all obligations satisfied

Step 2: PPSR Discharge (Required by Law)
?? We MUST discharge within 5 business days of your request
- This is a legal requirement under PPSA Section 178
- Failure = ,000 penalty for the bank
- You can rely on this timeline!

Step 3: Document Return
- Original Certificate of Title (if applicable)
- Security agreement documents
- Discharge confirmation letter

Step 4: Confirmation
- PPSR discharge confirmation number
- You can verify discharge on www.ppsr.gov.au
- Takes 24-48 hours to show on PPSR

Timeline:
- Today: Request received ?
- Day 1-2: Verification and processing
- Day 2-3: PPSR discharge lodged
- Day 3-5: Discharge completed
- Day 5: Documents returned to you

What You'll Receive:
?? Discharge Statement
?? PPSR Discharge Confirmation
?? Original documents (if held)

Important Note:
Once discharged from PPSR, the security interest is removed completely. You'll have full, unencumbered ownership!

Ready to proceed? I just need to verify a few details...
"""
        
        return {
            "success": True,
            "action": "release_request",
            "discharge_deadline_days": 5,
            "message": message,
            "emotional_tone": "celebratory",
            "next_steps": [
                "verify_loan_balance",
                "confirm_all_obligations_met",
                "lodge_ppsr_discharge",
                "return_documents"
            ],
            "confidence": 0.95
        }
    
    async def _handle_explain_ppsr(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Explain PPSR in simple terms."""
        message = """?? PPSR Explained (In Plain English!)

PPSR = Personal Property Securities Register
It's Australia's national online register for security interests in moveable property.

Think of it like this:
The PPSR is a public record that says "Bank XYZ has security over John's 2020 Toyota Camry."

?????????????????????
What Gets Registered?
?????????????????????
? Motor vehicles (cars, trucks, motorcycles)
? Watercraft (boats, jet skis)
? Aircraft
? Equipment and machinery
? Inventory and stock
? Accounts receivable

? Land and buildings (use state land title system instead)

?????????????????????
Why Does It Exist?
?????????????????????

Before 2012: Confusing mess!
- Different rules in each state
- No central register
- Hard to check existing securities
- Priority disputes common

After 2012 (PPSR launched):
- One national system
- Online searches
- Clear priority rules
- Reduced fraud

?????????????????????
Key Concepts
?????????????????????

1?? Priority = First to Register Wins
If you register at 10:00am and another lender registers at 10:01am, you have priority - even if they gave the loan first!

2?? Perfection = Legal Protection
"Perfecting" your security interest means registering it on PPSR. Without perfection, you might lose your security if the borrower goes bankrupt.

3?? Search Before You Lend
Always search PPSR before taking security. You need to know:
- Who else has security?
- What's your priority position?
- Any red flags?

4?? Discharge When Loan Repaid
Must remove PPSR registration within 5 business days of loan repayment. It's the law!

?????????????????????
Real World Example
?????????????????????

Sarah buys a car:
1. Dealer finances  through Bank A
2. Bank A registers on PPSR at 2:00pm
3. Bank A now has "first priority" security
4. If Sarah stops paying, Bank A can repossess
5. When Sarah pays off loan, Bank A must discharge PPSR within 5 days

Later, Sarah tries to refinance:
1. Bank B does PPSR search
2. Finds Bank A's registration
3. Knows Sarah still owes money
4. Waits for Bank A discharge before lending

See? It protects everyone!

?????????????????????
How to Use PPSR
?????????????????????

?? Website: www.ppsr.gov.au

As a borrower:
- Search to check what's registered against you
- Verify discharge when you pay off loans
- Free searches with your details

As a lender (like us):
- Search before taking security
- Register security interests
- Discharge when loan repaid
- Update registrations if needed

?????????????????????
Cost
?????????????????????

Registration: ~- depending on duration
Search: ~-
Discharge: ~

Not expensive for the protection it provides!

?????????????????????
Your Rights
?????????????????????

? Right to know what's registered against you
? Right to prompt discharge (5 days)
? Right to correct incorrect registrations
? Protected from hidden securities
? Can verify discharge yourself online

?????????????????????

Questions? I'm here to help explain anything else about PPSR! ??
"""
        
        return {
            "success": True,
            "action": "explain_ppsr",
            "message": message,
            "emotional_tone": "educational",
            "resources": [
                "https://www.ppsr.gov.au/",
                "https://www.ppsr.gov.au/searching-ppsr",
                "PPSA 2009 Legislation"
            ],
            "confidence": 1.0
        }
    
    async def _handle_valuation_update(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle valuation update notification."""
        params = parsed.get("parameters", {})
        new_value = Decimal(str(params.get("new_value", 0)))
        
        message = f"""?? Property Valuation Update

New Valuation: 

Great! I'll update our records with the new valuation.

What happens next:
1. Review the valuation report
2. Verify valuer credentials (API registered)
3. Recalculate LVR
4. Check compliance
5. Update insurance requirements

Give me a moment to process this...

[Processing...]

? Update Complete!

Your new LVR has been calculated. Would you like me to show you the updated position?
"""
        
        return {
            "success": True,
            "action": "valuation_update",
            "new_value": float(new_value),
            "message": message,
            "emotional_tone": "supportive",
            "confidence": 0.9
        }
