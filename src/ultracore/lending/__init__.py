"""UltraCore Loan Management System"""

# Origination
from ultracore.lending.origination.loan_application import get_application_manager
from ultracore.lending.origination.underwriting_engine import get_underwriting_engine

# Servicing
from ultracore.lending.servicing.loan_account import get_loan_account_manager
from ultracore.lending.servicing.amortization_engine import get_amortization_engine
from ultracore.lending.servicing.interest_calculator import get_interest_calculator
from ultracore.lending.servicing.payment_processor import get_payment_processor

# Collections
from ultracore.lending.collections.delinquency_tracker import get_delinquency_tracker
from ultracore.lending.collections.collections_manager import get_collections_manager

# Provisioning
from ultracore.lending.provisioning.ifrs9_engine import (
    get_ifrs9_staging_engine,
    get_provision_manager
)

__all__ = [
    'get_application_manager',
    'get_underwriting_engine',
    'get_loan_account_manager',
    'get_amortization_engine',
    'get_interest_calculator',
    'get_payment_processor',
    'get_delinquency_tracker',
    'get_collections_manager',
    'get_ifrs9_staging_engine',
    'get_provision_manager'
]
