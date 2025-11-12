"""Fixed Deposit Domain Models"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from .enums import (
    FixedDepositStatus,
    InterestCalculationMethod,
    MaturityInstructionType,
    PrematureClosurePenaltyType,
    InterestPostingFrequency
)


class FixedDepositProduct(BaseModel):
    """
    Fixed Deposit Product Configuration.
    
    Defines the terms and conditions for a type of fixed deposit.
    """
    
    product_id: str
    product_name: str
    product_code: str
    
    # Term configuration
    min_term_months: int = Field(ge=1)
    max_term_months: int = Field(le=120)
    allowed_term_months: Optional[List[int]] = None  # e.g., [3, 6, 12, 24, 36]
    
    # Amount configuration
    min_deposit_amount: Decimal
    max_deposit_amount: Optional[Decimal]
    currency: str = "AUD"
    
    # Interest configuration
    interest_calculation_method: InterestCalculationMethod
    interest_posting_frequency: InterestPostingFrequency
    day_count_convention: str = "ACT/365"
    
    # Interest rate tiers (amount-based or term-based)
    interest_rate_slabs: List[Dict[str, Any]] = Field(
        description="Interest rate slabs based on amount/term"
    )
    
    # Premature closure
    premature_closure_allowed: bool = True
    premature_penalty_type: PrematureClosurePenaltyType
    premature_penalty_rate: Optional[Decimal] = None
    min_days_before_premature_closure: int = 0
    
    # Auto-renewal
    auto_renewal_allowed: bool = True
    auto_renewal_default: bool = False
    
    # Features
    partial_withdrawal_allowed: bool = False
    loan_against_fd_allowed: bool = True
    nomination_required: bool = False
    
    # Regulatory
    tax_applicable: bool = True
    tds_rate: Optional[Decimal] = None
    insurance_covered: bool = True
    insurance_limit: Optional[Decimal] = None
    
    # Status
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    @validator("interest_rate_slabs")
    def validate_slabs(cls, v):
        """Ensure interest rate slabs are properly configured."""
        if not v:
            raise ValueError("At least one interest rate slab required")
        return v


class FixedDepositApplication(BaseModel):
    """
    Fixed Deposit Application (before activation).
    """
    
    application_id: str
    customer_id: str
    product_id: str
    
    # Application details
    deposit_amount: Decimal
    term_months: int
    interest_rate_annual: Decimal
    interest_calculation_method: InterestCalculationMethod
    
    # Maturity instructions
    maturity_instruction: MaturityInstructionType
    maturity_transfer_account: Optional[str] = None
    auto_renewal: bool = False
    
    # Nomination
    nominee_name: Optional[str] = None
    nominee_relationship: Optional[str] = None
    
    # Status
    status: FixedDepositStatus = FixedDepositStatus.SUBMITTED
    submitted_by: str
    submitted_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Channel
    channel: str = "web"
    
    # ML context
    fraud_score: Optional[float] = None
    risk_score: Optional[float] = None


class FixedDepositAccount(BaseModel):
    """
    Active Fixed Deposit Account (event-sourced).
    
    This is the aggregate root reconstructed from events.
    """
    
    # Identity
    account_id: str
    account_number: str
    customer_id: str
    product_id: str
    
    # Deposit details
    principal_amount: Decimal
    current_balance: Decimal
    interest_earned: Decimal = Decimal("0.00")
    
    # Terms
    term_months: int
    interest_rate_annual: Decimal
    interest_calculation_method: InterestCalculationMethod
    interest_posting_frequency: InterestPostingFrequency
    
    # Dates
    start_date: date
    maturity_date: date
    last_interest_posting_date: Optional[date] = None
    
    # Maturity
    maturity_instruction: MaturityInstructionType
    maturity_transfer_account: Optional[str] = None
    auto_renewal: bool = False
    
    # Status
    status: FixedDepositStatus
    
    # Premature closure
    premature_closure_allowed: bool = True
    premature_penalty_rate: Decimal = Decimal("0.00")
    
    # Certificate
    certificate_number: Optional[str] = None
    certificate_issued: bool = False
    
    # Accounting
    gl_liability_account: str
    gl_interest_expense_account: str
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int = 0  # Optimistic locking
    
    # Event sourcing
    event_stream_version: int = 0
    
    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class InterestCalculation(BaseModel):
    """Interest calculation result."""
    
    calculation_date: date
    principal_balance: Decimal
    interest_rate_annual: Decimal
    days_in_period: int
    interest_amount: Decimal
    cumulative_interest: Decimal
    projected_maturity_value: Decimal
    
    calculation_method: InterestCalculationMethod
    day_count_convention: str


class MaturityInstruction(BaseModel):
    """Maturity processing instructions."""
    
    account_id: str
    maturity_date: date
    principal_amount: Decimal
    interest_earned: Decimal
    tax_deducted: Decimal
    net_proceeds: Decimal
    
    instruction_type: MaturityInstructionType
    target_account_id: Optional[str] = None
    
    # Auto-renewal details
    renew_with_same_terms: bool = False
    new_interest_rate: Optional[Decimal] = None
