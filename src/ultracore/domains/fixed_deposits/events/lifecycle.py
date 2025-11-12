"""Fixed Deposit Lifecycle Events"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import Field

from .base import FixedDepositEvent


class FixedDepositApplicationSubmittedEvent(FixedDepositEvent):
    """
    Event: Customer submits fixed deposit application.
    
    Kafka Topic: ultracore.fixed_deposits.events
    Partition Key: account_id
    
    Triggers:
    - Maker-checker workflow (if enabled)
    - Credit check (if required)
    - ML risk assessment
    - Anya notification to customer
    """
    
    event_type: str = "FixedDepositApplicationSubmitted"
    
    # Application details
    application_id: str
    deposit_amount: Decimal = Field(..., description="Deposit amount")
    term_months: int = Field(..., ge=1, le=120, description="Term in months")
    interest_rate_annual: Decimal = Field(..., description="Annual interest rate %")
    interest_calculation_method: Literal["simple", "compound_monthly", "compound_quarterly", "compound_annual"]
    maturity_instruction: Literal["transfer_to_savings", "renew_deposit", "transfer_to_account"]
    maturity_transfer_account: Optional[str] = None
    
    # Customer preferences
    auto_renewal: bool = False
    premature_closure_allowed: bool = True
    
    # Submitted by
    submitted_by: str
    submitted_at: datetime
    channel: Literal["web", "mobile", "branch", "api"] = "web"
    
    # ML context
    ml_fraud_score: Optional[float] = Field(None, description="ML fraud detection score")
    ml_churn_risk: Optional[float] = Field(None, description="Customer churn risk")


class FixedDepositApprovedEvent(FixedDepositEvent):
    """
    Event: Fixed deposit application approved (maker-checker).
    
    Triggers:
    - Account activation
    - Customer notification (Anya)
    - Accounting entries
    """
    
    event_type: str = "FixedDepositApproved"
    
    application_id: str
    approved_by: str
    approved_at: datetime
    approval_notes: Optional[str] = None
    
    # Final approved terms
    deposit_amount: Decimal
    term_months: int
    interest_rate_annual: Decimal
    maturity_date: date


class FixedDepositActivatedEvent(FixedDepositEvent):
    """
    Event: Fixed deposit activated and funds deposited.
    
    Triggers:
    - Interest calculation scheduling
    - COB job registration
    - Data mesh product update
    - Accounting entries (debit savings, credit FD liability)
    """
    
    event_type: str = "FixedDepositActivated"
    
    deposit_amount: Decimal
    activation_date: date
    maturity_date: date
    term_months: int
    interest_rate_annual: Decimal
    interest_calculation_method: str
    
    # Expected maturity values
    expected_interest: Decimal
    expected_maturity_value: Decimal
    
    # Source of funds
    source_account_id: str
    source_account_type: Literal["savings", "checking", "external"]
    
    # Certificate details
    certificate_number: str
    certificate_issued: bool = False


class FixedDepositMaturedEvent(FixedDepositEvent):
    """
    Event: Fixed deposit reached maturity date.
    
    Triggers:
    - Maturity processing
    - Interest posting
    - Principal transfer
    - Auto-renewal (if configured)
    - Customer notification (Anya)
    - ML: Predict renewal likelihood
    """
    
    event_type: str = "FixedDepositMatured"
    
    maturity_date: date
    principal_amount: Decimal
    interest_earned: Decimal
    total_maturity_value: Decimal
    
    # Tax
    tax_deducted: Decimal = Decimal("0.00")
    net_proceeds: Decimal
    
    # Maturity instruction
    maturity_instruction: str
    target_account_id: Optional[str] = None
    
    # ML predictions
    ml_renewal_probability: Optional[float] = Field(None, description="Predicted renewal likelihood")


class FixedDepositClosedEvent(FixedDepositEvent):
    """
    Event: Fixed deposit closed (maturity or premature).
    
    Triggers:
    - Final accounting entries
    - Data mesh archival
    - Compliance reporting
    - Customer satisfaction survey (Anya)
    """
    
    event_type: str = "FixedDepositClosed"
    
    closure_date: date
    closure_reason: Literal["maturity", "premature_customer_request", "death", "bankruptcy", "regulatory"]
    
    principal_amount: Decimal
    interest_earned: Decimal
    penalty_amount: Decimal = Decimal("0.00")
    tax_deducted: Decimal = Decimal("0.00")
    net_proceeds: Decimal
    
    # Transfer details
    transferred_to_account: Optional[str] = None
    transfer_completed: bool = False
    
    closed_by: str
    closure_notes: Optional[str] = None


class FixedDepositRenewedEvent(FixedDepositEvent):
    """
    Event: Fixed deposit auto-renewed for another term.
    
    Triggers:
    - New FD account creation
    - Interest rate adjustment (current market rate)
    - Customer notification
    - ML: Update renewal prediction model
    """
    
    event_type: str = "FixedDepositRenewed"
    
    previous_account_id: str
    new_account_id: str
    
    # Previous term
    previous_maturity_value: Decimal
    
    # New term
    new_principal: Decimal
    new_term_months: int
    new_interest_rate: Decimal
    new_maturity_date: date
    
    # Rate adjustment
    rate_change: Decimal = Field(..., description="Change in interest rate")
    rate_change_reason: str
    
    renewal_date: date
    auto_renewed: bool = True
