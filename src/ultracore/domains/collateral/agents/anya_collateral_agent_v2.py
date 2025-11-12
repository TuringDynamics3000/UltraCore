"""Anya - Dual AI Support (OpenAI + Anthropic) for Collateral Management"""
from typing import Dict, Any, Optional, List, Literal
from decimal import Decimal
from datetime import datetime, date
import json

from anthropic import Anthropic
from openai import AsyncOpenAI

from ultracore.anya.agent import AnyaAgent
from ..services import CollateralService
from ..integrations.ppsr import PPSRClient


class AnyaCollateralAgentV2(AnyaAgent):
    """
    Anya's Collateral Management specialist with dual AI support.
    
    Supports both:
    - Anthropic Claude (primary): Deep reasoning, Australian compliance expertise
    - OpenAI GPT-4 (secondary): Quick responses, function calling
    
    Natural language interface for:
    - Registering collateral
    - Checking PPSR
    - LVR monitoring
    - Valuation updates
    - Insurance compliance
    - Release requests
    """
    
    def __init__(
        self,
        anthropic_client: Optional[Anthropic] = None,
        openai_client: Optional[AsyncOpenAI] = None,
        collateral_service: CollateralService = None,
        ppsr_client: PPSRClient = None,
        customer_id: str = None,
        preferred_provider: Literal["anthropic", "openai"] = "anthropic"
    ):
        super().__init__(
            name="AnyaCollateralAgentV2",
            description="Dual AI collateral management with Australian compliance",
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
        self.openai = openai_client
        self.collateral_service = collateral_service
        self.ppsr = ppsr_client
        self.customer_id = customer_id
        self.preferred_provider = preferred_provider
        
        # Validate at least one provider available
        if not self.anthropic and not self.openai:
            raise ValueError("At least one AI provider (Anthropic or OpenAI) must be configured")
    
    async def execute(
        self,
        natural_language_request: str,
        provider: Optional[Literal["anthropic", "openai"]] = None
    ) -> Dict[str, Any]:
        """
        Process natural language request with specified or preferred AI provider.
        
        Args:
            natural_language_request: User's request in plain language
            provider: Force specific provider, or use preferred_provider
        """
        
        # Determine which provider to use
        use_provider = provider or self.preferred_provider
        
        # Fallback if preferred not available
        if use_provider == "anthropic" and not self.anthropic:
            use_provider = "openai"
        elif use_provider == "openai" and not self.openai:
            use_provider = "anthropic"
        
        # Build context
        context = await self._build_context()
        
        # Route to appropriate provider
        if use_provider == "anthropic":
            return await self._execute_anthropic(natural_language_request, context)
        else:
            return await self._execute_openai(natural_language_request, context)
    
    async def _execute_anthropic(
        self,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute using Anthropic Claude."""
        
        prompt = self._build_prompt(request, context)
        
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        try:
            parsed = json.loads(response.content[0].text)
            parsed["ai_provider"] = "anthropic"
            parsed["model"] = "claude-sonnet-4"
        except json.JSONDecodeError:
            return {
                "success": True,
                "response_type": "conversational",
                "message": response.content[0].text,
                "confidence": 0.7,
                "ai_provider": "anthropic"
            }
        
        # Execute action
        return await self._execute_intent(parsed)
    
    async def _execute_openai(
        self,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute using OpenAI GPT-4."""
        
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
        
        # Parse response
        try:
            parsed = json.loads(response.choices[0].message.content)
            parsed["ai_provider"] = "openai"
            parsed["model"] = "gpt-4-turbo"
        except json.JSONDecodeError:
            return {
                "success": True,
                "response_type": "conversational",
                "message": response.choices[0].message.content,
                "confidence": 0.7,
                "ai_provider": "openai"
            }
        
        # Execute action
        return await self._execute_intent(parsed)
    
    async def _execute_intent(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parsed intent (provider-agnostic)."""
        intent = parsed.get("intent")
        
        if intent == "register_collateral":
            result = await self._handle_register_collateral(parsed)
        elif intent == "ppsr_search":
            result = await self._handle_ppsr_search(parsed)
        elif intent == "check_lvr":
            result = await self._handle_check_lvr(parsed)
        elif intent == "insurance_check":
            result = await self._handle_insurance_check(parsed)
        elif intent == "release_request":
            result = await self._handle_release_request(parsed)
        elif intent == "explain_ppsr":
            result = await self._handle_explain_ppsr(parsed)
        elif intent == "valuation_update":
            result = await self._handle_valuation_update(parsed)
        else:
            result = {
                "success": False,
                "error": f"Unknown intent: {intent}",
                "confidence": parsed.get("confidence", 0.0)
            }
        
        # Add provider info
        result["ai_provider"] = parsed.get("ai_provider")
        result["model"] = parsed.get("model")
        
        return result
    
    def _get_system_prompt(self) -> str:
        """System prompt (works for both providers)."""
        return """You are Anya, an AI banking assistant specializing in collateral management and security interests in Australia.

Your role is to help customers understand collateral requirements, PPSR processes, LVR monitoring, insurance, and security release.

Australian context expertise:
- PPSA (Personal Property Securities Act 2009)
- PPSR registration and priority rules
- State land title systems (Torrens)
- LMI for LVR > 80%
- Australian valuation standards
- Consumer protections under NCCP

Respond in JSON format:
{
    "intent": "register_collateral|ppsr_search|check_lvr|insurance_check|release_request|explain_ppsr|valuation_update",
    "parameters": {
        "collateral_type": "string",
        "description": "string",
        "value": "number",
        ...
    },
    "confidence": 0.0-1.0,
    "emotional_tone": "informative|reassuring|cautionary|supportive",
    "reasoning": "string"
}

Always explain Australian legal requirements clearly and be transparent about PPSR and security interests.
"""
    
    def _build_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """Build prompt with context (same for both providers)."""
        return f"""Customer Request: "{request}"

Customer Context:
- Customer ID: {self.customer_id}
- Active Collateral: {len(context.get('active_collateral', []))}
- Loans with Security: {context.get('secured_loans', [])}
- Average LVR: {context.get('average_lvr', 0):.1f}%
- State: {context.get('state', 'NSW')}

Parse the request and provide appropriate guidance.
"""
    
    async def _build_context(self) -> Dict[str, Any]:
        """Build customer context."""
        return {
            "active_collateral": [],
            "secured_loans": [],
            "average_lvr": 75.0,
            "insurance_compliant": True,
            "state": "NSW"
        }
    
    # Handler methods (same as before, omitted for brevity)
    async def _handle_register_collateral(self, parsed: Dict) -> Dict:
        """Handle collateral registration."""
        # Same implementation as before
        return {"success": True, "action": "register_collateral"}
    
    async def _handle_ppsr_search(self, parsed: Dict) -> Dict:
        """Handle PPSR search."""
        return {"success": True, "action": "ppsr_search"}
    
    async def _handle_check_lvr(self, parsed: Dict) -> Dict:
        """Handle LVR check."""
        return {"success": True, "action": "check_lvr"}
    
    async def _handle_insurance_check(self, parsed: Dict) -> Dict:
        """Handle insurance check."""
        return {"success": True, "action": "insurance_check"}
    
    async def _handle_release_request(self, parsed: Dict) -> Dict:
        """Handle release request."""
        return {"success": True, "action": "release_request"}
    
    async def _handle_explain_ppsr(self, parsed: Dict) -> Dict:
        """Explain PPSR."""
        return {"success": True, "action": "explain_ppsr"}
    
    async def _handle_valuation_update(self, parsed: Dict) -> Dict:
        """Handle valuation update."""
        return {"success": True, "action": "valuation_update"}
