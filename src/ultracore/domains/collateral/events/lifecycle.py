"""Collateral Lifecycle Events - Australian Compliant"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal, List, Dict, Any
from pydantic import Field

from .base import CollateralEvent


class CollateralRegisteredEvent(CollateralEvent):
    """
    Event: Collateral registered against loan.
    
    Australian Compliance:
    - Must specify collateral type and jurisdiction
    - Real property requires land title details
    - Motor vehicles require VIN and registration
    - Equipment requires serial numbers
    - Must comply with PPSA for perfection
    
    Triggers:
    - PPSR registration (for personal property)
    - Land title search (for real property)
    - Valuation ordering
    - Insurance requirement setup
    - LVR calculation
    """
    
    event_type: str = "CollateralRegistered"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    # Collateral identification
    collateral_type: Literal[
        "real_property_residential",
        "real_property_commercial",
        "motor_vehicle",
        "equipment",
        "inventory",
        "accounts_receivable",
        "intellectual_property",
        "shares",
        "other_ppsa_property"
    ]
    
    collateral_description: str
    
    # Real property details (if applicable)
    property_address: Optional[str] = None
    title_reference: Optional[str] = None  # e.g., "Lot 10 DP 12345"
    certificate_of_title: Optional[str] = None
    land_registry_office: Optional[str] = Field(
        None,
        description="State land registry: NSW LRS, Land Use Victoria, etc."
    )
    zoning: Optional[str] = None
    land_area_sqm: Optional[Decimal] = None
    
    # Motor vehicle details (if applicable)
    vehicle_vin: Optional[str] = Field(None, description="Vehicle Identification Number")
    vehicle_registration: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    
    # Equipment details (if applicable)
    equipment_serial_number: Optional[str] = None
    equipment_manufacturer: Optional[str] = None
    equipment_model: Optional[str] = None
    
    # Valuation
    estimated_value: Decimal = Field(..., description="Initial estimated value AUD")
    valuation_date: date
    valuation_method: Literal["professional", "automated", "desktop", "self_declared"]
    
    # Loan security
    security_position: Literal["first", "second", "third", "unsecured"]
    loan_amount_secured: Decimal
    required_lvr: Decimal = Field(..., description="Required Loan-to-Value Ratio")
    current_lvr: Decimal = Field(..., description="Current LVR")
    
    # Insurance
    insurance_required: bool = True
    insurance_type: Optional[str] = Field(None, description="Comprehensive, Third Party, etc.")
    insurance_minimum_amount: Optional[Decimal] = None
    
    # Registered by
    registered_by: str
    registered_at: datetime
    
    # Australian compliance flags
    ppsr_required: bool = Field(
        ...,
        description="Whether PPSR registration required (personal property only)"
    )
    lmi_required: bool = Field(
        False,
        description="Lenders Mortgage Insurance required (typically LVR > 80%)"
    )


class CollateralValuationOrderedEvent(CollateralEvent):
    """
    Event: Professional valuation ordered.
    
    Australian Compliance:
    - Must use Australian Certified Practising Valuer (CPV)
    - Must comply with Australian Valuation Standards
    - For residential property >, independent valuation mandatory
    - For LMI, valuer must be from approved panel
    """
    
    event_type: str = "CollateralValuationOrderedEvent"
    
    valuation_order_id: str
    valuation_firm: str
    valuer_name: Optional[str] = None
    valuer_registration: str = Field(..., description="API (Australian Property Institute) number")
    
    valuation_purpose: Literal[
        "loan_origination",
        "loan_review",
        "lmi_requirement",
        "forced_sale",
        "insurance",
        "regulatory"
    ]
    
    valuation_type: Literal[
        "full_inspection",
        "desktop",
        "kerbside",
        "automated_valuation_model"
    ]
    
    estimated_completion_date: date
    ordered_by: str
    ordered_at: datetime
    
    # Compliance
    australian_valuation_standards_applicable: List[str] = Field(
        default_factory=list,
        description="e.g., ['RICS', 'API', 'IVS']"
    )


class CollateralValuationCompletedEvent(CollateralEvent):
    """
    Event: Professional valuation completed.
    
    Triggers:
    - LVR recalculation
    - LMI requirement assessment
    - Loan approval decision
    - Collateral adequacy review
    - ML: Valuation accuracy prediction
    """
    
    event_type: str = "CollateralValuationCompleted"
    regulatory_event: bool = True
    
    valuation_order_id: str
    valuation_report_reference: str
    
    # Valuation results
    market_value: Decimal = Field(..., description="Market value in AUD")
    forced_sale_value: Optional[Decimal] = Field(
        None,
        description="Estimated value in forced sale scenario (typically 70-80% of market)"
    )
    
    valuation_date: date
    valuation_effective_date: date
    valuation_expiry_date: date = Field(
        ...,
        description="Typically 90 days for property, 30 days for vehicles"
    )
    
    # Valuer details
    valuer_name: str
    valuer_registration: str
    valuation_firm: str
    
    # Previous valuation comparison
    previous_value: Optional[Decimal] = None
    value_change_percentage: Optional[Decimal] = None
    value_change_reason: Optional[str] = None
    
    # LVR impact
    new_lvr: Decimal
    lvr_breach: bool = Field(False, description="Whether LVR now exceeds policy limit")
    
    # Additional security required
    additional_security_required: bool = False
    additional_security_amount: Optional[Decimal] = None
    
    # Valuation quality indicators
    confidence_level: Literal["high", "medium", "low"]
    market_conditions: str
    comparable_sales_count: Optional[int] = None
    
    completed_at: datetime


class CollateralPerfectedEvent(CollateralEvent):
    """
    Event: Security interest perfected under PPSA.
    
    Australian Compliance:
    - PPSR registration completed for personal property
    - Land title caveat lodged for real property
    - Priority established
    - Perfection gives priority over unperfected interests
    
    Critical for enforcement rights!
    """
    
    event_type: str = "CollateralPerfected"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    perfection_method: Literal[
        "ppsr_registration",  # Personal property
        "title_caveat",  # Real property
        "possession",  # Physical possession
        "control"  # e.g., bank accounts
    ]
    
    # PPSR details (if applicable)
    ppsr_registration_number: Optional[str] = None
    ppsr_registration_time: Optional[datetime] = None
    ppsr_security_agreement_date: date
    
    # Land title details (if applicable)
    caveat_number: Optional[str] = None
    caveat_lodgement_date: Optional[date] = None
    dealing_number: Optional[str] = None
    
    # Priority
    priority_position: Literal["first", "second", "third", "subsequent"]
    prior_encumbrances: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of any prior security interests"
    )
    
    # Perfection confirmation
    perfected_by: str
    perfected_at: datetime
    legal_advice_obtained: bool = Field(
        False,
        description="Whether legal advice obtained for complex securities"
    )


class CollateralReleasedEvent(CollateralEvent):
    """
    Event: Collateral released (loan repaid or refinanced).
    
    Australian Compliance:
    - PPSR discharge within 5 business days (PPSA requirement)
    - Land title discharge/withdrawal of caveat
    - Return of original documents
    - Final discharge statement
    
    Triggers:
    - PPSR discharge
    - Land title discharge
    - Insurance cancellation
    - Document return
    """
    
    event_type: str = "CollateralReleased"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    release_reason: Literal[
        "loan_repaid",
        "loan_refinanced",
        "collateral_substituted",
        "security_no_longer_required",
        "borrower_request"
    ]
    
    # Loan details
    final_loan_balance: Decimal
    release_date: date
    
    # PPSR discharge
    ppsr_discharge_requested: bool = False
    ppsr_discharge_completed: bool = False
    ppsr_discharge_date: Optional[date] = None
    
    # Land title discharge
    title_discharge_lodged: bool = False
    title_discharge_completed: bool = False
    
    # Documents returned
    original_title_returned: bool = False
    other_documents_returned: List[str] = Field(default_factory=list)
    
    # Final discharge
    discharge_statement_issued: bool = False
    discharge_statement_date: Optional[date] = None
    
    released_by: str
    released_at: datetime


class CollateralSeizedEvent(CollateralEvent):
    """
    Event: Collateral seized due to default.
    
    Australian Compliance:
    - Must comply with PPSA Part 4 (Enforcement)
    - Notice requirements (Section 130 PPSA)
    - Debtor rights under PPSA
    - Consumer protections under NCCP
    - Must follow state-specific procedures for real property
    
    Triggers:
    - Legal notification requirements
    - Valuation for forced sale
    - Asset disposal process
    - Regulatory reporting (ASIC)
    """
    
    event_type: str = "CollateralSeized"
    regulatory_event: bool = True
    
    seizure_reason: Literal[
        "payment_default",
        "covenant_breach",
        "fraud_detected",
        "unauthorized_disposal",
        "insolvency"
    ]
    
    # Default details
    days_in_default: int
    outstanding_amount: Decimal
    
    # Legal process
    notice_issued: bool = True
    notice_date: date
    notice_method: Literal["registered_mail", "personal_service", "email", "sms"]
    
    # PPSA Section 130 notice
    section_130_notice_issued: bool = True
    section_130_notice_date: date
    debtor_redemption_period_days: int = Field(
        15,
        description="Minimum 15 business days under PPSA"
    )
    redemption_deadline: date
    
    # Seizure execution
    seizure_date: date
    seizure_method: Literal[
        "voluntary_surrender",
        "repossession",
        "court_order",
        "receiver_appointed"
    ]
    
    # Asset condition
    asset_condition: Literal["excellent", "good", "fair", "poor", "damaged"]
    asset_location: str
    
    # Forced sale valuation
    forced_sale_valuation_ordered: bool = True
    estimated_forced_sale_value: Optional[Decimal] = None
    
    # Consumer protections
    hardship_notice_provided: bool = Field(
        True,
        description="Under NCCP, must inform of hardship options"
    )
    financial_counselling_offered: bool = True
    
    seized_by: str
    seized_at: datetime
