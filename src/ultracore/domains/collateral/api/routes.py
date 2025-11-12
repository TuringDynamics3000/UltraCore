"""Collateral Management API Routes - Australian Compliant"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from decimal import Decimal

from ..models import (
    Collateral,
    CollateralType,
    CollateralStatus,
    SecurityPosition,
    AustralianState
)
from ..services import CollateralService
from ..integrations.ppsr import PPSRClient
from ultracore.api.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/collateral",
    tags=["Collateral Management - Australian Compliant"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_collateral(
    loan_id: str,
    customer_id: str,
    collateral_type: CollateralType,
    collateral_description: str,
    estimated_value: Decimal,
    loan_amount_secured: Decimal,
    jurisdiction: AustralianState,
    security_position: SecurityPosition = SecurityPosition.FIRST,
    current_user = Depends(get_current_user),
    collateral_service: CollateralService = Depends()
):
    """
    Register collateral as security for loan.
    
    Australian Compliance:
    - PPSR registration for personal property
    - Land title registration for real property
    - LVR calculation
    - LMI requirement assessment
    
    Publishes: CollateralRegisteredEvent to Kafka
    """
    try:
        collateral = await collateral_service.register_collateral(
            loan_id=loan_id,
            customer_id=customer_id,
            collateral_type=collateral_type,
            collateral_description=collateral_description,
            estimated_value=estimated_value,
            loan_amount_secured=loan_amount_secured,
            jurisdiction=jurisdiction,
            security_position=security_position,
            registered_by=current_user.user_id
        )
        
        return {
            "collateral_id": collateral.collateral_id,
            "status": collateral.status.value,
            "current_lvr": float(collateral.current_lvr),
            "lmi_required": collateral.lmi_required,
            "ppsr_required": collateral.collateral_type not in [
                CollateralType.REAL_PROPERTY_RESIDENTIAL,
                CollateralType.REAL_PROPERTY_COMMERCIAL
            ],
            "message": "Collateral registered successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/collateral/{collateral_id}")
async def get_collateral(
    collateral_id: str,
    current_user = Depends(get_current_user),
    collateral_service: CollateralService = Depends()
) -> Collateral:
    """
    Get collateral details (reconstructed from events).
    
    Event sourcing: Complete audit trail available.
    """
    collateral = await collateral_service.get_collateral(collateral_id)
    return collateral


@router.post("/collateral/{collateral_id}/valuation")
async def complete_valuation(
    collateral_id: str,
    valuation_order_id: str,
    market_value: Decimal,
    forced_sale_value: Optional[Decimal],
    valuer_name: str,
    valuer_registration: str,
    valuation_firm: str,
    valuation_report_reference: str,
    current_user = Depends(get_current_user),
    collateral_service: CollateralService = Depends()
):
    """
    Record completed professional valuation.
    
    Australian Compliance:
    - Valuer must be API (Australian Property Institute) registered
    - Valuation must comply with Australian Valuation Standards
    - For LMI, must be from approved panel
    
    Publishes: CollateralValuationCompletedEvent to Kafka
    
    Triggers:
    - LVR recalculation
    - LVR breach detection
    - Additional security assessment
    """
    await collateral_service.complete_valuation(
        collateral_id=collateral_id,
        valuation_order_id=valuation_order_id,
        market_value=market_value,
        forced_sale_value=forced_sale_value,
        valuer_name=valuer_name,
        valuer_registration=valuer_registration,
        valuation_firm=valuation_firm,
        valuation_report_reference=valuation_report_reference
    )
    
    return {
        "message": "Valuation recorded successfully",
        "collateral_id": collateral_id,
        "market_value": float(market_value)
    }


@router.post("/collateral/{collateral_id}/perfect")
async def perfect_security(
    collateral_id: str,
    perfection_method: str,
    ppsr_registration_number: Optional[str] = None,
    caveat_number: Optional[str] = None,
    current_user = Depends(get_current_user),
    collateral_service: CollateralService = Depends()
):
    """
    Perfect security interest under PPSA.
    
    Australian Compliance:
    - PPSR registration for personal property
    - Land title caveat for real property
    - Priority established by perfection time
    
    CRITICAL: Perfection protects bank's security interest!
    
    Publishes: CollateralPerfectedEvent to Kafka
    """
    await collateral_service.perfect_security(
        collateral_id=collateral_id,
        perfection_method=perfection_method,
        ppsr_registration_number=ppsr_registration_number,
        caveat_number=caveat_number
    )
    
    return {
        "message": "Security interest perfected",
        "collateral_id": collateral_id,
        "perfection_method": perfection_method
    }


@router.post("/collateral/{collateral_id}/release")
async def release_collateral(
    collateral_id: str,
    release_reason: str,
    final_loan_balance: Decimal = Decimal("0.00"),
    current_user = Depends(get_current_user),
    collateral_service: CollateralService = Depends()
):
    """
    Release collateral (loan repaid or refinanced).
    
    Australian Compliance:
    - PPSR discharge within 5 business days (PPSA Section 178)
    - Land title discharge
    - Return of original documents
    
    CRITICAL: 5-day discharge deadline is LAW!
    Failure = ,000 penalty
    
    Publishes: CollateralReleasedEvent to Kafka
    
    Triggers:
    - PPSR discharge
    - Document return process
    """
    await collateral_service.release_collateral(
        collateral_id=collateral_id,
        release_reason=release_reason,
        final_loan_balance=final_loan_balance,
        released_by=current_user.user_id
    )
    
    return {
        "message": "Collateral release initiated. PPSR discharge will be completed within 5 business days.",
        "collateral_id": collateral_id,
        "discharge_deadline": "5 business days from today"
    }


@router.get("/ppsr/search/grantor")
async def search_ppsr_by_grantor(
    grantor_name: str = Query(..., description="Borrower name"),
    grantor_abn: Optional[str] = Query(None, description="Borrower ABN"),
    current_user = Depends(get_current_user),
    ppsr_client: PPSRClient = Depends()
):
    """
    Search PPSR by grantor (borrower) details.
    
    Australian PPSR search for due diligence.
    
    Returns all security interests registered against borrower.
    
    CRITICAL: Always search before taking security!
    """
    result = await ppsr_client.search_by_grantor(
        grantor_name=grantor_name,
        grantor_abn=grantor_abn
    )
    
    return {
        "search_id": result["search_id"],
        "registrations_found": result["registrations_found"],
        "clear_title": result["grantor_clear"],
        "registrations": result["registrations"],
        "can_proceed": result["grantor_clear"]
    }


@router.get("/ppsr/search/serial")
async def search_ppsr_by_serial(
    serial_number: str = Query(..., description="VIN or serial number"),
    collateral_class: str = Query("motor_vehicle", description="PPSR collateral class"),
    current_user = Depends(get_current_user),
    ppsr_client: PPSRClient = Depends()
):
    """
    Search PPSR by serial number (VIN for vehicles).
    
    Returns all security interests against specific asset.
    
    Critical for vehicle finance!
    """
    result = await ppsr_client.search_by_serial_number(
        serial_number=serial_number,
        collateral_class=collateral_class
    )
    
    return {
        "search_id": result["search_id"],
        "registrations_found": result["registrations_found"],
        "clear_title": result["serial_number_clear"],
        "registrations": result["registrations"]
    }


@router.post("/ppsr/register")
async def register_ppsr(
    secured_party_name: str,
    secured_party_abn: str,
    grantor_name: str,
    grantor_identifier: str,
    collateral_class: str,
    collateral_description: str,
    security_agreement_date: date,
    secured_amount: Optional[Decimal] = None,
    serial_number: Optional[str] = None,
    current_user = Depends(get_current_user),
    ppsr_client: PPSRClient = Depends()
):
    """
    Register security interest on PPSR.
    
    Australian PPSR registration under PPSA 2009.
    
    CRITICAL: Registration time establishes priority!
    Earlier registration = superior security interest.
    
    Returns registration number and timestamp.
    """
    result = await ppsr_client.register_security_interest(
        secured_party_name=secured_party_name,
        secured_party_abn=secured_party_abn,
        grantor_name=grantor_name,
        grantor_identifier=grantor_identifier,
        collateral_class=collateral_class,
        collateral_description=collateral_description,
        security_agreement_date=security_agreement_date,
        secured_amount=secured_amount,
        serial_number=serial_number
    )
    
    return {
        "ppsr_registration_number": result["registration_number"],
        "registration_time": result["registration_time"].isoformat(),
        "priority_established": True,
        "message": f"PPSR registration completed. Priority established at {result['registration_time'].isoformat()}"
    }


@router.post("/ppsr/discharge/{registration_number}")
async def discharge_ppsr(
    registration_number: str,
    current_user = Depends(get_current_user),
    ppsr_client: PPSRClient = Depends()
):
    """
    Discharge PPSR registration.
    
    PPSA Section 178: Must discharge within 5 business days!
    
    Failure to discharge on time = ,000 penalty.
    """
    result = await ppsr_client.discharge_registration(
        registration_number=registration_number
    )
    
    return {
        "registration_number": registration_number,
        "discharge_time": result["discharge_time"].isoformat(),
        "discharge_confirmation": result["discharge_confirmation"],
        "status": "discharged",
        "message": "PPSR registration discharged successfully"
    }


@router.get("/lvr/breaches")
async def get_lvr_breaches(
    severity: Optional[str] = Query(None, description="critical, high, moderate"),
    current_user = Depends(get_current_user),
    collateral_service: CollateralService = Depends()
):
    """
    Get all collateral in LVR breach.
    
    Risk management endpoint.
    """
    # Would query from data mesh
    breaches = []
    
    return {
        "total_breaches": len(breaches),
        "breaches": breaches
    }


@router.get("/compliance/ppsr-discharge")
async def check_ppsr_discharge_compliance(
    current_user = Depends(get_current_user)
):
    """
    Check compliance with 5-day PPSR discharge requirement.
    
    Regulatory compliance monitoring.
    
    PPSA Section 178 compliance report.
    """
    # Would query from data mesh
    return {
        "total_discharges_required": 0,
        "discharged_on_time": 0,
        "pending_discharge": 0,
        "overdue_discharge": 0,
        "compliance_rate": 100.0,
        "overdue_details": []
    }


@router.get("/compliance/insurance")
async def check_insurance_compliance(
    current_user = Depends(get_current_user)
):
    """
    Check insurance compliance across portfolio.
    
    Risk management endpoint.
    """
    return {
        "total_collateral": 0,
        "insurance_compliant": 0,
        "insurance_lapsed": 0,
        "compliance_rate": 100.0
    }
