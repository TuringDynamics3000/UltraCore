"""
UltraCore Account Management - Core Models

Next-generation account models with:
- Data mesh integration (account data products)
- Event sourcing (complete audit trail)
- Real-time streaming (balance updates)
- ML-ready features
- MCP integration ready
- Multi-currency support
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
import uuid


# ============================================================================
# Account Enums
# ============================================================================

class AccountType(str, Enum):
    """Types of accounts"""
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    TERM_DEPOSIT = "TERM_DEPOSIT"
    MONEY_MARKET = "MONEY_MARKET"
    TRANSACTION = "TRANSACTION"
    INVESTMENT = "INVESTMENT"
    LOAN = "LOAN"  # For loan accounts (already handled in lending)
    CREDIT_CARD = "CREDIT_CARD"


class AccountStatus(str, Enum):
    """Account lifecycle status"""
    PENDING = "PENDING"  # Application submitted
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"  # No activity for 12+ months
    FROZEN = "FROZEN"  # Frozen by customer or bank
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"  # Blocked due to fraud/compliance


class TransactionType(str, Enum):
    """Types of transactions"""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    INTEREST_CREDIT = "INTEREST_CREDIT"
    FEE_DEBIT = "FEE_DEBIT"
    REVERSAL = "REVERSAL"
    ADJUSTMENT = "ADJUSTMENT"
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"


class TransactionStatus(str, Enum):
    """Transaction processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    CANCELLED = "CANCELLED"


class HoldType(str, Enum):
    """Types of holds on account"""
    AUTHORIZATION = "AUTHORIZATION"  # Card authorization
    LEGAL = "LEGAL"  # Court order
    FRAUD = "FRAUD"  # Fraud investigation
    COMPLIANCE = "COMPLIANCE"  # AML/CTF hold
    OVERDRAFT = "OVERDRAFT"  # Overdraft protection


class InterestCalculationMethod(str, Enum):
    """Interest calculation methods"""
    SIMPLE = "SIMPLE"
    COMPOUND_DAILY = "COMPOUND_DAILY"
    COMPOUND_MONTHLY = "COMPOUND_MONTHLY"
    COMPOUND_QUARTERLY = "COMPOUND_QUARTERLY"
    COMPOUND_ANNUALLY = "COMPOUND_ANNUALLY"


# ============================================================================
# Core Data Models
# ============================================================================

@dataclass
class AccountBalance:
    """
    Account balance tracking
    
    Balance types:
    - Ledger Balance: Actual balance including all completed transactions
    - Available Balance: Ledger balance minus holds
    - Pending Balance: Including pending transactions
    """
    
    # Current balances
    ledger_balance: Decimal = Decimal('0.00')
    available_balance: Decimal = Decimal('0.00')
    pending_balance: Decimal = Decimal('0.00')
    
    # Holds
    total_holds: Decimal = Decimal('0.00')
    
    # Limits
    overdraft_limit: Decimal = Decimal('0.00')
    minimum_balance: Decimal = Decimal('0.00')
    maximum_balance: Optional[Decimal] = None
    
    # Interest tracking
    interest_accrued: Decimal = Decimal('0.00')
    interest_paid_ytd: Decimal = Decimal('0.00')
    
    # Last updated
    last_transaction_date: Optional[datetime] = None
    last_interest_date: Optional[date] = None
    
    def calculate_available_balance(self):
        """Calculate available balance"""
        self.available_balance = self.ledger_balance - self.total_holds
        
        # Add overdraft limit if applicable
        if self.overdraft_limit > 0:
            self.available_balance += self.overdraft_limit
    
    def is_overdrawn(self) -> bool:
        """Check if account is overdrawn"""
        return self.ledger_balance < Decimal('0.00')
    
    def has_sufficient_funds(self, amount: Decimal) -> bool:
        """Check if sufficient funds available"""
        return self.available_balance >= amount


