"""Recurring Deposit Domain Models"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from .enums import (
    RecurringDepositStatus,
    DepositFrequency,
    MaturityInstructionType,
    PenaltyType,
    InstallmentStatus
)


class RecurringDepositProduct(BaseModel):
    """
    Recurring Deposit Product Configuration.
    
    Defines terms for systematic savings with regular deposits.
    """
    
    product_id: str
    product_name: str
    product_code: str
    
    # Term configuration
    min_term_months: int = Field(ge=6)
    max_term_months: int = Field(le=120)
    allowed_term_months: Optional[List[int]] = None  # e.g., [12, 24, 36, 48, 60]
    
    # Deposit amount configuration
    min_monthly_deposit: Decimal
    max_monthly_deposit: Optional[Decimal]
    deposit_frequency: DepositFrequency = DepositFrequency.MONTHLY
    currency: str = "AUD"
    
    # Interest configuration
    interest_calculation_method: str = "compound_monthly"
    day_count_convention: str = "ACT/365"
    
    # Interest rate (typically higher than savings, lower than FD)
    interest_rate_slabs: List[Dict[str, Any]] = Field(
        description="Interest rate based on tenure/amount"
    )
    
    # Penalties
    missed_deposit_penalty: Optional[Decimal] = None
    max_allowed_misses: int = 3
    premature_closure_penalty_type: PenaltyType
    premature_closure_penalty_rate: Optional[Decimal] = None
    
    # Auto-debit
    auto_debit_mandatory: bool = True
    auto_debit_retry_attempts: int = 3
    grace_period_days: int = 5
    
    # Features
    partial_withdrawal_allowed: bool = False
    loan_against_rd_allowed: bool = True
    skip_deposit_allowed: bool = False
    max_skips_allowed: int = 2
    
    # Regulatory
    tax_applicable: bool = True
    tds_rate: Optional[Decimal] = None
    insurance_covered: bool = True
    
    # Status
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class DepositInstallment(BaseModel):
    """
    Individual deposit installment in schedule.
    """
    
    installment_number: int
    due_date: date
    deposit_amount: Decimal
    status: InstallmentStatus = InstallmentStatus.PENDING
    
    # Payment details (when paid)
    paid_date: Optional[date] = None
    paid_amount: Optional[Decimal] = None
    payment_reference: Optional[str] = None
    days_late: int = 0
    
    # Penalty
    penalty_applied: bool = False
    penalty_amount: Decimal = Decimal("0.00")


class DepositSchedule(BaseModel):
    """
    Complete deposit schedule for RD account.
    """
    
    account_id: str
    start_date: date
    maturity_date: date
    monthly_deposit_amount: Decimal
    total_installments: int
    
    installments: List[DepositInstallment]
    
    # Summary
    deposits_made: int = 0
    deposits_missed: int = 0
    deposits_pending: int = 0
    total_principal_collected: Decimal = Decimal("0.00")
    total_penalties: Decimal = Decimal("0.00")
    completion_percentage: float = 0.0


class RecurringDepositApplication(BaseModel):
    """
    Recurring Deposit Application (before activation).
    """
    
    application_id: str
    customer_id: str
    product_id: str
    
    # Application details
    monthly_deposit_amount: Decimal
    term_months: int
    deposit_frequency: DepositFrequency
    interest_rate_annual: Decimal
    
    # Auto-debit
    source_account_id: str
    debit_day_of_month: int
    
    # Maturity instructions
    maturity_instruction: MaturityInstructionType
    maturity_transfer_account: Optional[str] = None
    
    # Status
    status: RecurringDepositStatus = RecurringDepositStatus.SUBMITTED
    submitted_by: str
    submitted_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # ML context
    fraud_score: Optional[float] = None
    affordability_score: Optional[float] = None
    completion_probability: Optional[float] = None


class RecurringDepositAccount(BaseModel):
    """
    Active Recurring Deposit Account (event-sourced).
    
    This is the aggregate root reconstructed from events.
    """
    
    # Identity
    account_id: str
    account_number: str
    customer_id: str
    product_id: str
    
    # Deposit details
    monthly_deposit_amount: Decimal
    current_balance: Decimal
    total_deposits_made: int
    total_deposits_missed: int
    total_principal_deposited: Decimal
    interest_earned: Decimal = Decimal("0.00")
    
    # Terms
    term_months: int
    total_deposits_expected: int
    deposit_frequency: DepositFrequency
    interest_rate_annual: Decimal
    interest_calculation_method: str
    
    # Dates
    start_date: date
    maturity_date: date
    next_deposit_due_date: Optional[date]
    last_deposit_date: Optional[date] = None
    
    # Auto-debit
    source_account_id: str
    debit_day_of_month: int
    mandate_reference: str
    mandate_status: str = "active"
    
    # Maturity
    maturity_instruction: MaturityInstructionType
    maturity_transfer_account: Optional[str] = None
    
    # Performance tracking
    deposits_on_time: int = 0
    deposits_late: int = 0
    consecutive_misses: int = 0
    total_penalties_paid: Decimal = Decimal("0.00")
    completion_percentage: float = 0.0
    account_health_score: float = 100.0  # 0-100
    
    # Status
    status: RecurringDepositStatus
    
    # Accounting
    gl_liability_account: str
    gl_interest_expense_account: str
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int = 0
    event_stream_version: int = 0
    
    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }
    
    def calculate_health_score(self) -> float:
        """
        Calculate account health score (0-100).
        
        Factors:
        - Completion rate: 50%
        - On-time payment rate: 30%
        - Consecutive misses: -20%
        - Penalties: -10%
        """
        if self.total_deposits_expected == 0:
            return 100.0
        
        completion_score = (self.total_deposits_made / self.total_deposits_expected) * 50
        
        if self.total_deposits_made > 0:
            on_time_rate = self.deposits_on_time / self.total_deposits_made
            on_time_score = on_time_rate * 30
        else:
            on_time_score = 0
        
        miss_penalty = min(self.consecutive_misses * 10, 20)
        penalty_deduction = min(float(self.total_penalties_paid), 10)
        
        score = completion_score + on_time_score - miss_penalty - penalty_deduction
        return max(0, min(100, score))
