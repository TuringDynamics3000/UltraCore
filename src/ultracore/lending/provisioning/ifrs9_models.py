"""
UltraCore Loan Management - IFRS 9 Models

IFRS 9 / AASB 9 Expected Credit Loss models:
- Stage classification
- PD/LGD/EAD parameters
- Provision calculations
- Stage transitions
- Event sourcing integration
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal


# ============================================================================
# IFRS 9 Enums
# ============================================================================

class IFRS9Stage(str, Enum):
    """IFRS 9 impairment stages"""
    STAGE_1 = "STAGE_1"  # 12-month ECL
    STAGE_2 = "STAGE_2"  # Lifetime ECL (not credit-impaired)
    STAGE_3 = "STAGE_3"  # Lifetime ECL (credit-impaired)
    POCI = "POCI"  # Purchased or Originated Credit Impaired


class SignificantIncreaseIndicator(str, Enum):
    """Indicators of significant increase in credit risk"""
    DPD_30_PLUS = "DPD_30_PLUS"  # 30+ days past due
    INTERNAL_RATING_DOWNGRADE = "INTERNAL_RATING_DOWNGRADE"
    EXTERNAL_RATING_DOWNGRADE = "EXTERNAL_RATING_DOWNGRADE"
    FORBEARANCE = "FORBEARANCE"
    WATCHLIST = "WATCHLIST"
    COVENANT_BREACH = "COVENANT_BREACH"
    ADVERSE_CHANGE = "ADVERSE_CHANGE"


class CreditImpairedIndicator(str, Enum):
    """Indicators of credit impairment (Stage 3)"""
    DPD_90_PLUS = "DPD_90_PLUS"  # 90+ days past due
    BANKRUPTCY = "BANKRUPTCY"
    RESTRUCTURING = "RESTRUCTURING"
    DEFAULT = "DEFAULT"
    ENFORCEMENT = "ENFORCEMENT"


class ProvisionEventType(str, Enum):
    """Types of provision events (for event sourcing)"""
    PROVISION_CALCULATED = "PROVISION_CALCULATED"
    PROVISION_POSTED = "PROVISION_POSTED"
    PROVISION_REVERSED = "PROVISION_REVERSED"
    STAGE_CHANGED = "STAGE_CHANGED"
    WRITE_OFF_APPLIED = "WRITE_OFF_APPLIED"
    RECOVERY_RECORDED = "RECOVERY_RECORDED"


class ProvisionMethod(str, Enum):
    """ECL calculation method"""
    INDIVIDUAL = "INDIVIDUAL"  # Individual assessment
    COLLECTIVE = "COLLECTIVE"  # Collective/portfolio assessment
    SIMPLIFIED = "SIMPLIFIED"  # Simplified approach


# ============================================================================
# IFRS 9 Data Models
# ============================================================================

@dataclass
class PDLGDEADParameters:
    """
    Probability of Default (PD), Loss Given Default (LGD), 
    Exposure at Default (EAD) parameters
    """
    parameter_id: str
    loan_account_id: str
    
    # Stage
    stage: IFRS9Stage
    
    # PD (Probability of Default) - %
    pd_12_month: Decimal  # 12-month PD for Stage 1
    pd_lifetime: Decimal  # Lifetime PD for Stage 2/3
    
    # LGD (Loss Given Default) - %
    lgd: Decimal  # Expected loss given default occurs
    
    # EAD (Exposure at Default)
    ead: Decimal  # Outstanding balance at default
    
    # Effective Interest Rate
    eir: Decimal  # For discounting
    
    # Time horizon
    time_to_maturity_years: Decimal
    
    # Credit risk grade/rating
    credit_grade: Optional[str] = None
    internal_rating: Optional[str] = None
    
    # Model used
    model_version: str = ""
    calculation_date: date = field(default_factory=date.today)
    
    # Scenarios (for forward-looking)
    base_case_weight: Decimal = Decimal('0.50')
    optimistic_weight: Decimal = Decimal('0.25')
    pessimistic_weight: Decimal = Decimal('0.25')
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StageClassification:
    """IFRS 9 stage classification"""
    classification_id: str
    loan_account_id: str
    
    # Stage
    current_stage: IFRS9Stage
    previous_stage: Optional[IFRS9Stage] = None
    
    # Stage change date
    stage_change_date: Optional[date] = None
    days_in_stage: int = 0
    
    # Indicators
    sicr_indicators: List[SignificantIncreaseIndicator] = field(default_factory=list)
    impairment_indicators: List[CreditImpairedIndicator] = field(default_factory=list)
    
    # Metrics
    days_past_due: int = 0
    lifetime_pd_change_percent: Optional[Decimal] = None
    
    # Flags
    forbearance_granted: bool = False
    on_watchlist: bool = False
    
    # Assessment
    assessment_date: date = field(default_factory=date.today)
    assessed_by: str = "SYSTEM"
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


@dataclass
class ECLCalculation:
    """Expected Credit Loss calculation result"""
    calculation_id: str
    loan_account_id: str
    
    # Stage
    stage: IFRS9Stage
    
    # Parameters used
    pd: Decimal
    lgd: Decimal
    ead: Decimal
    eir: Decimal
    
    # Calculated ECL
    ecl_amount: Decimal
    
    # Breakdown
    ecl_principal: Decimal = Decimal('0.00')
    ecl_interest: Decimal = Decimal('0.00')
    
    # Discounting
    discount_factor: Decimal = Decimal('1.00')
    discounted_ecl: Decimal = Decimal('0.00')
    
    # Time period
    time_horizon: str = "12_MONTH"  # 12_MONTH or LIFETIME
    
    # Method
    calculation_method: ProvisionMethod
    
    # Scenarios (probability-weighted)
    base_case_ecl: Optional[Decimal] = None
    optimistic_ecl: Optional[Decimal] = None
    pessimistic_ecl: Optional[Decimal] = None
    
    # Calculation date
    calculation_date: date = field(default_factory=date.today)
    
    # Metadata
    model_version: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoanProvision:
    """Loan loss provision record"""
    provision_id: str
    loan_account_id: str
    
    # Stage
    stage: IFRS9Stage
    
    # Provision amounts
    provision_amount: Decimal
    cumulative_provision: Decimal
    
    # Movement from previous
    provision_increase: Decimal = Decimal('0.00')
    provision_decrease: Decimal = Decimal('0.00')
    provision_movement: Decimal = Decimal('0.00')
    
    # Breakdown
    specific_provision: Decimal = Decimal('0.00')
    collective_provision: Decimal = Decimal('0.00')
    
    # Effective date
    effective_date: date
    
    # Posted to GL
    posted: bool = False
    posting_date: Optional[date] = None
    journal_entry_id: Optional[str] = None
    
    # Reversal
    reversed: bool = False
    reversal_provision_id: Optional[str] = None
    
    # Metadata
    created_by: str = "SYSTEM"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvisionEvent:
    """
    Event-sourced provision event
    Immutable record of all provision activities
    """
    event_id: str
    event_type: ProvisionEventType
    event_timestamp: datetime
    
    # Aggregate
    loan_account_id: str
    provision_id: Optional[str] = None
    
    # Event data
    event_data: Dict[str, Any] = field(default_factory=dict)
    
    # Stage information
    previous_stage: Optional[IFRS9Stage] = None
    new_stage: Optional[IFRS9Stage] = None
    
    # Amounts
    previous_provision: Optional[Decimal] = None
    new_provision: Optional[Decimal] = None
    provision_movement: Optional[Decimal] = None
    
    # GL integration
    journal_entry_id: Optional[str] = None
    
    # Causation
    caused_by: str = "SYSTEM"
    reason: Optional[str] = None
    
    # Correlation (for event tracing)
    correlation_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PortfolioProvision:
    """Portfolio-level provision summary"""
    portfolio_id: str
    calculation_date: date
    
    # Stage breakdown
    stage_1_count: int = 0
    stage_1_exposure: Decimal = Decimal('0.00')
    stage_1_provision: Decimal = Decimal('0.00')
    
    stage_2_count: int = 0
    stage_2_exposure: Decimal = Decimal('0.00')
    stage_2_provision: Decimal = Decimal('0.00')
    
    stage_3_count: int = 0
    stage_3_exposure: Decimal = Decimal('0.00')
    stage_3_provision: Decimal = Decimal('0.00')
    
    # Totals
    total_count: int = 0
    total_exposure: Decimal = Decimal('0.00')
    total_provision: Decimal = Decimal('0.00')
    
    # Coverage ratios
    stage_1_coverage_ratio: Decimal = Decimal('0.00')
    stage_2_coverage_ratio: Decimal = Decimal('0.00')
    stage_3_coverage_ratio: Decimal = Decimal('0.00')
    total_coverage_ratio: Decimal = Decimal('0.00')
    
    # Movement
    provision_movement: Decimal = Decimal('0.00')
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_coverage_ratios(self):
        """Calculate provision coverage ratios"""
        if self.stage_1_exposure > 0:
            self.stage_1_coverage_ratio = (self.stage_1_provision / self.stage_1_exposure) * Decimal('100')
        
        if self.stage_2_exposure > 0:
            self.stage_2_coverage_ratio = (self.stage_2_provision / self.stage_2_exposure) * Decimal('100')
        
        if self.stage_3_exposure > 0:
            self.stage_3_coverage_ratio = (self.stage_3_provision / self.stage_3_exposure) * Decimal('100')
        
        if self.total_exposure > 0:
            self.total_coverage_ratio = (self.total_provision / self.total_exposure) * Decimal('100')


# ============================================================================
# GL Account Mapping for Provisions
# ============================================================================

@dataclass
class ProvisionGLAccounts:
    """GL account mapping for loan provisions"""
    
    # Provision expense accounts (P&L impact)
    stage_1_expense: str = "5800"  # Provision Expense - Stage 1
    stage_2_expense: str = "5810"  # Provision Expense - Stage 2
    stage_3_expense: str = "5820"  # Provision Expense - Stage 3
    
    # Provision liability accounts (Balance Sheet)
    stage_1_liability: str = "2500"  # Provision for Credit Losses - Stage 1
    stage_2_liability: str = "2510"  # Provision for Credit Losses - Stage 2
    stage_3_liability: str = "2520"  # Provision for Credit Losses - Stage 3
    
    # Write-off accounts
    writeoff_expense: str = "5830"  # Loan Write-off Expense
    
    # Recovery accounts
    recovery_income: str = "4400"  # Recovery Income
    
    def get_expense_account(self, stage: IFRS9Stage) -> str:
        """Get expense account for stage"""
        if stage == IFRS9Stage.STAGE_1:
            return self.stage_1_expense
        elif stage == IFRS9Stage.STAGE_2:
            return self.stage_2_expense
        elif stage == IFRS9Stage.STAGE_3:
            return self.stage_3_expense
        return self.stage_3_expense  # Default to stage 3
    
    def get_liability_account(self, stage: IFRS9Stage) -> str:
        """Get liability account for stage"""
        if stage == IFRS9Stage.STAGE_1:
            return self.stage_1_liability
        elif stage == IFRS9Stage.STAGE_2:
            return self.stage_2_liability
        elif stage == IFRS9Stage.STAGE_3:
            return self.stage_3_liability
        return self.stage_3_liability  # Default to stage 3
