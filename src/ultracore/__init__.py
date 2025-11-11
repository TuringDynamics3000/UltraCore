"""
UltraCore Banking Platform

A complete, AI-native core banking platform with:
- Customer Management (KYC/AML, Graph, AI Agents)
- Account Management (Deposits, Transactions, Payment Rails)
- Loan Management (Lending, Servicing, Collections)
- General Ledger (Accounting)
- Audit & Compliance (Regulatory)

Version: 1.0.0
License: Proprietary
"""

__version__ = "1.0.0"
__author__ = "UltraCore Team"
__license__ = "Proprietary"

# Package metadata
__all__ = [
    'accounting',
    'audit',
    'lending',
    'customers',
    'accounts',
]

# Core imports for convenience
from ultracore.accounting.general_ledger import get_general_ledger
from ultracore.audit.audit_core import get_audit_store
from ultracore.customers.core.customer_manager import get_customer_manager
from ultracore.accounts.core.account_manager import get_account_manager

# Version info
def get_version():
    """Get UltraCore version"""
    return __version__

# System info
def get_info():
    """Get system information"""
    return {
        'version': __version__,
        'modules': __all__,
        'author': __author__,
        'license': __license__
    }
