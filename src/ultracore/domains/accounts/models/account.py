"""Account Models - Event-Sourced, UltraLedger Backed"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .enums import AccountType, AccountStatus, TransactionType, TransactionStatus


class Transaction(BaseModel):
    """Individual transaction."""
    
    transaction_id: str
    transaction_type: TransactionType
    amount: Decimal
    
    # Balance tracking
    balance_before: Decimal
    balance_after: Decimal
    
    # Description
    description: str
    reference: Optional[str] = None
    
    # Counterparty
    counterparty_account: Optional[str] = None
    counterparty_name: Optional[str] = None
    
    # Timing
    transaction_date: datetime
    value_date: date  # When funds are available
    
    # Status
    status: TransactionStatus = TransactionStatus.COMPLETED
    
    # Categories (for ML)
    category: Optional[str] = None  # groceries, transport, entertainment, etc.
    merchant: Optional[str] = None
    
    # Location
    location: Optional[str] = None
    
    # UltraLedger
    ledger_entry_id: str


class AccountStatement(BaseModel):
    """Account statement for a period."""
    
    account_id: str
    statement_period_start: date
    statement_period_end: date
    
    # Balances
    opening_balance: Decimal
    closing_balance: Decimal
    
    # Transactions
    transactions: List[Transaction] = Field(default_factory=list)
    
    # Summary
    total_deposits: Decimal = Decimal("0.00")
    total_withdrawals: Decimal = Decimal("0.00")
    total_fees: Decimal = Decimal("0.00")
    interest_earned: Decimal = Decimal("0.00")
    
    # Generated
    generated_at: datetime
    statement_number: str


class Account(BaseModel):
    """
    Base Account (Event-Sourced).
    
    Reconstructed from events.
    UltraLedger provides authoritative balances.
    """
    
    # Identity
    account_id: str
    customer_id: str
    
    # Australian identifiers
    bsb: str  # XXX-XXX format
    account_number: str  # 6-9 digits
    
    # Account details
    account_type: AccountType
    account_name: str
    currency: str = "AUD"
    
    # Product
    product_code: str
    product_name: str
    
    # Status
    status: AccountStatus = AccountStatus.ACTIVE
    
    # Balances (cached from UltraLedger)
    current_balance: Decimal = Decimal("0.00")
    available_balance: Decimal = Decimal("0.00")  # After holds
    
    # Limits
    daily_withdrawal_limit: Decimal
    daily_transfer_limit: Decimal
    overdraft_limit: Decimal = Decimal("0.00")
    
    # Today's usage
    todays_withdrawals: Decimal = Decimal("0.00")
    todays_transfers: Decimal = Decimal("0.00")
    
    # Interest (for savings)
    interest_rate: Optional[Decimal] = None
    interest_accrued_this_month: Decimal = Decimal("0.00")
    
    # Tax
    tfn_provided: bool = False
    withholding_tax_rate: Decimal = Decimal("0.00")  # 47% if no TFN
    
    # Cards
    linked_cards: List[str] = Field(default_factory=list)
    
    # Lifecycle
    opened_date: date
    last_transaction_date: Optional[date] = None
    
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


class TransactionalAccount(Account):
    """
    Transactional account (everyday banking).
    
    Australian Features:
    - No monthly fees (standard)
    - Unlimited transactions
    - NPP instant payments
    - BPAY bill payments
    - Direct debits
    - Debit card
    - Overdraft optional
    """
    
    account_type: AccountType = AccountType.TRANSACTIONAL
    
    # Fee structure
    monthly_account_fee: Decimal = Decimal("0.00")  # Often free
    transaction_fee: Decimal = Decimal("0.00")  # Often unlimited free
    
    # Features
    overdraft_approved: bool = False
    overdraft_limit: Decimal = Decimal("0.00")
    overdraft_interest_rate: Optional[Decimal] = None
    
    # NPP enabled
    npp_enabled: bool = True
    payid_email: Optional[str] = None
    payid_mobile: Optional[str] = None
    
    # BPAY enabled
    bpay_enabled: bool = True


class SavingsAccount(Account):
    """
    Savings account (interest-bearing).
    
    Australian Features:
    - Competitive interest rates
    - Bonus interest conditions
    - Limited withdrawals (to maintain bonus)
    - No overdraft
    - Often requires linked transactional account
    """
    
    account_type: AccountType = AccountType.SAVINGS
    
    # Interest structure
    base_interest_rate: Decimal
    bonus_interest_rate: Decimal = Decimal("0.00")
    total_interest_rate: Decimal
    
    # Bonus conditions
    bonus_conditions: List[str] = Field(default_factory=list)
    # Example: "Deposit $1000+ per month", "Max 1 withdrawal per month"
    
    bonus_conditions_met_this_month: bool = False
    
    # Withdrawal tracking (for bonus)
    withdrawals_this_month: int = 0
    deposits_this_month: Decimal = Decimal("0.00")
    
    # Interest calculation
    interest_calculation_method: str = "daily"  # daily compound
    interest_payment_frequency: str = "monthly"
    last_interest_payment_date: Optional[date] = None
    
    # No overdraft
    overdraft_limit: Decimal = Decimal("0.00")
    
    # Linked transactional account
    linked_transactional_account: Optional[str] = None
