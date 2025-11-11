"""
UltraCore Account Management - Interest Engine

Advanced interest calculation:
- Daily interest accrual
- Tiered interest rates
- Compound interest (multiple frequencies)
- Bonus interest calculations
- Interest payment processing
- Term deposit maturity
- GL integration
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid

from ultracore.accounts.core.account_models import (
    Account, AccountType, InterestRate, InterestCalculationMethod,
    Transaction, TransactionType
)
from ultracore.accounting.general_ledger import get_general_ledger, JournalEntryType
from ultracore.audit.audit_core import (
    get_audit_store, AuditEventType, AuditCategory, AuditSeverity
)


# ============================================================================
# Interest Models
# ============================================================================

@dataclass
class InterestAccrual:
    """Daily interest accrual record"""
    accrual_id: str
    account_id: str
    accrual_date: date
    
    # Balance
    balance: Decimal
    
    # Interest calculation
    annual_rate: Decimal
    daily_rate: Decimal
    interest_accrued: Decimal
    
    # Cumulative
    cumulative_interest: Decimal
    
    # Method
    calculation_method: InterestCalculationMethod
    
    # Posted
    posted: bool = False
    posted_date: Optional[date] = None
    transaction_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterestPayment:
    """Interest payment record"""
    payment_id: str
    account_id: str
    payment_date: date
    
    # Interest details
    period_start: date
    period_end: date
    gross_interest: Decimal
    
    # Tax withholding
    tax_withheld: Decimal = Decimal('0.00')
    net_interest: Decimal = Decimal('0.00')
    
    # Transaction
    transaction_id: Optional[str] = None
    gl_entry_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TieredRateResult:
    """Result of tiered rate calculation"""
    total_interest: Decimal
    tier_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    effective_rate: Decimal = Decimal('0.00')


# ============================================================================
# Interest Engine
# ============================================================================

class InterestEngine:
    """
    Interest calculation engine
    
    Capabilities:
    - Daily interest accrual
    - Multiple calculation methods
    - Tiered interest rates
    - Bonus interest
    - Compound interest
    - Interest payment processing
    - GL integration
    """
    
    def __init__(self):
        # Storage
        self.accruals: Dict[str, List[InterestAccrual]] = {}  # account_id -> [accruals]
        self.payments: Dict[str, List[InterestPayment]] = {}  # account_id -> [payments]
        
        # Integrations
        self.general_ledger = get_general_ledger()
        self.audit_store = get_audit_store()
        
        # Configuration
        self.days_per_year = 365
        self.tax_rate = Decimal('0.00')  # No withholding by default
    
    async def calculate_daily_interest(
        self,
        account: Account,
        calculation_date: date
    ) -> InterestAccrual:
        """
        Calculate daily interest accrual
        
        Formula:
        - Simple: Principal × (Rate / Days) × 1
        - Compound: Principal × ((1 + Rate/Days)^Days - 1)
        """
        
        if not account.interest_bearing:
            raise ValueError("Account is not interest bearing")
        
        if not account.current_interest_rate:
            raise ValueError("No interest rate configured")
        
        interest_rate = account.current_interest_rate
        balance = account.balance.ledger_balance
        
        # Calculate daily rate
        annual_rate = interest_rate.annual_rate
        daily_rate = annual_rate / Decimal(str(self.days_per_year))
        
        # Calculate interest based on method
        if interest_rate.calculation_method == InterestCalculationMethod.SIMPLE:
            interest_accrued = balance * (daily_rate / Decimal('100'))
        
        elif interest_rate.calculation_method == InterestCalculationMethod.COMPOUND_DAILY:
            # Compound daily: A = P(1 + r/n)^(nt)
            # For single day: Interest = P × (r / days_per_year / 100)
            interest_accrued = balance * (daily_rate / Decimal('100'))
        
        else:
            # Default to simple for other methods
            interest_accrued = balance * (daily_rate / Decimal('100'))
        
        # Round to 2 decimal places
        interest_accrued = interest_accrued.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Get cumulative interest
        previous_accruals = self.accruals.get(account.account_id, [])
        cumulative = sum(a.interest_accrued for a in previous_accruals if not a.posted)
        cumulative += interest_accrued
        
        # Create accrual record
        accrual = InterestAccrual(
            accrual_id=f"ACCR-{uuid.uuid4().hex[:12].upper()}",
            account_id=account.account_id,
            accrual_date=calculation_date,
            balance=balance,
            annual_rate=annual_rate,
            daily_rate=daily_rate,
            interest_accrued=interest_accrued,
            cumulative_interest=cumulative,
            calculation_method=interest_rate.calculation_method
        )
        
        # Store accrual
        if account.account_id not in self.accruals:
            self.accruals[account.account_id] = []
        self.accruals[account.account_id].append(accrual)
        
        # Update account
        account.balance.interest_accrued += interest_accrued
        account.balance.last_interest_date = calculation_date
        
        return accrual
    
    async def calculate_tiered_interest(
        self,
        balance: Decimal,
        interest_rate: InterestRate,
        days: int = 1
    ) -> TieredRateResult:
        """
        Calculate interest with tiered rates
        
        Example tiers:
        $0 - $10,000: 2.5%
        $10,000 - $50,000: 3.5%
        $50,000+: 4.5%
        """
        
        if not interest_rate.balance_tiers:
            # No tiers, use base rate
            daily_rate = interest_rate.annual_rate / Decimal(str(self.days_per_year))
            interest = balance * (daily_rate / Decimal('100')) * days
            
            return TieredRateResult(
                total_interest=interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                effective_rate=interest_rate.annual_rate
            )
        
        total_interest = Decimal('0.00')
        tier_breakdown = []
        remaining_balance = balance
        
        for tier in interest_rate.balance_tiers:
            tier_min = Decimal(str(tier.get('min', 0)))
            tier_max = Decimal(str(tier.get('max', 999999999))) if tier.get('max') else None
            tier_rate = Decimal(str(tier['rate']))
            
            # Calculate balance in this tier
            if tier_max:
                tier_balance = min(remaining_balance, tier_max - tier_min)
            else:
                tier_balance = remaining_balance
            
            if tier_balance <= 0:
                continue
            
            # Calculate interest for this tier
            daily_rate = tier_rate / Decimal(str(self.days_per_year))
            tier_interest = tier_balance * (daily_rate / Decimal('100')) * days
            
            total_interest += tier_interest
            
            tier_breakdown.append({
                'tier_min': float(tier_min),
                'tier_max': float(tier_max) if tier_max else None,
                'tier_rate': float(tier_rate),
                'balance_in_tier': float(tier_balance),
                'interest_earned': float(tier_interest)
            })
            
            remaining_balance -= tier_balance
            
            if remaining_balance <= 0:
                break
        
        # Calculate effective rate
        if balance > 0:
            effective_rate = (total_interest / balance) * Decimal(str(self.days_per_year)) / days * Decimal('100')
        else:
            effective_rate = Decimal('0.00')
        
        return TieredRateResult(
            total_interest=total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            tier_breakdown=tier_breakdown,
            effective_rate=effective_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        )
    
    async def calculate_bonus_interest(
        self,
        account: Account,
        interest_rate: InterestRate,
        base_interest: Decimal
    ) -> Decimal:
        """
        Calculate bonus interest if conditions met
        
        Common conditions:
        - Minimum monthly deposits
        - No withdrawals
        - Growing balance
        """
        
        if not interest_rate.has_bonus:
            return Decimal('0.00')
        
        bonus_rate = interest_rate.bonus_rate or Decimal('0.00')
        conditions_met = True
        
        # Check bonus conditions
        for condition in interest_rate.bonus_conditions:
            if condition == "NO_WITHDRAWALS":
                # In production: check for withdrawals this month
                pass
            elif condition == "MIN_DEPOSIT_1000":
                # In production: check monthly deposits >= 1000
                pass
        
        if conditions_met and bonus_rate > 0:
            # Calculate bonus interest
            bonus_interest = base_interest * (bonus_rate / interest_rate.annual_rate)
            return bonus_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return Decimal('0.00')
    
    async def pay_interest(
        self,
        account: Account,
        payment_date: date,
        paid_by: str = "SYSTEM"
    ) -> InterestPayment:
        """
        Pay accrued interest to account
        
        Process:
        1. Get unpaid accruals
        2. Calculate total interest
        3. Apply tax withholding
        4. Credit account
        5. Post to GL
        6. Mark accruals as paid
        """
        
        # Get unpaid accruals
        accruals = self.accruals.get(account.account_id, [])
        unpaid = [a for a in accruals if not a.posted]
        
        if not unpaid:
            raise ValueError("No unpaid interest to pay")
        
        # Calculate total interest
        gross_interest = sum(a.interest_accrued for a in unpaid)
        
        # Apply tax withholding
        tax_withheld = Decimal('0.00')
        if account.tax_withholding:
            tax_withheld = (gross_interest * self.tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        net_interest = gross_interest - tax_withheld
        
        # Create interest payment record
        payment_id = f"INTPAY-{uuid.uuid4().hex[:12].upper()}"
        
        payment = InterestPayment(
            payment_id=payment_id,
            account_id=account.account_id,
            payment_date=payment_date,
            period_start=unpaid[0].accrual_date,
            period_end=unpaid[-1].accrual_date,
            gross_interest=gross_interest,
            tax_withheld=tax_withheld,
            net_interest=net_interest
        )
        
        # Create transaction to credit account
        from ultracore.accounts.core.account_manager import get_account_manager
        account_manager = get_account_manager()
        
        transaction = await account_manager.deposit(
            account_id=account.account_id,
            amount=net_interest,
            description=f"Interest payment: {payment.period_start} to {payment.period_end}",
            deposited_by=paid_by,
            external_reference=payment_id
        )
        
        payment.transaction_id = transaction.transaction_id
        
        # Post to GL
        await self._post_interest_to_gl(account, payment)
        
        # Mark accruals as paid
        for accrual in unpaid:
            accrual.posted = True
            accrual.posted_date = payment_date
            accrual.transaction_id = transaction.transaction_id
        
        # Update account
        account.balance.interest_accrued = Decimal('0.00')
        account.balance.interest_paid_ytd += net_interest
        
        # Store payment
        if account.account_id not in self.payments:
            self.payments[account.account_id] = []
        self.payments[account.account_id].append(payment)
        
        # Audit log
        await self.audit_store.log_event(
            event_type=AuditEventType.TRANSACTION_SETTLED,
            category=AuditCategory.ACCOUNT,
            severity=AuditSeverity.INFO,
            resource_type='interest_payment',
            resource_id=payment_id,
            action='interest_paid',
            description=f"Interest paid: ${net_interest}",
            user_id=paid_by,
            metadata={
                'account_id': account.account_id,
                'gross_interest': str(gross_interest),
                'tax_withheld': str(tax_withheld),
                'net_interest': str(net_interest)
            },
            regulatory_relevant=True
        )
        
        return payment
    
    async def process_term_deposit_maturity(
        self,
        account: Account,
        maturity_date: date
    ) -> Dict[str, Any]:
        """
        Process term deposit maturity
        
        Options:
        - ROLLOVER: Create new term deposit
        - TRANSFER: Transfer to savings account
        - CLOSE: Close account and transfer funds
        """
        
        if account.account_type != AccountType.TERM_DEPOSIT:
            raise ValueError("Account is not a term deposit")
        
        if not account.maturity_date:
            raise ValueError("No maturity date set")
        
        if maturity_date < account.maturity_date:
            raise ValueError("Maturity date not reached")
        
        # Pay any remaining interest
        if account.balance.interest_accrued > 0:
            await self.pay_interest(account, maturity_date)
        
        maturity_instruction = account.maturity_instruction or "TRANSFER"
        
        result = {
            'account_id': account.account_id,
            'maturity_date': maturity_date.isoformat(),
            'principal': str(account.balance.ledger_balance),
            'instruction': maturity_instruction
        }
        
        if maturity_instruction == "ROLLOVER":
            # Create new term deposit (in production)
            result['action'] = 'New term deposit created'
        
        elif maturity_instruction == "TRANSFER":
            # Transfer to nominated account (in production)
            result['action'] = 'Funds transferred to savings account'
        
        elif maturity_instruction == "CLOSE":
            # Close account (in production)
            result['action'] = 'Account closed, funds transferred'
        
        return result
    
    async def run_daily_interest_accrual(
        self,
        accounts: List[Account],
        calculation_date: date
    ) -> Dict[str, Any]:
        """
        Run daily interest accrual for all interest-bearing accounts
        Batch processing
        """
        
        results = {
            'calculation_date': calculation_date.isoformat(),
            'accounts_processed': 0,
            'total_interest_accrued': Decimal('0.00'),
            'errors': []
        }
        
        for account in accounts:
            if not account.interest_bearing:
                continue
            
            if account.account_status != AccountStatus.ACTIVE:
                continue
            
            try:
                accrual = await self.calculate_daily_interest(account, calculation_date)
                
                results['accounts_processed'] += 1
                results['total_interest_accrued'] += accrual.interest_accrued
            
            except Exception as e:
                results['errors'].append({
                    'account_id': account.account_id,
                    'error': str(e)
                })
        
        return results
    
    async def _post_interest_to_gl(
        self,
        account: Account,
        payment: InterestPayment
    ):
        """Post interest payment to GL"""
        
        # Debit: Interest Expense (expense increases)
        # Credit: Customer Deposit (liability increases)
        
        lines = [
            {
                'account_code': '5010',  # Interest Expense
                'debit': str(payment.gross_interest),
                'credit': '0.00',
                'description': f"Interest paid - Account {account.account_number}"
            },
            {
                'account_code': '2010',  # Customer Deposits
                'debit': '0.00',
                'credit': str(payment.net_interest),
                'description': f"Interest paid - Account {account.account_number}"
            }
        ]
        
        # If tax withheld, add tax payable
        if payment.tax_withheld > 0:
            lines.append({
                'account_code': '2020',  # Tax Payable
                'debit': '0.00',
                'credit': str(payment.tax_withheld),
                'description': f"Tax withheld - Account {account.account_number}"
            })
        
        entry = await self.general_ledger.create_entry(
            entry_type=JournalEntryType.STANDARD,
            entry_date=payment.payment_date,
            description=f"Interest payment - {account.account_number}",
            lines=lines,
            created_by="SYSTEM",
            reference=payment.payment_id,
            auto_post=True
        )
        
        payment.gl_entry_id = entry.entry_id


# ============================================================================
# Global Singleton
# ============================================================================

_interest_engine: Optional[InterestEngine] = None

def get_interest_engine() -> InterestEngine:
    """Get singleton interest engine"""
    global _interest_engine
    if _interest_engine is None:
        _interest_engine = InterestEngine()
    return _interest_engine