@dataclass
class AccountHold:
    """Hold placed on account funds"""
    hold_id: str
    account_id: str
    hold_type: HoldType
    amount: Decimal
    reason: str
    
    # Lifecycle
    placed_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    active: bool = True
    
    # Authorization details (for card holds)
    authorization_code: Optional[str] = None
    merchant_name: Optional[str] = None
    
    # Metadata
    placed_by: str = "SYSTEM"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transaction:
    """
    Account transaction
    
    Features:
    - Event sourcing compatible
    - Idempotency key for duplicate prevention
    - Real-time streaming ready
    - ML feature extraction
    """
    
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    
    # Amount
    amount: Decimal
    currency: str = "AUD"
    
    # Dates
    transaction_date: datetime
    value_date: date  # When funds are available
    posting_date: Optional[date] = None  # When posted to ledger
    
    # Description
    description: str = ""
    merchant_name: Optional[str] = None
    merchant_category: Optional[str] = None
    
    # Parties
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    external_reference: Optional[str] = None
    
    # Status
    status: TransactionStatus = TransactionStatus.PENDING
    
    # Balance tracking (snapshot at transaction time)
    balance_before: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None
    
    # Fees
    fee_amount: Decimal = Decimal('0.00')
    
    # Idempotency
    idempotency_key: Optional[str] = None
    
    # Reversal tracking
    reversed: bool = False
    reversal_transaction_id: Optional[str] = None
    reversal_reason: Optional[str] = None
    
    # GL integration
    gl_entry_id: Optional[str] = None
    
    # MCP integration
    mcp_transaction_id: Optional[str] = None  # External system reference
    payment_rail: Optional[str] = None  # NPP, BPAY, SWIFT, etc.
    
    # ML features (for categorization, fraud detection)
    ml_features: Dict[str, Any] = field(default_factory=dict)
    ml_category: Optional[str] = None
    fraud_score: Optional[Decimal] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "SYSTEM"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterestRate:
    """Interest rate for account"""
    rate_id: str
    account_id: str
    
    # Rate details
    annual_rate: Decimal  # APR
    calculation_method: InterestCalculationMethod
    
    # Tiered rates (optional)
    balance_tiers: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [{'min': 0, 'max': 10000, 'rate': 2.5}, {'min': 10000, 'max': None, 'rate': 3.5}]
    
    # Validity
    effective_from: date
    effective_to: Optional[date] = None
    
    # Bonus interest
    has_bonus: bool = False
    bonus_rate: Optional[Decimal] = None
    bonus_conditions: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccountFee:
    """Fee structure for account"""
    fee_id: str
    account_id: str
    fee_type: str  # MONTHLY, TRANSACTION, OVERDRAFT, etc.
    fee_name: str
    amount: Decimal
    
    # Frequency
    frequency: str = "MONTHLY"  # DAILY, WEEKLY, MONTHLY, ANNUALLY, PER_TRANSACTION
    
    # Waivers
    can_be_waived: bool = False
    waiver_conditions: List[str] = field(default_factory=list)
    
    # Next charge
    last_charged: Optional[date] = None
    next_charge_date: Optional[date] = None
    
    # Status
    active: bool = True


@dataclass
class AccountStatement:
    """Account statement"""
    statement_id: str
    account_id: str
    
    # Period
    period_start: date
    period_end: date
    
    # Balances
    opening_balance: Decimal
    closing_balance: Decimal
    
    # Activity summary
    total_deposits: Decimal = Decimal('0.00')
    total_withdrawals: Decimal = Decimal('0.00')
    total_fees: Decimal = Decimal('0.00')
    total_interest: Decimal = Decimal('0.00')
    transaction_count: int = 0
    
    # Transactions (references)
    transaction_ids: List[str] = field(default_factory=list)
    
    # Statement details
    generated_at: datetime = field(default_factory=datetime.utcnow)
    statement_url: Optional[str] = None  # PDF URL


# ============================================================================
# Main Account Entity (Aggregate Root)
# ============================================================================

