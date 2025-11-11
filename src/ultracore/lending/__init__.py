"""
UltraCore Lending Module

Complete loan lifecycle management
"""

__version__ = "1.0.0"

from ultracore.lending.loan_models import (
    Loan,
    LoanType,
    LoanStatus,
    RepaymentFrequency,
    InterestType,
    LoanApplication,
    Collateral
)

from ultracore.lending.loan_manager import (
    get_loan_manager,
    LoanManager
)

from ultracore.lending.underwriting import (
    get_underwriting_engine,
    UnderwritingEngine,
    CreditScore,
    RiskRating
)

from ultracore.lending.servicing import (
    get_loan_servicing,
    LoanServicing,
    PaymentSchedule,
    Payment
)

__all__ = [
    # Models
    'Loan',
    'LoanType',
    'LoanStatus',
    'RepaymentFrequency',
    'InterestType',
    'LoanApplication',
    'Collateral',
    
    # Manager
    'get_loan_manager',
    'LoanManager',
    
    # Underwriting
    'get_underwriting_engine',
    'UnderwritingEngine',
    'CreditScore',
    'RiskRating',
    
    # Servicing
    'get_loan_servicing',
    'LoanServicing',
    'PaymentSchedule',
    'Payment',
]
