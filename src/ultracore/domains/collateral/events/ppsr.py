"""PPSR (Personal Property Securities Register) Events - Australian Specific"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal, List, Dict, Any
from pydantic import Field

from .base import CollateralEvent


class PPSRRegistrationCompletedEvent(CollateralEvent):
    """
    Event: PPSR registration completed successfully.
    
    PPSR is Australia's national online register for security interests
    in personal property (everything except land).
    
    Critical: Registration time establishes priority!
    
    PPSA Reference: Section 21 (Perfection), Section 55 (Priority)
    """
    
    event_type: str = "PPSRRegistrationCompleted"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    # PPSR registration details
    ppsr_registration_number: str = Field(..., description="Unique 16-digit registration number")
    registration_time: datetime = Field(..., description="CRITICAL: Establishes priority")
    
    # Secured party (lender)
    secured_party_name: str
    secured_party_abn: Optional[str] = None
    secured_party_acn: Optional[str] = None
    
    # Grantor (borrower)
    grantor_name: str
    grantor_type: Literal["individual", "company", "trust", "partnership"]
    grantor_abn: Optional[str] = None
    grantor_acn: Optional[str] = None
    
    # Collateral description
    collateral_class: Literal[
        "motor_vehicle",
        "watercraft",
        "aircraft",
        "agricultural",
        "all_present_and_after_acquired_property",
        "all_present_property",
        "accounts",
        "crops",
        "negotiable_instruments",
        "inventory",
        "other"
    ]
    
    collateral_description: str
    serial_numbered: bool = False
    serial_number: Optional[str] = None
    
    # Security agreement
    security_agreement_date: date
    secured_amount: Optional[Decimal] = Field(
        None,
        description="Can be omitted for 'all obligations' security"
    )
    
    # Registration period
    registration_start_date: date
    registration_end_date: Optional[date] = Field(
        None,
        description="If None, registration is perpetual (for companies)"
    )
    
    # Subordination (if applicable)
    subordinated_to_registration: Optional[str] = Field(
        None,
        description="PPSR registration number of superior security interest"
    )
    
    registered_by: str
    registered_at: datetime
    
    # Compliance verification
    ppsa_compliant: bool = True
    registration_verified: bool = True


class PPSRSearchCompletedEvent(CollateralEvent):
    """
    Event: PPSR search completed before taking security.
    
    Critical for due diligence:
    - Identifies existing security interests
    - Establishes priority position
    - Detects fraud risk
    
    Best practice: Search immediately before registration
    """
    
    event_type: str = "PPSRSearchCompleted"
    
    search_id: str
    search_type: Literal[
        "grantor_search",  # Search by borrower details
        "serial_number_search",  # Search by VIN, etc.
        "registration_number_search"  # Search by PPSR registration number
    ]
    
    # Search criteria
    search_criteria: Dict[str, Any]
    search_date: datetime
    
    # Search results
    registrations_found: int
    existing_securities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of existing PPSR registrations"
    )
    
    # Risk assessment
    prior_secured_parties: List[str] = Field(default_factory=list)
    expected_priority_position: Literal["first", "second", "third", "subsequent"]
    
    # Red flags
    red_flags_detected: bool = False
    red_flags: List[str] = Field(
        default_factory=list,
        description="e.g., Multiple recent registrations, Serial number mismatches"
    )
    
    # Recommendations
    proceed_with_registration: bool = True
    additional_diligence_required: bool = False
    
    searched_by: str
    searched_at: datetime


class PPSRDischargeRequestedEvent(CollateralEvent):
    """
    Event: PPSR discharge requested (loan repaid).
    
    PPSA Requirement: Must discharge within 5 business days
    of being requested by debtor (Section 178).
    
    Failure to discharge on time = ,000 penalty!
    """
    
    event_type: str = "PPSRDischargeRequested"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    ppsr_registration_number: str
    discharge_reason: Literal[
        "loan_fully_repaid",
        "security_released",
        "error_in_registration",
        "court_order"
    ]
    
    requested_by: str
    requested_at: datetime
    
    # PPSA compliance deadline
    discharge_deadline: datetime = Field(
        ...,
        description="5 business days from request (PPSA Section 178)"
    )
    
    # Verification
    final_loan_balance: Decimal
    all_obligations_satisfied: bool = True


class PPSRDischargeCompletedEvent(CollateralEvent):
    """
    Event: PPSR discharge completed.
    
    Registration removed from PPSR.
    Borrower's credit file updated.
    """
    
    event_type: str = "PPSRDischargeCompleted"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    ppsr_registration_number: str
    discharge_time: datetime
    
    # Compliance
    discharged_within_deadline: bool = True
    days_to_discharge: int
    
    # Confirmation
    discharge_confirmation_number: str
    discharge_certificate_issued: bool = True
    
    discharged_by: str
    discharged_at: datetime


class PPSRPriorityChangedEvent(CollateralEvent):
    """
    Event: Priority position changed on PPSR.
    
    Can occur due to:
    - Subordination agreement
    - New superior registration
    - Amendment to registration
    - Court order
    
    Critical for risk assessment!
    """
    
    event_type: str = "PPSRPriorityChanged"
    regulatory_event: bool = True
    ppsr_relevant: bool = True
    
    ppsr_registration_number: str
    
    # Priority change
    previous_priority: Literal["first", "second", "third", "subsequent"]
    new_priority: Literal["first", "second", "third", "subsequent"]
    
    change_reason: Literal[
        "subordination_agreement",
        "new_superior_registration",
        "amendment",
        "court_order",
        "discharge_of_prior"
    ]
    
    # New superior party (if applicable)
    superior_registration_number: Optional[str] = None
    superior_party_name: Optional[str] = None
    
    # Risk impact
    security_position_weakened: bool = False
    additional_security_required: bool = False
    
    # ML context
    ml_risk_score_before: Optional[float] = None
    ml_risk_score_after: Optional[float] = None
    
    detected_at: datetime