@dataclass
class Account:
    """
    Core Account entity - Aggregate Root
    
    Features:
    - Event sourcing (all changes as events)
    - Data mesh integration (account data product)
    - Real-time streaming (balance updates)
    - ML-ready features
    - MCP integration
    - Multi-currency support
    """
    
    # Core identity
    account_id: str
    account_number: str  # Customer-facing account number
    account_type: AccountType
    account_status: AccountStatus
    
    # Ownership
    customer_id: str
    tenant_id: str = "default"
    
    # Joint/multi-party accounts
    joint_holders: List[str] = field(default_factory=list)
    authorized_signatories: List[str] = field(default_factory=list)
    
    # Account details
    account_name: str = ""
    nickname: Optional[str] = None
    currency: str = "AUD"
    
    # Balance
    balance: AccountBalance = field(default_factory=AccountBalance)
    
    # Interest
    interest_bearing: bool = False
    current_interest_rate: Optional[InterestRate] = None
    interest_payment_frequency: str = "MONTHLY"
    
    # Fees
    fee_structure: List[AccountFee] = field(default_factory=list)
    fee_free: bool = False
    
    # Holds
    active_holds: List[AccountHold] = field(default_factory=list)
    
    # Transaction limits
    daily_withdrawal_limit: Optional[Decimal] = None
    daily_deposit_limit: Optional[Decimal] = None
    transaction_limit_per_transaction: Optional[Decimal] = None
    
    # Term deposit specific
    term_months: Optional[int] = None  # For term deposits
    maturity_date: Optional[date] = None
    maturity_instruction: Optional[str] = None  # ROLLOVER, TRANSFER, etc.
    
    # Account hierarchy
    parent_account_id: Optional[str] = None
    child_account_ids: Set[str] = field(default_factory=set)
    
    # Linked accounts
    linked_loan_ids: Set[str] = field(default_factory=set)
    linked_card_ids: Set[str] = field(default_factory=set)
    
    # Lifecycle dates
    opened_date: date = field(default_factory=date.today)
    closed_date: Optional[date] = None
    closure_reason: Optional[str] = None
    last_activity_date: Optional[datetime] = None
    
    # Dormancy tracking
    days_inactive: int = 0
    dormancy_warning_sent: bool = False
    
    # Compliance
    reporting_currency: str = "AUD"
    tax_withholding: bool = False
    
    # Statements
    statement_frequency: str = "MONTHLY"
    last_statement_date: Optional[date] = None
    paperless: bool = True
    
    # Notifications
    notification_preferences: Dict[str, bool] = field(default_factory=dict)
    low_balance_alert: Optional[Decimal] = None
    
    # Data Mesh - Data Product Metadata
    data_product_version: str = "v1.0"
    data_quality_score: Optional[Decimal] = None
    sla_response_time_ms: int = 100  # 100ms SLA
    
    # ML Features
    ml_features: Dict[str, Any] = field(default_factory=dict)
    predicted_balance_30d: Optional[Decimal] = None
    churn_probability: Optional[Decimal] = None
    lifetime_value: Optional[Decimal] = None
    
    # MCP Integration
    mcp_external_ids: Dict[str, str] = field(default_factory=dict)  # {'npp': 'xxx', 'bpay': 'yyy'}
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "SYSTEM"
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: str = "SYSTEM"
    version: int = 1  # For optimistic locking
    
    # Tags & attributes
    tags: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def update_balance(self, amount: Decimal, transaction_type: TransactionType):
        """Update account balance"""
        old_balance = self.balance.ledger_balance
        
        if transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER_IN, 
                                TransactionType.INTEREST_CREDIT, TransactionType.REFUND]:
            self.balance.ledger_balance += amount
        else:
            self.balance.ledger_balance -= amount
        
        self.balance.calculate_available_balance()
        self.balance.last_transaction_date = datetime.utcnow()
        self.last_activity_date = datetime.utcnow()
        self.days_inactive = 0
        self.updated_at = datetime.utcnow()
        
        return old_balance, self.balance.ledger_balance
    
    def place_hold(self, hold: AccountHold):
        """Place hold on funds"""
        self.active_holds.append(hold)
        self.balance.total_holds += hold.amount
        self.balance.calculate_available_balance()
    
    def release_hold(self, hold_id: str) -> Optional[AccountHold]:
        """Release hold"""
        for hold in self.active_holds:
            if hold.hold_id == hold_id and hold.active:
                hold.active = False
                hold.released_at = datetime.utcnow()
                self.balance.total_holds -= hold.amount
                self.balance.calculate_available_balance()
                return hold
        return None
    
    def is_dormant(self) -> bool:
        """Check if account is dormant"""
        return self.days_inactive >= 365 or self.account_status == AccountStatus.DORMANT
    
    def is_frozen(self) -> bool:
        """Check if account is frozen"""
        return self.account_status in [AccountStatus.FROZEN, AccountStatus.BLOCKED]
    
    def can_transact(self) -> Tuple[bool, Optional[str]]:
        """Check if account can perform transactions"""
        if self.account_status != AccountStatus.ACTIVE:
            return False, f"Account status is {self.account_status.value}"
        
        if self.is_frozen():
            return False, "Account is frozen"
        
        return True, None
    
    def add_child_account(self, child_account_id: str):
        """Add child account"""
        self.child_account_ids.add(child_account_id)
    
    def link_loan(self, loan_id: str):
        """Link loan to account"""
        self.linked_loan_ids.add(loan_id)
    
    def get_account_age_days(self) -> int:
        """Get account age in days"""
        return (date.today() - self.opened_date).days


