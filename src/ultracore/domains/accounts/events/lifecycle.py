"""Account Lifecycle Events - Australian Banking"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import Field

from .base import AccountEvent


class AccountOpenedEvent(AccountEvent):
    """
    Event: New account opened.
    
    Australian Requirements:
    - BSB (Bank State Branch) assigned
    - Account number generated (6-9 digits)
    - KYC/AML checks completed (AUSTRAC)
    - TFN/ABN collected (tax compliance)
    
    UltraLedger:
    Creates initial ledger account with zero balance.
    
    Publishes to: ultracore.accounts.events
    
    Triggers:
    - UltraLedger account creation
    - Card issuance (debit card)
    - Welcome communication (Anya)
    - ML: Customer segment classification
    """
    
    event_type: str = "AccountOpened"
    regulatory_event: bool = True
    
    # Account details
    account_type: Literal["transactional", "savings", "term_deposit"]
    account_name: str  # Display name
    currency: str = "AUD"
    
    # Australian identifiers
    bsb: str  # Format: XXX-XXX
    account_number: str  # 6-9 digits
    
    # Product details
    product_code: str
    product_name: str
    
    # Opening balance
    opening_balance: Decimal = Decimal("0.00")
    opening_deposit_amount: Optional[Decimal] = None
    
    # Interest (for savings accounts)
    interest_rate: Optional[Decimal] = None
    interest_calculation_method: Optional[str] = None  # daily, monthly
    
    # Limits
    daily_withdrawal_limit: Decimal = Decimal("5000.00")
    daily_transfer_limit: Decimal = Decimal("10000.00")
    overdraft_limit: Decimal = Decimal("0.00")
    
    # Tax compliance
    tfn_provided: bool = False
    tfn: Optional[str] = None  # Encrypted
    abn_provided: bool = False
    abn: Optional[str] = None
    tax_exemption_claimed: bool = False
    
    # KYC/AML (AUSTRAC)
    kyc_completed: bool = True
    kyc_verification_level: str = "full"  # basic, standard, full
    aml_risk_rating: str = "low"  # low, medium, high
    pep_check_completed: bool = True  # Politically Exposed Person
    sanctions_check_completed: bool = True
    
    # Customer details
    customer_type: Literal["individual", "business", "trust", "smsf"]
    
    # Branch/channel
    opening_branch: Optional[str] = None
    opening_channel: str = "online"  # online, branch, mobile, phone
    
    # Opened by
    opened_by: str  # User ID or staff ID
    opened_at: datetime
    
    # UltraLedger
    ledger_account_id: str
    ledger_entry_id: str


class AccountActivatedEvent(AccountEvent):
    """Account activated and ready for transactions."""
    
    event_type: str = "AccountActivated"
    
    activated_at: datetime
    activated_by: str
    
    # First card issued
    debit_card_issued: bool = False
    card_number_last_four: Optional[str] = None


class AccountDormantEvent(AccountEvent):
    """
    Account marked as dormant (inactive).
    
    Australian Banking:
    - Typically after 12 months of no activity
    - ASIC unclaimed money rules apply
    - Reduced functionality
    """
    
    event_type: str = "AccountDormant"
    regulatory_event: bool = True
    
    last_transaction_date: date
    days_inactive: int
    
    dormant_reason: str = "no_activity"
    dormant_at: datetime
    
    # ASIC unclaimed money
    balance_at_dormancy: Decimal
    unclaimed_money_threshold_met: bool = False


class AccountClosedEvent(AccountEvent):
    """
    Account closed permanently.
    
    Australian Requirements:
    - Zero balance before closure
    - Final statement issued
    - Cards cancelled
    - Direct debits notified
    """
    
    event_type: str = "AccountClosed"
    regulatory_event: bool = True
    
    closure_reason: str
    final_balance: Decimal
    
    # Closures
    cards_cancelled: bool = True
    direct_debits_notified: bool = True
    final_statement_issued: bool = True
    
    # Transfer details
    residual_balance_transferred_to: Optional[str] = None
    
    closed_at: datetime
    closed_by: str


class AccountFrozenEvent(AccountEvent):
    """
    Account frozen (no transactions allowed).
    
    Reasons:
    - Fraud suspicion
    - Court order
    - AML/CTF concerns
    - Customer request
    """
    
    event_type: str = "AccountFrozen"
    regulatory_event: bool = True
    austrac_reportable: bool = False  # Depends on reason
    
    freeze_reason: Literal[
        "fraud_suspicion",
        "court_order",
        "aml_concern",
        "customer_request",
        "debt_recovery",
        "deceased_estate"
    ]
    
    freeze_description: str
    freeze_expiry: Optional[datetime] = None
    
    frozen_by: str
    frozen_at: datetime


class AccountUnfrozenEvent(AccountEvent):
    """Account unfrozen (transactions allowed again)."""
    
    event_type: str = "AccountUnfrozen"
    regulatory_event: bool = True
    
    unfreeze_reason: str
    unfrozen_by: str
    unfrozen_at: datetime
