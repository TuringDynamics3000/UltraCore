"""Fixed Deposit Lifecycle Commands"""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from ultracore.infrastructure.cqrs import Command


class SubmitFixedDepositApplicationCommand(Command):
    """
    Command: Submit new fixed deposit application.
    
    Flow:
    1. Validate customer eligibility
    2. ML fraud detection
    3. Publish FixedDepositApplicationSubmittedEvent to Kafka
    4. Trigger maker-checker (if enabled)
    5. Anya notification to customer
    """
    
    customer_id: str
    product_id: str
    deposit_amount: Decimal
    term_months: int
    
    # Source of funds
    source_account_id: str
    
    # Maturity instructions
    maturity_instruction: str
    maturity_transfer_account: Optional[str] = None
    auto_renewal: bool = False
    
    # Nomination
    nominee_name: Optional[str] = None
    nominee_relationship: Optional[str] = None
    
    # Channel
    channel: str = "web"
    submitted_by: str


class ApproveFixedDepositCommand(Command):
    """
    Command: Approve fixed deposit application (maker-checker).
    
    Flow:
    1. Validate approval authority
    2. Publish FixedDepositApprovedEvent to Kafka
    3. Trigger activation workflow
    """
    
    application_id: str
    approved_by: str
    approval_notes: Optional[str] = None


class RejectFixedDepositCommand(Command):
    """Command: Reject fixed deposit application."""
    
    application_id: str
    rejected_by: str
    rejection_reason: str


class ActivateFixedDepositCommand(Command):
    """
    Command: Activate fixed deposit account.
    
    Flow:
    1. Debit source account
    2. Credit FD liability account
    3. Publish FixedDepositActivatedEvent to Kafka
    4. Schedule interest calculations
    5. Issue certificate
    6. Anya welcome message
    """
    
    application_id: str
    activation_date: date
    certificate_number: Optional[str] = None


class RequestPrematureClosureCommand(Command):
    """
    Command: Request premature closure of FD.
    
    Flow:
    1. Calculate penalty
    2. ML: Assess customer retention risk
    3. Publish PrematureClosureRequestedEvent to Kafka
    4. Trigger maker-checker approval
    5. Anya: Offer retention incentives
    """
    
    account_id: str
    closure_reason: str
    requested_by: str
    closure_date: date


class ProcessMaturityCommand(Command):
    """
    Command: Process maturity of fixed deposit.
    
    Flow:
    1. Calculate final interest
    2. Process maturity instruction
    3. Publish FixedDepositMaturedEvent to Kafka
    4. ML: Predict renewal probability
    5. Anya: Renewal offer
    """
    
    account_id: str
    maturity_date: date
    process_as_per_instruction: bool = True
