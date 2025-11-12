"""Recurring Deposit Transaction Events"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import Field

from .base import RecurringDepositEvent


class MonthlyDepositDueEvent(RecurringDepositEvent):
    """
    Event: Monthly deposit is due.
    
    Published by COB job on due date.
    
    Triggers:
    - Auto-debit attempt
    - Customer notification (Anya) if auto-debit fails
    - Grace period tracking
    """
    
    event_type: str = "MonthlyDepositDue"
    
    due_date: date
    installment_number: int
    deposit_amount_due: Decimal
    
    # Account state
    current_balance: Decimal
    deposits_made_so_far: int
    deposits_missed_so_far: int
    
    # Auto-debit
    auto_debit_scheduled: bool = True
    source_account_id: str


class MonthlyDepositReceivedEvent(RecurringDepositEvent):
    """
    Event: Monthly deposit received successfully.
    
    Triggers:
    - Update account balance
    - Interest calculation
    - Accounting entries
    - Thank you message (Anya)
    """
    
    event_type: str = "MonthlyDepositReceived"
    
    deposit_date: date
    due_date: date
    installment_number: int
    deposit_amount: Decimal
    
    # Payment method
    payment_method: Literal["auto_debit", "manual_deposit", "transfer"]
    transaction_reference: str
    
    # Account state after deposit
    new_balance: Decimal
    total_deposits_made: int
    cumulative_principal: Decimal
    
    # Timeliness
    days_late: int = 0
    is_on_time: bool = True


class DepositMissedEvent(RecurringDepositEvent):
    """
    Event: Monthly deposit was missed.
    
    Triggers:
    - Penalty calculation (if applicable)
    - Grace period tracking
    - Customer reminder (Anya)
    - ML: Predict account abandonment risk
    """
    
    event_type: str = "DepositMissed"
    
    due_date: date
    installment_number: int
    deposit_amount_due: Decimal
    
    # Reason
    reason: Literal["insufficient_funds", "mandate_cancelled", "account_frozen", "unknown"]
    
    # Account state
    consecutive_misses: int
    total_misses: int
    deposits_made: int
    
    # Grace period
    grace_period_days: int = 5
    grace_period_expires: date
    
    # Actions
    penalty_applicable: bool = True
    warning_issued: bool = True
    
    # ML context
    ml_abandonment_risk: Optional[float] = Field(None, description="Risk of account abandonment")


class PenaltyAppliedEvent(RecurringDepositEvent):
    """
    Event: Penalty applied for missed deposit.
    
    Triggers:
    - Accounting entries
    - Customer notification (Anya)
    - Update account standing
    """
    
    event_type: str = "PenaltyApplied"
    
    penalty_date: date
    installment_number: int
    penalty_amount: Decimal
    penalty_type: Literal["late_fee", "missed_deposit_penalty", "premature_closure_penalty"]
    
    # Reason
    reason: str
    
    # Account impact
    new_balance: Decimal
    total_penalties: Decimal


class InterestCalculatedEvent(RecurringDepositEvent):
    """
    Event: Interest calculated for recurring deposit.
    
    Published daily/monthly by COB job.
    """
    
    event_type: str = "InterestCalculated"
    
    calculation_date: date
    principal_balance: Decimal
    interest_rate_annual: Decimal
    days_in_period: int
    interest_amount: Decimal
    
    # Cumulative
    cumulative_interest: Decimal
    projected_maturity_value: Decimal
    
    # Method
    calculation_method: str
    day_count_convention: str = "ACT/365"


class InterestPostedEvent(RecurringDepositEvent):
    """
    Event: Interest posted to RD account.
    
    Compound interest - increases principal for next period.
    """
    
    event_type: str = "InterestPosted"
    
    posting_date: date
    interest_amount: Decimal
    new_balance: Decimal
    
    posting_frequency: str  # monthly, quarterly, maturity
    next_posting_date: Optional[date]
    
    # Accounting
    gl_interest_expense_account: str
    gl_deposit_liability_account: str


class PrematureClosureRequestedEvent(RecurringDepositEvent):
    """
    Event: Customer requests premature closure.
    
    Triggers:
    - Penalty calculation
    - Interest reduction calculation
    - Maker-checker approval
    - Anya: Retention offer
    """
    
    event_type: str = "PrematureClosureRequested"
    
    request_id: str
    request_date: date
    requested_by: str
    closure_reason: str
    
    # Current position
    current_balance: Decimal
    deposits_made: int
    deposits_expected: int
    completion_percentage: float
    interest_earned: Decimal
    
    # Penalty calculation
    penalty_type: Literal["forfeit_all_interest", "reduced_interest", "flat_penalty"]
    calculated_penalty: Decimal
    revised_interest: Decimal
    net_proceeds: Decimal
    
    # Approval required
    requires_approval: bool = True
    approval_status: str = "pending"
    
    # ML context
    ml_retention_probability: Optional[float] = None
