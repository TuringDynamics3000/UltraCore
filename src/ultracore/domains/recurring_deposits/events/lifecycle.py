"""Recurring Deposit Lifecycle Events"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import Field

from .base import RecurringDepositEvent


class RecurringDepositApplicationSubmittedEvent(RecurringDepositEvent):
    """
    Event: Customer submits recurring deposit application.
    
    Kafka Topic: ultracore.recurring_deposits.events
    
    Triggers:
    - Maker-checker workflow (if enabled)
    - ML fraud detection
    - Credit/affordability check
    - Auto-debit mandate setup
    - Anya notification to customer
    """
    
    event_type: str = "RecurringDepositApplicationSubmitted"
    
    # Application details
    application_id: str
    monthly_deposit_amount: Decimal = Field(..., description="Monthly deposit amount")
    term_months: int = Field(..., ge=6, le=120, description="Term in months")
    deposit_frequency: Literal["monthly", "quarterly"] = "monthly"
    interest_rate_annual: Decimal = Field(..., description="Annual interest rate %")
    interest_calculation_method: Literal["compound_monthly", "compound_quarterly"]
    
    # Maturity instructions
    maturity_instruction: Literal["transfer_to_savings", "convert_to_fd", "transfer_to_account"]
    maturity_transfer_account: Optional[str] = None
    
    # Auto-debit setup
    source_account_id: str = Field(..., description="Account for auto-debit")
    debit_day_of_month: int = Field(..., ge=1, le=28, description="Day of month for auto-debit")
    
    # Submitted by
    submitted_by: str
    submitted_at: datetime
    channel: Literal["web", "mobile", "branch", "api"] = "web"
    
    # ML context
    ml_fraud_score: Optional[float] = None
    ml_affordability_score: Optional[float] = None
    ml_completion_probability: Optional[float] = None


class RecurringDepositApprovedEvent(RecurringDepositEvent):
    """
    Event: RD application approved (maker-checker).
    
    Triggers:
    - Account activation
    - Auto-debit mandate activation
    - Customer notification (Anya)
    - First deposit scheduling
    """
    
    event_type: str = "RecurringDepositApproved"
    
    application_id: str
    approved_by: str
    approved_at: datetime
    approval_notes: Optional[str] = None
    
    # Final approved terms
    monthly_deposit_amount: Decimal
    term_months: int
    interest_rate_annual: Decimal
    maturity_date: date
    first_deposit_due_date: date


class RecurringDepositActivatedEvent(RecurringDepositEvent):
    """
    Event: Recurring deposit activated.
    
    Triggers:
    - Monthly deposit scheduling (COB job)
    - Interest calculation scheduling
    - Auto-debit mandate confirmation
    - Data mesh product update
    - First deposit due notification (Anya)
    """
    
    event_type: str = "RecurringDepositActivated"
    
    monthly_deposit_amount: Decimal
    activation_date: date
    maturity_date: date
    term_months: int
    total_deposits_expected: int
    interest_rate_annual: Decimal
    
    # Expected maturity calculation
    total_principal_expected: Decimal
    expected_interest: Decimal
    expected_maturity_value: Decimal
    
    # Auto-debit details
    source_account_id: str
    debit_day_of_month: int
    mandate_reference: str
    mandate_status: str = "active"
    
    # First deposit
    first_deposit_due_date: date
    
    # Certificate
    certificate_number: Optional[str] = None


class RecurringDepositMaturedEvent(RecurringDepositEvent):
    """
    Event: Recurring deposit reached maturity.
    
    Triggers:
    - Final interest calculation
    - Maturity processing
    - Customer notification (Anya)
    - ML: Predict whether customer will open another RD
    """
    
    event_type: str = "RecurringDepositMatured"
    
    maturity_date: date
    total_deposits_made: int
    total_deposits_missed: int
    total_principal: Decimal
    interest_earned: Decimal
    total_maturity_value: Decimal
    
    # Tax
    tax_deducted: Decimal = Decimal("0.00")
    net_proceeds: Decimal
    
    # Performance
    deposit_completion_rate: float = Field(..., description="% of deposits made")
    total_penalties_paid: Decimal = Decimal("0.00")
    
    # Maturity instruction
    maturity_instruction: str
    target_account_id: Optional[str] = None
    
    # ML predictions
    ml_renewal_probability: Optional[float] = None


class RecurringDepositClosedEvent(RecurringDepositEvent):
    """
    Event: Recurring deposit closed.
    
    Triggers:
    - Final accounting entries
    - Auto-debit mandate cancellation
    - Data mesh archival
    - Customer satisfaction survey (Anya)
    """
    
    event_type: str = "RecurringDepositClosed"
    
    closure_date: date
    closure_reason: Literal[
        "maturity",
        "premature_customer_request",
        "affordability_hardship",
        "death",
        "bankruptcy"
    ]
    
    total_deposits_made: int
    total_principal: Decimal
    interest_earned: Decimal
    penalty_amount: Decimal = Decimal("0.00")
    tax_deducted: Decimal = Decimal("0.00")
    net_proceeds: Decimal
    
    # Transfer details
    transferred_to_account: Optional[str] = None
    transfer_completed: bool = False
    
    closed_by: str
    closure_notes: Optional[str] = None
