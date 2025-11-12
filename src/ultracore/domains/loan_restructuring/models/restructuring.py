"""Loan Restructuring Domain Models - Australian NCCP Compliant"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .enums import (
    HardshipReason,
    ReliefType,
    RestructuringStatus,
    ApplicationStatus
)


class HardshipApplication(BaseModel):
    """
    Hardship application under Australian NCCP Section 72.
    
    Lenders must consider hardship variations.
    """
    
    application_id: str
    loan_id: str
    customer_id: str
    
    # Hardship details
    hardship_reason: HardshipReason
    hardship_description: str
    financial_impact_description: str
    
    # Financial situation
    current_income_monthly: Decimal
    essential_expenses_monthly: Decimal
    other_debts_monthly: Decimal
    disposable_income_monthly: Decimal
    
    # Current loan status
    current_payment_amount: Decimal
    current_arrears_amount: Decimal = Decimal("0.00")
    days_in_arrears: int = 0
    
    # Requested relief
    requested_relief_types: List[ReliefType] = Field(default_factory=list)
    requested_duration_months: Optional[int] = None
    can_afford_amount: Optional[Decimal] = None
    
    # Supporting evidence
    documents_provided: List[str] = Field(default_factory=list)
    income_evidence_provided: bool = False
    expense_evidence_provided: bool = False
    
    # Financial counselling
    financial_counselling_contacted: bool = False
    counselling_reference: Optional[str] = None
    
    # Status
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    
    # Outcome
    approved_relief: Optional[ReliefType] = None
    rejection_reasons: List[str] = Field(default_factory=list)


class PaymentHoliday(BaseModel):
    """
    Payment holiday (temporary payment suspension).
    
    Common hardship relief in Australia.
    """
    
    loan_id: str
    customer_id: str
    
    holiday_type: str  # hardship, voluntary, covid_relief
    
    # Period
    start_date: date
    end_date: date
    duration_months: int
    payments_deferred: int
    
    # Financial impact
    deferred_amount: Decimal
    interest_during_holiday: Decimal
    interest_capitalized: bool = True
    
    # Loan impact
    original_maturity_date: date
    new_maturity_date: date
    term_extension_months: int
    
    # Resumption
    resumption_payment_amount: Decimal
    resumption_date: date
    
    # Status
    is_active: bool = True
    ended_date: Optional[date] = None


class TermExtension(BaseModel):
    """Term extension to reduce payment amount."""
    
    loan_id: str
    customer_id: str
    
    # Original terms
    original_term_months: int
    original_maturity_date: date
    original_payment_amount: Decimal
    
    # New terms
    new_term_months: int
    new_maturity_date: date
    new_payment_amount: Decimal
    extension_months: int
    
    # Financial impact
    payment_reduction_amount: Decimal
    payment_reduction_percentage: Decimal
    total_interest_increase: Decimal
    
    # Effective date
    effective_date: date
    applied_at: datetime


class InterestRateModification(BaseModel):
    """Interest rate reduction (hardship relief)."""
    
    loan_id: str
    customer_id: str
    
    # Original rate
    original_interest_rate: Decimal
    
    # New rate
    new_interest_rate: Decimal
    rate_reduction: Decimal
    
    # Duration
    modification_start_date: date
    modification_end_date: Optional[date] = None
    temporary: bool = True
    duration_months: Optional[int] = None
    
    # Impact
    monthly_payment_reduction: Decimal
    total_interest_saved: Decimal
    
    # Reversion
    revert_to_rate: Optional[Decimal] = None
    reversion_date: Optional[date] = None


class RestructuringPlan(BaseModel):
    """
    Complete loan restructuring plan.
    
    May combine multiple relief types.
    """
    
    restructuring_id: str
    loan_id: str
    customer_id: str
    
    # Plan details
    restructuring_type: str
    relief_types: List[ReliefType] = Field(default_factory=list)
    
    # Components
    payment_holiday: Optional[PaymentHoliday] = None
    term_extension: Optional[TermExtension] = None
    rate_modification: Optional[InterestRateModification] = None
    
    # Financial summary
    original_monthly_payment: Decimal
    new_monthly_payment: Decimal
    payment_reduction: Decimal
    total_additional_interest: Decimal
    total_cost_to_customer: Decimal
    
    # Timeline
    effective_date: date
    review_date: Optional[date] = None
    completion_date: Optional[date] = None
    
    # Status
    status: RestructuringStatus = RestructuringStatus.PENDING
    
    # Conditions
    conditions: List[str] = Field(default_factory=list)
    monitoring_required: bool = True
    
    # Success tracking
    payments_made_on_time: int = 0
    payments_missed: int = 0
    success_probability: Optional[float] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime


class LoanRestructuring(BaseModel):
    """
    Main Loan Restructuring aggregate (event-sourced).
    
    Reconstructed from events.
    """
    
    restructuring_id: str
    loan_id: str
    customer_id: str
    
    # Trigger
    hardship_application: Optional[HardshipApplication] = None
    trigger_reason: str
    
    # Active plan
    active_plan: Optional[RestructuringPlan] = None
    
    # History
    previous_restructurings: List[str] = Field(default_factory=list)
    restructuring_count: int = 0
    
    # Status
    status: RestructuringStatus
    
    # Monitoring
    is_performing: bool = True
    consecutive_on_time_payments: int = 0
    arrears_amount: Decimal = Decimal("0.00")
    
    # ML predictions
    ml_success_probability: Optional[float] = None
    ml_risk_score: Optional[float] = None
    
    # Compliance
    nccp_compliant: bool = True
    financial_counselling_offered: bool = True
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int = 0
    
    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }
