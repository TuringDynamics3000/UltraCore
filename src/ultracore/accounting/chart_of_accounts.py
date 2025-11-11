"""
UltraCore Accounting System - Chart of Accounts

AI-Enhanced Chart of Accounts with:
- Standard Australian accounting structure
- AI-powered account classification
- Dynamic account creation
- ML-based account recommendations
- Data mesh domain ownership
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal


# ============================================================================
# Account Enums
# ============================================================================

class AccountType(str, Enum):
    """Standard account types"""
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class AccountSubType(str, Enum):
    """Detailed account subtypes"""
    # Assets
    CASH = "CASH"
    BANK = "BANK"
    ACCOUNTS_RECEIVABLE = "ACCOUNTS_RECEIVABLE"
    INVENTORY = "INVENTORY"
    PREPAID_EXPENSES = "PREPAID_EXPENSES"
    FIXED_ASSETS = "FIXED_ASSETS"
    ACCUMULATED_DEPRECIATION = "ACCUMULATED_DEPRECIATION"
    INTANGIBLE_ASSETS = "INTANGIBLE_ASSETS"
    
    # Liabilities
    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"
    ACCRUED_EXPENSES = "ACCRUED_EXPENSES"
    SHORT_TERM_DEBT = "SHORT_TERM_DEBT"
    LONG_TERM_DEBT = "LONG_TERM_DEBT"
    DEFERRED_REVENUE = "DEFERRED_REVENUE"
    
    # Equity
    SHARE_CAPITAL = "SHARE_CAPITAL"
    RETAINED_EARNINGS = "RETAINED_EARNINGS"
    RESERVES = "RESERVES"
    
    # Revenue
    OPERATING_REVENUE = "OPERATING_REVENUE"
    INTEREST_INCOME = "INTEREST_INCOME"
    FEE_INCOME = "FEE_INCOME"
    OTHER_INCOME = "OTHER_INCOME"
    
    # Expenses
    OPERATING_EXPENSES = "OPERATING_EXPENSES"
    INTEREST_EXPENSE = "INTEREST_EXPENSE"
    DEPRECIATION = "DEPRECIATION"
    SALARIES = "SALARIES"
    MARKETING = "MARKETING"
    IT_EXPENSES = "IT_EXPENSES"


class AccountClass(str, Enum):
    """Account classification for reporting"""
    CURRENT = "CURRENT"  # Current assets/liabilities
    NON_CURRENT = "NON_CURRENT"  # Long-term
    OPERATING = "OPERATING"  # Operating activities
    FINANCING = "FINANCING"  # Financing activities
    INVESTING = "INVESTING"  # Investing activities


class DataMeshDomain(str, Enum):
    """Data mesh domain ownership"""
    LENDING = "LENDING"
    DEPOSITS = "DEPOSITS"
    PAYMENTS = "PAYMENTS"
    INVESTMENTS = "INVESTMENTS"
    TREASURY = "TREASURY"
    OPERATIONS = "OPERATIONS"
    COMPLIANCE = "COMPLIANCE"


# ============================================================================
# Account Models
# ============================================================================

@dataclass
class GLAccount:
    """General Ledger Account with AI capabilities"""
    account_code: str  # e.g., "1100" for Cash
    account_name: str
    account_type: AccountType
    account_subtype: AccountSubType
    account_class: AccountClass
    
    # Hierarchy
    parent_account: Optional[str] = None
    level: int = 1  # 1=top level, 2=sub, 3=sub-sub
    
    # Data Mesh
    domain_owner: DataMeshDomain = DataMeshDomain.OPERATIONS
    
    # AI/ML Metadata
    ml_category_confidence: float = 1.0  # AI confidence in categorization
    common_keywords: List[str] = field(default_factory=list)
    auto_categorization_enabled: bool = True
    
    # Account properties
    is_system_account: bool = False
    is_control_account: bool = False
    currency: str = "AUD"
    allow_manual_entries: bool = True
    
    # Balance tracking
    normal_balance: str = "DEBIT"  # DEBIT or CREDIT
    current_balance: Decimal = Decimal('0.00')
    
    # Status
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccountMapping:
    """Maps products/services to GL accounts"""
    mapping_id: str
    product_type: str  # loan, savings, payment, etc.
    transaction_type: str  # disbursement, repayment, fee, interest
    
    # Account mappings
    debit_account: str
    credit_account: str
    
    # Conditional logic
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # AI decision
    ai_recommended: bool = False
    confidence_score: float = 1.0
    
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Chart of Accounts Manager
# ============================================================================

class ChartOfAccounts:
    """
    AI-Enhanced Chart of Accounts Manager
    Manages GL accounts with AI-powered categorization
    """
    
    def __init__(self):
        self.accounts: Dict[str, GLAccount] = {}
        self.mappings: List[AccountMapping] = []
        self._initialize_standard_accounts()
    
    def _initialize_standard_accounts(self):
        """Initialize standard Australian banking chart of accounts"""
        
        # ====================================================================
        # ASSETS (1000-1999)
        # ====================================================================
        
        # Current Assets (1000-1499)
        self.add_account(GLAccount(
            account_code="1000",
            account_name="Current Assets",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.CASH,
            account_class=AccountClass.CURRENT,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.TREASURY
        ))
        
        self.add_account(GLAccount(
            account_code="1100",
            account_name="Cash on Hand",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.CASH,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.TREASURY,
            common_keywords=["cash", "petty cash", "till"]
        ))
        
        self.add_account(GLAccount(
            account_code="1110",
            account_name="Cash at Bank - Operating",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.BANK,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.TREASURY,
            common_keywords=["bank", "checking", "current account"]
        ))
        
        self.add_account(GLAccount(
            account_code="1120",
            account_name="Cash at Bank - Settlement",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.BANK,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.PAYMENTS,
            common_keywords=["settlement", "clearing"]
        ))
        
        self.add_account(GLAccount(
            account_code="1200",
            account_name="Customer Loans - Principal",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.ACCOUNTS_RECEIVABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.LENDING,
            common_keywords=["loan", "receivable", "principal"]
        ))
        
        self.add_account(GLAccount(
            account_code="1210",
            account_name="Loan Interest Receivable",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.ACCOUNTS_RECEIVABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.LENDING,
            common_keywords=["interest", "accrued interest"]
        ))
        
        self.add_account(GLAccount(
            account_code="1220",
            account_name="Fee Receivable",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.ACCOUNTS_RECEIVABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS,
            common_keywords=["fee", "charge", "receivable"]
        ))
        
        self.add_account(GLAccount(
            account_code="1300",
            account_name="Loan Loss Allowance",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.ACCOUNTS_RECEIVABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="1000",
            normal_balance="CREDIT",  # Contra-asset
            domain_owner=DataMeshDomain.LENDING,
            common_keywords=["provision", "allowance", "bad debt"]
        ))
        
        # Non-Current Assets (1500-1999)
        self.add_account(GLAccount(
            account_code="1500",
            account_name="Non-Current Assets",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.FIXED_ASSETS,
            account_class=AccountClass.NON_CURRENT,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="1510",
            account_name="Property, Plant & Equipment",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.FIXED_ASSETS,
            account_class=AccountClass.NON_CURRENT,
            level=2,
            parent_account="1500",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="1520",
            account_name="Accumulated Depreciation",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.ACCUMULATED_DEPRECIATION,
            account_class=AccountClass.NON_CURRENT,
            level=2,
            parent_account="1500",
            normal_balance="CREDIT",  # Contra-asset
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="1600",
            account_name="Intangible Assets",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.INTANGIBLE_ASSETS,
            account_class=AccountClass.NON_CURRENT,
            level=2,
            parent_account="1500",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS,
            common_keywords=["software", "licenses", "goodwill"]
        ))
        
        # ====================================================================
        # LIABILITIES (2000-2999)
        # ====================================================================
        
        # Current Liabilities (2000-2499)
        self.add_account(GLAccount(
            account_code="2000",
            account_name="Current Liabilities",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.ACCOUNTS_PAYABLE,
            account_class=AccountClass.CURRENT,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="2100",
            account_name="Customer Deposits - Savings",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.ACCOUNTS_PAYABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="2000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.DEPOSITS,
            common_keywords=["deposit", "savings", "customer balance"]
        ))
        
        self.add_account(GLAccount(
            account_code="2110",
            account_name="Customer Deposits - Current",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.ACCOUNTS_PAYABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="2000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.DEPOSITS,
            common_keywords=["checking", "current account"]
        ))
        
        self.add_account(GLAccount(
            account_code="2200",
            account_name="Interest Payable",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.ACCRUED_EXPENSES,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="2000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.DEPOSITS,
            common_keywords=["interest", "accrued"]
        ))
        
        self.add_account(GLAccount(
            account_code="2300",
            account_name="Accounts Payable",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.ACCOUNTS_PAYABLE,
            account_class=AccountClass.CURRENT,
            level=2,
            parent_account="2000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        # Non-Current Liabilities (2500-2999)
        self.add_account(GLAccount(
            account_code="2500",
            account_name="Non-Current Liabilities",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.LONG_TERM_DEBT,
            account_class=AccountClass.NON_CURRENT,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.TREASURY
        ))
        
        self.add_account(GLAccount(
            account_code="2510",
            account_name="Long-term Borrowings",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubType.LONG_TERM_DEBT,
            account_class=AccountClass.NON_CURRENT,
            level=2,
            parent_account="2500",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.TREASURY
        ))
        
        # ====================================================================
        # EQUITY (3000-3999)
        # ====================================================================
        
        self.add_account(GLAccount(
            account_code="3000",
            account_name="Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubType.SHARE_CAPITAL,
            account_class=AccountClass.FINANCING,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.TREASURY
        ))
        
        self.add_account(GLAccount(
            account_code="3100",
            account_name="Share Capital",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubType.SHARE_CAPITAL,
            account_class=AccountClass.FINANCING,
            level=2,
            parent_account="3000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.TREASURY
        ))
        
        self.add_account(GLAccount(
            account_code="3200",
            account_name="Retained Earnings",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubType.RETAINED_EARNINGS,
            account_class=AccountClass.FINANCING,
            level=2,
            parent_account="3000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.TREASURY,
            is_system_account=True
        ))
        
        self.add_account(GLAccount(
            account_code="3300",
            account_name="Current Year Profit/Loss",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubType.RETAINED_EARNINGS,
            account_class=AccountClass.FINANCING,
            level=2,
            parent_account="3000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.TREASURY,
            is_system_account=True
        ))
        
        # ====================================================================
        # REVENUE (4000-4999)
        # ====================================================================
        
        self.add_account(GLAccount(
            account_code="4000",
            account_name="Revenue",
            account_type=AccountType.REVENUE,
            account_subtype=AccountSubType.OPERATING_REVENUE,
            account_class=AccountClass.OPERATING,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="4100",
            account_name="Interest Income - Loans",
            account_type=AccountType.REVENUE,
            account_subtype=AccountSubType.INTEREST_INCOME,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="4000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.LENDING,
            common_keywords=["interest income", "loan interest"]
        ))
        
        self.add_account(GLAccount(
            account_code="4200",
            account_name="Fee Income",
            account_type=AccountType.REVENUE,
            account_subtype=AccountSubType.FEE_INCOME,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="4000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.OPERATIONS,
            common_keywords=["fee", "charge", "service fee"]
        ))
        
        self.add_account(GLAccount(
            account_code="4210",
            account_name="Transaction Fee Income",
            account_type=AccountType.REVENUE,
            account_subtype=AccountSubType.FEE_INCOME,
            account_class=AccountClass.OPERATING,
            level=3,
            parent_account="4200",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.PAYMENTS
        ))
        
        self.add_account(GLAccount(
            account_code="4300",
            account_name="Other Income",
            account_type=AccountType.REVENUE,
            account_subtype=AccountSubType.OTHER_INCOME,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="4000",
            normal_balance="CREDIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        # ====================================================================
        # EXPENSES (5000-5999)
        # ====================================================================
        
        self.add_account(GLAccount(
            account_code="5000",
            account_name="Expenses",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATING_EXPENSES,
            account_class=AccountClass.OPERATING,
            level=1,
            is_control_account=True,
            allow_manual_entries=False,
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="5100",
            account_name="Interest Expense - Deposits",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.INTEREST_EXPENSE,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="5000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.DEPOSITS,
            common_keywords=["interest expense", "deposit interest"]
        ))
        
        self.add_account(GLAccount(
            account_code="5200",
            account_name="Salaries & Wages",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.SALARIES,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="5000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="5300",
            account_name="Marketing & Advertising",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.MARKETING,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="5000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="5400",
            account_name="IT & Technology",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.IT_EXPENSES,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="5000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
        
        self.add_account(GLAccount(
            account_code="5500",
            account_name="Loan Loss Provision",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATING_EXPENSES,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="5000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.LENDING,
            common_keywords=["provision", "bad debt", "write-off"]
        ))
        
        self.add_account(GLAccount(
            account_code="5600",
            account_name="Depreciation Expense",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.DEPRECIATION,
            account_class=AccountClass.OPERATING,
            level=2,
            parent_account="5000",
            normal_balance="DEBIT",
            domain_owner=DataMeshDomain.OPERATIONS
        ))
    
    def add_account(self, account: GLAccount) -> GLAccount:
        """Add account to chart"""
        self.accounts[account.account_code] = account
        return account
    
    def get_account(self, account_code: str) -> Optional[GLAccount]:
        """Get account by code"""
        return self.accounts.get(account_code)
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[GLAccount]:
        """Get all accounts of a specific type"""
        return [
            acc for acc in self.accounts.values()
            if acc.account_type == account_type
        ]
    
    def get_accounts_by_domain(self, domain: DataMeshDomain) -> List[GLAccount]:
        """Get all accounts owned by a data mesh domain"""
        return [
            acc for acc in self.accounts.values()
            if acc.domain_owner == domain
        ]
    
    def get_hierarchy(self, parent_code: Optional[str] = None) -> List[GLAccount]:
        """Get account hierarchy"""
        if parent_code is None:
            # Return top level accounts
            return [
                acc for acc in self.accounts.values()
                if acc.parent_account is None
            ]
        else:
            # Return child accounts
            return [
                acc for acc in self.accounts.values()
                if acc.parent_account == parent_code
            ]
    
    def ai_suggest_account(
        self,
        description: str,
        amount: Decimal,
        transaction_type: str
    ) -> Optional[str]:
        """
        Use AI to suggest the appropriate GL account
        Returns account code with highest confidence
        """
        # Simple keyword matching (would use ML model in production)
        description_lower = description.lower()
        
        best_match = None
        best_score = 0.0
        
        for account in self.accounts.values():
            if not account.auto_categorization_enabled:
                continue
            
            score = 0.0
            for keyword in account.common_keywords:
                if keyword.lower() in description_lower:
                    score += 1.0
            
            # Boost score for transaction type match
            if transaction_type == "deposit" and account.account_type == AccountType.LIABILITY:
                score += 0.5
            elif transaction_type == "loan" and account.account_code.startswith("12"):
                score += 0.5
            elif transaction_type == "fee" and "fee" in account.account_name.lower():
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = account.account_code
        
        return best_match if best_score > 0 else None
    
    def add_mapping(
        self,
        product_type: str,
        transaction_type: str,
        debit_account: str,
        credit_account: str,
        conditions: Optional[Dict[str, Any]] = None
    ) -> AccountMapping:
        """Add account mapping for product transaction"""
        mapping_id = f"MAP-{len(self.mappings) + 1:04d}"
        
        mapping = AccountMapping(
            mapping_id=mapping_id,
            product_type=product_type,
            transaction_type=transaction_type,
            debit_account=debit_account,
            credit_account=credit_account,
            conditions=conditions or {}
        )
        
        self.mappings.append(mapping)
        return mapping
    
    def get_mapping(
        self,
        product_type: str,
        transaction_type: str
    ) -> Optional[AccountMapping]:
        """Get account mapping for a transaction"""
        for mapping in self.mappings:
            if (mapping.product_type == product_type and
                mapping.transaction_type == transaction_type and
                mapping.active):
                return mapping
        return None


# ============================================================================
# Global Chart of Accounts
# ============================================================================

_chart_of_accounts: Optional[ChartOfAccounts] = None

def get_chart_of_accounts() -> ChartOfAccounts:
    """Get the singleton chart of accounts"""
    global _chart_of_accounts
    if _chart_of_accounts is None:
        _chart_of_accounts = ChartOfAccounts()
    return _chart_of_accounts
