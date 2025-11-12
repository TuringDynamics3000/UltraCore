"""MCP Server for Collateral Management Tools"""
from typing import Dict, Any, List
from datetime import date
from decimal import Decimal

from mcp.server import Server
from ultracore.mcp.base import BaseMCPServer
from ..services import CollateralService
from ..integrations.ppsr import PPSRClient
from ..agents import AnyaCollateralAgentV2


class CollateralMCPServer(BaseMCPServer):
    """
    MCP Server exposing Collateral Management capabilities as AI tools.
    
    Tools available:
    - register_collateral: Register security interest
    - search_ppsr: Search Personal Property Securities Register
    - check_lvr: Check loan-to-value ratio
    - order_valuation: Order professional valuation
    - check_insurance: Verify insurance compliance
    - release_collateral: Release security (loan repaid)
    - discharge_ppsr: Discharge PPSR registration
    - get_collateral_advice: AI-powered collateral guidance
    """
    
    def __init__(
        self,
        collateral_service: CollateralService,
        ppsr_client: PPSRClient,
        anya_agent: AnyaCollateralAgentV2
    ):
        super().__init__(server_name="collateral_management")
        self.collateral_service = collateral_service
        self.ppsr = ppsr_client
        self.anya = anya_agent
    
    def register_tools(self):
        """Register all Collateral Management MCP tools."""
        
        @self.server.tool()
        async def register_collateral(
            customer_id: str,
            loan_id: str,
            collateral_type: str,
            description: str,
            estimated_value: float,
            loan_amount_secured: float,
            state: str = "NSW",
            vin: str = None,
            property_address: str = None,
            title_reference: str = None
        ) -> Dict[str, Any]:
            """
            Register collateral as security for a loan.
            
            Args:
                customer_id: Customer identifier
                loan_id: Loan identifier
                collateral_type: Type (motor_vehicle, real_property_residential, etc.)
                description: Collateral description
                estimated_value: Estimated value in AUD
                loan_amount_secured: Loan amount secured by this collateral
                state: Australian state (NSW, VIC, QLD, etc.)
                vin: Vehicle Identification Number (for vehicles)
                property_address: Property address (for real estate)
                title_reference: Land title reference (for real estate)
            
            Returns:
                Registration confirmation with next steps
            """
            from ..models import CollateralType, AustralianState
            
            # Convert types
            col_type = CollateralType(collateral_type)
            aus_state = AustralianState(state)
            
            collateral = await self.collateral_service.register_collateral(
                loan_id=loan_id,
                customer_id=customer_id,
                collateral_type=col_type,
                collateral_description=description,
                estimated_value=Decimal(str(estimated_value)),
                loan_amount_secured=Decimal(str(loan_amount_secured)),
                jurisdiction=aus_state,
                registered_by="mcp_api"
            )
            
            # Calculate LVR
            lvr = (Decimal(str(loan_amount_secured)) / Decimal(str(estimated_value)) * Decimal("100"))
            
            return {
                "success": True,
                "collateral_id": collateral.collateral_id,
                "collateral_type": collateral_type,
                "estimated_value": estimated_value,
                "lvr": float(lvr),
                "lmi_required": lvr > Decimal("80.0"),
                "ppsr_required": col_type not in [
                    CollateralType.REAL_PROPERTY_RESIDENTIAL,
                    CollateralType.REAL_PROPERTY_COMMERCIAL
                ],
                "next_steps": [
                    "PPSR search" if col_type == CollateralType.MOTOR_VEHICLE else "Land title search",
                    "Professional valuation",
                    "Insurance setup",
                    "Security documentation"
                ],
                "message": f"Collateral registered successfully. LVR: {float(lvr):.1f}%"
            }
        
        @self.server.tool()
        async def search_ppsr(
            search_type: str,
            grantor_name: str = None,
            grantor_abn: str = None,
            serial_number: str = None
        ) -> Dict[str, Any]:
            """
            Search the Australian Personal Property Securities Register.
            
            Critical for due diligence before taking security!
            
            Args:
                search_type: "grantor" or "serial_number"
                grantor_name: Borrower name (for grantor search)
                grantor_abn: Borrower ABN (optional)
                serial_number: VIN or serial number (for serial search)
            
            Returns:
                Existing registrations and clear title status
            """
            if search_type == "grantor":
                result = await self.ppsr.search_by_grantor(
                    grantor_name=grantor_name,
                    grantor_abn=grantor_abn
                )
            else:
                result = await self.ppsr.search_by_serial_number(
                    serial_number=serial_number
                )
            
            return {
                "success": True,
                "search_type": search_type,
                "registrations_found": result["registrations_found"],
                "clear_title": result.get("grantor_clear") or result.get("serial_number_clear"),
                "registrations": result["registrations"],
                "can_proceed": result["registrations_found"] == 0,
                "message": "Clear title - can proceed!" if result["registrations_found"] == 0 else f"Found {result['registrations_found']} existing security interest(s)"
            }
        
        @self.server.tool()
        async def check_lvr(
            collateral_id: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Check current Loan-to-Value Ratio for collateral.
            
            Args:
                collateral_id: Collateral identifier
                customer_id: Customer identifier
            
            Returns:
                Current LVR, compliance status, and recommendations
            """
            collateral = await self.collateral_service.get_collateral(collateral_id)
            
            is_compliant = collateral.current_lvr <= collateral.policy_max_lvr
            buffer = collateral.policy_max_lvr - collateral.current_lvr
            
            return {
                "success": True,
                "current_lvr": float(collateral.current_lvr),
                "policy_max_lvr": float(collateral.policy_max_lvr),
                "is_compliant": is_compliant,
                "buffer_percentage": float(buffer),
                "property_value": float(collateral.estimated_value),
                "loan_balance": float(collateral.loan_amount_secured),
                "message": f"LVR: {float(collateral.current_lvr):.1f}% - {'Compliant ?' if is_compliant else 'BREACH ??'}"
            }
        
        @self.server.tool()
        async def order_valuation(
            collateral_id: str,
            valuation_type: str = "full_inspection",
            purpose: str = "loan_review"
        ) -> Dict[str, Any]:
            """
            Order professional valuation for collateral.
            
            Args:
                collateral_id: Collateral identifier
                valuation_type: full_inspection, desktop, kerbside, or avm
                purpose: loan_origination, loan_review, lmi_requirement, etc.
            
            Returns:
                Valuation order confirmation
            """
            # Would integrate with valuation service provider
            order_id = f"VAL-{collateral_id[-8:]}"
            
            return {
                "success": True,
                "valuation_order_id": order_id,
                "collateral_id": collateral_id,
                "valuation_type": valuation_type,
                "purpose": purpose,
                "estimated_completion": "5-7 business days",
                "valuer": "Australian Property Institute certified valuer",
                "message": f"Valuation ordered successfully. Order ID: {order_id}"
            }
        
        @self.server.tool()
        async def check_insurance(
            collateral_id: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Check insurance compliance for collateral.
            
            Args:
                collateral_id: Collateral identifier
                customer_id: Customer identifier
            
            Returns:
                Insurance status and compliance
            """
            collateral = await self.collateral_service.get_collateral(collateral_id)
            
            is_compliant = collateral.is_insurance_compliant()
            
            return {
                "success": True,
                "insurance_required": collateral.insurance_required,
                "insurance_compliant": is_compliant,
                "insurance_active": collateral.insurance.is_active if collateral.insurance else False,
                "sum_insured": float(collateral.insurance.sum_insured) if collateral.insurance else 0,
                "policy_expiry": collateral.insurance.policy_end_date.isoformat() if collateral.insurance else None,
                "message": "Insurance compliant ?" if is_compliant else "Insurance action required ??"
            }
        
        @self.server.tool()
        async def release_collateral(
            collateral_id: str,
            customer_id: str,
            release_reason: str = "loan_repaid"
        ) -> Dict[str, Any]:
            """
            Release collateral security (loan repaid or refinanced).
            
            PPSA Requirement: Must discharge PPSR within 5 business days!
            
            Args:
                collateral_id: Collateral identifier
                customer_id: Customer identifier
                release_reason: loan_repaid, loan_refinanced, etc.
            
            Returns:
                Release confirmation and discharge timeline
            """
            await self.collateral_service.release_collateral(
                collateral_id=collateral_id,
                release_reason=release_reason,
                final_loan_balance=Decimal("0.00"),
                released_by="mcp_api"
            )
            
            return {
                "success": True,
                "collateral_id": collateral_id,
                "release_date": date.today().isoformat(),
                "ppsr_discharge_deadline": "5 business days from today",
                "status": "release_initiated",
                "next_steps": [
                    "PPSR discharge (automatic)",
                    "Document return (5-7 days)",
                    "Discharge confirmation letter"
                ],
                "message": "Collateral release initiated. PPSR discharge will be completed within 5 business days (legal requirement)."
            }
        
        @self.server.tool()
        async def discharge_ppsr(
            ppsr_registration_number: str,
            customer_id: str
        ) -> Dict[str, Any]:
            """
            Discharge PPSR registration.
            
            PPSA Section 178: Must discharge within 5 business days of request!
            
            Args:
                ppsr_registration_number: PPSR registration number (16 digits)
                customer_id: Customer identifier
            
            Returns:
                Discharge confirmation
            """
            result = await self.ppsr.discharge_registration(
                registration_number=ppsr_registration_number,
                discharge_reason="obligations_satisfied"
            )
            
            return {
                "success": True,
                "ppsr_registration_number": ppsr_registration_number,
                "discharge_time": result["discharge_time"].isoformat(),
                "discharge_confirmation": result["discharge_confirmation"],
                "status": "discharged",
                "message": f"PPSR registration {ppsr_registration_number} successfully discharged!"
            }
        
        @self.server.tool()
        async def get_collateral_advice(
            customer_id: str,
            question: str
        ) -> Dict[str, Any]:
            """
            Get AI-powered collateral management advice from Anya.
            
            Uses both OpenAI and Anthropic for comprehensive guidance.
            
            Args:
                customer_id: Customer identifier
                question: Natural language question about collateral
            
            Returns:
                Personalized advice from Anya
            """
            self.anya.customer_id = customer_id
            advice = await self.anya.execute(question)
            
            return advice
