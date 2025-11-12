"""Data Mesh Products for Fixed Deposits"""
from .fd_accounts_product import FixedDepositsAccountsProduct
from .fd_transactions_product import FixedDepositTransactionsProduct
from .fd_analytics_product import FixedDepositAnalyticsProduct

__all__ = [
    "FixedDepositsAccountsProduct",
    "FixedDepositTransactionsProduct",
    "FixedDepositAnalyticsProduct",
]
