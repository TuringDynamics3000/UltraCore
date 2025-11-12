"""Hardship Events - Australian NCCP Compliant"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal, List, Dict, Any
from pydantic import Field

from .base import LoanRestructuringEvent


class HardshipApplicationSubmittedEvent(LoanRestructuringEvent):
    """
    Event: Customer submits hardship application.
    
    Australian NCCP Section 72: Lenders must consider hardship variations.
    
    Triggers:
    - Assessment workflow
    - Financial counselling offer
    - Anya empathetic support
    - ML: Predict likelihood of success
    - Regulatory notification (ASIC)
    """
    
    event_type: str = "HardshipApplicationSubmitted"
    regulatory_event: bool = True
    asic_reportable: bool = True
    hardship_case: bool = True
    
    application_id: str
    
    # Hardship details
    hardship_reason: Literal[
        "job_loss",
        "reduced_income",
        "illness_injury",
        "family_breakdown",
        "business_failure",
        "natural_disaster",
        "other"
    ]
    
    hardship_description: str
    financial_impact_description: str
    
    # Financial situation
    current_income_monthly: Decimal
    essential_expenses_monthly: Decimal
    other_debts_monthly: Decimal
    disposable_income_monthly: Decimal
    
    # Current loan
    current_payment_amount: Decimal
    current_arrears_amount: Decimal = Decimal("0.00")
    days_in_arrears: int = 0
    
    # Requested assistance
    requested_relief_type: List[str] = Field(
        default_factory=list,
        description="payment_holiday, term_extension, rate_reduction, payment_reduction"
    )
    
    requested_duration_months: Optional[int] = None
    can_afford_amount: Optional[Decimal] = None
    
    # Supporting documents
    documents_provided: List[str] = Field(default_factory=list)
    income_evidence_provided: bool = False
    expense_evidence_provided: bool = False
    
    # Counselling
    financial_counselling_contacted: bool = False
    counselling_reference: Optional[str] = None
    
    # Submission
    submitted_by: str
    submitted_at: datetime
    submission_channel: Literal["web", "mobile", "phone", "branch", "email"]
    
    # ML context
    ml_approval_probability: Optional[float] = None
    ml_recommended_relief: Optional[str] = None


class HardshipApplicationApprovedEvent(LoanRestructuringEvent):
    """
    Event: Hardship application approved.
    
    Australian NCCP: Must be reasonable and consider customer circumstances.
    
    Triggers:
    - Restructuring implementation
    - Payment holiday or modification
    - Customer notification (Anya)
    - Monitoring setup
    """
    
    event_type: str = "HardshipApplicationApproved"
    regulatory_event: bool = True
    asic_reportable: bool = True
    hardship_case: bool = True
    
    application_id: str
    
    # Approved relief
    approved_relief_type: str
    relief_duration_months: Optional[int] = None
    
    # Payment holiday
    payment_holiday_start_date: Optional[date] = None
    payment_holiday_end_date: Optional[date] = None
    payments_deferred: Optional[int] = None
    
    # Term extension
    original_term_months: Optional[int] = None
    new_term_months: Optional[int] = None
    new_maturity_date: Optional[date] = None
    
    # Payment reduction
    original_payment_amount: Optional[Decimal] = None
    new_payment_amount: Optional[Decimal] = None
    reduction_percentage: Optional[Decimal] = None
    
    # Rate modification
    original_interest_rate: Optional[Decimal] = None
    new_interest_rate: Optional[Decimal] = None
    rate_reduction_duration_months: Optional[int] = None
    
    # Financial impact
    total_interest_increase: Decimal = Decimal("0.00")
    total_cost_to_customer: Decimal
    
    # Conditions
    conditions: List[str] = Field(default_factory=list)
    review_date: Optional[date] = None
    
    # Approval
    approved_by: str
    approved_at: datetime
    approval_notes: Optional[str] = None


class HardshipApplicationRejectedEvent(LoanRestructuringEvent):
    """
    Event: Hardship application rejected.
    
    Australian NCCP: Must provide reasons and alternatives.
    
    Triggers:
    - Customer notification with reasons
    - Alternative options offered
    - Financial counselling referral
    - Complaints process information
    """
    
    event_type: str = "HardshipApplicationRejected"
    regulatory_event: bool = True
    asic_reportable: bool = True
    hardship_case: bool = True
    
    application_id: str
    
    # Rejection details
    rejection_reasons: List[str] = Field(
        default_factory=list,
        description="Specific reasons for rejection"
    )
    
    rejection_explanation: str
    
    # Alternatives offered
    alternative_options: List[str] = Field(default_factory=list)
    financial_counselling_offered: bool = True
    counselling_contact_details: Optional[str] = None
    
    # Complaint rights
    internal_dispute_resolution_offered: bool = True
    afca_information_provided: bool = True  # Australian Financial Complaints Authority
    
    # Rejection
    rejected_by: str
    rejected_at: datetime


class PaymentHolidayGrantedEvent(LoanRestructuringEvent):
    """
    Event: Payment holiday granted (hardship or voluntary).
    
    Australian NCCP: Common hardship relief mechanism.
    
    Triggers:
    - Payment schedule suspension
    - Interest capitalization
    - Customer notification
    - Monitoring setup
    """
    
    event_type: str = "PaymentHolidayGranted"
    regulatory_event: bool = True
    hardship_case: bool = True
    
    holiday_type: Literal["hardship", "voluntary", "covid_relief"]
    
    # Holiday period
    start_date: date
    end_date: date
    duration_months: int
    payments_deferred: int
    
    # Financial impact
    deferred_amount: Decimal
    interest_during_holiday: Decimal
    interest_capitalized: bool = True
    
    # Loan adjustments
    original_maturity_date: date
    new_maturity_date: date
    term_extension_months: int
    
    # Resumption
    resumption_payment_amount: Decimal
    resumption_date: date
    
    # Granted by
    granted_by: str
    granted_at: datetime


class PaymentHolidayEndedEvent(LoanRestructuringEvent):
    """
    Event: Payment holiday ended, payments resume.
    
    Triggers:
    - Payment resumption
    - Customer notification
    - ML: Predict resumption success
    """
    
    event_type: str = "PaymentHolidayEnded"
    hardship_case: bool = True
    
    holiday_end_date: date
    payments_resumed_date: date
    
    # Holiday summary
    total_payments_deferred: int
    total_amount_deferred: Decimal
    total_interest_capitalized: Decimal
    
    # Resumption
    new_payment_amount: Decimal
    new_payment_frequency: str
    
    # Success prediction
    ml_resumption_success_probability: Optional[float] = None
    
    ended_at: datetime
