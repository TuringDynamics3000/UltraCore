"""Fixed Deposit Transaction Events"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import Field

from .base import FixedDepositEvent


class FixedDepositCreatedEvent(FixedDepositEvent):
    """Event: Fixed deposit account created in system."""
    
    event_type: str = "FixedDepositCreated"
    
    account_number: str
    product_name: str
    deposit_amount: Decimal
    term_months: int
    interest_rate_annual: Decimal
    start_date: date
    maturity_date: date
    
    created_by: str
    created_at: datetime


class InterestCalculatedEvent(FixedDepositEvent):
    """
    Event: Interest calculated for fixed deposit (daily/monthly).
    
    Published daily by COB job for:
    - Compound interest tracking
    - Accrual accounting
    - Interest projections
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
    
    # Calculation method
    calculation_method: str
    day_count_convention: str = "ACT/365"


class InterestPostedEvent(FixedDepositEvent):
    """
    Event: Interest posted to fixed deposit account.
    
    For compound interest, this happens at posting frequency.
    For simple interest, this happens at maturity.
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


class PrematureClosureRequestedEvent(FixedDepositEvent):
    """
    Event: Customer requests premature closure.
    
    Triggers:
    - Penalty calculation
    - Maker-checker approval
    - Anya notification
    """
    
    event_type: str = "PrematureClosureRequested"
    
    request_id: str
    request_date: date
    requested_by: str
    closure_reason: str
    
    # Current position
    current_balance: Decimal
    interest_earned: Decimal
    days_held: int
    
    # Penalty calculation
    penalty_rate: Decimal
    calculated_penalty: Decimal
    net_proceeds: Decimal
    
    # Approval required
    requires_approval: bool = True
    approval_status: str = "pending"


class PrematureClosureProcessedEvent(FixedDepositEvent):
    """
    Event: Premature closure processed.
    
    Triggers:
    - Fund transfer
    - Account closure
    - Compliance reporting
    """
    
    event_type: str = "PrematureClosureProcessed"
    
    request_id: str
    closure_date: date
    
    principal_returned: Decimal
    interest_paid: Decimal
    penalty_charged: Decimal
    net_proceeds: Decimal
    
    transferred_to_account: str
    processed_by: str
    approved_by: Optional[str]