# ============================================================================
# Event Models (for Event Sourcing)
# ============================================================================

class AccountEventType(str, Enum):
    """Types of account events"""
    ACCOUNT_OPENED = "ACCOUNT_OPENED"
    ACCOUNT_CLOSED = "ACCOUNT_CLOSED"
    ACCOUNT_FROZEN = "ACCOUNT_FROZEN"
    ACCOUNT_UNFROZEN = "ACCOUNT_UNFROZEN"
    TRANSACTION_POSTED = "TRANSACTION_POSTED"
    TRANSACTION_REVERSED = "TRANSACTION_REVERSED"
    BALANCE_UPDATED = "BALANCE_UPDATED"
    INTEREST_ACCRUED = "INTEREST_ACCRUED"
    FEE_CHARGED = "FEE_CHARGED"
    HOLD_PLACED = "HOLD_PLACED"
    HOLD_RELEASED = "HOLD_RELEASED"
    STATEMENT_GENERATED = "STATEMENT_GENERATED"


@dataclass
class AccountEvent:
    """
    Account event for event sourcing
    Immutable record of all account changes
    
    Features:
    - Event streaming ready
    - Data mesh integration
    - Real-time processing
    """
    
    event_id: str
    event_type: AccountEventType
    event_timestamp: datetime
    
    # Aggregate
    account_id: str
    tenant_id: str
    
    # Event data
    event_data: Dict[str, Any] = field(default_factory=dict)
    
    # Previous state (for some events)
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    # Causation
    caused_by: str = "SYSTEM"
    caused_by_event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Streaming metadata
    partition_key: Optional[str] = None  # For event streaming
    sequence_number: Optional[int] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Data Mesh - Account Data Product
# ============================================================================

@dataclass
class AccountDataProduct:
    """
    Data Mesh: Account Data Product
    
    Features:
    - SLA guarantees
    - Quality metrics
    - Schema versioning
    - Discovery metadata
    """
    
    product_id: str = "account-data-product"
    product_name: str = "Account Data Product"
    domain: str = "accounts"
    
    # Owner
    owner_team: str = "Account Management Team"
    owner_contact: str = "accounts@ultracore.com"
    
    # SLA
    availability_sla: Decimal = Decimal('99.9')  # 99.9%
    latency_sla_ms: int = 100  # 100ms
    freshness_sla_seconds: int = 1  # Real-time
    
    # Quality metrics
    completeness_score: Decimal = Decimal('100.0')
    accuracy_score: Decimal = Decimal('99.9')
    consistency_score: Decimal = Decimal('100.0')
    
    # Schema
    schema_version: str = "v1.0"
    schema_registry_url: str = "https://schema-registry.ultracore.com/accounts/v1"
    
    # Discovery
    description: str = "Real-time account data with balance, transactions, and analytics"
    tags: List[str] = field(default_factory=lambda: ["accounts", "balance", "transactions", "real-time"])
    
    # Access
    access_policy: str = "role-based"
    api_endpoint: str = "https://api.ultracore.com/v1/accounts"
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
