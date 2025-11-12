"""Data Mesh Products for Recurring Deposits"""
from .rd_accounts_product import RecurringDepositsAccountsProduct
from .rd_payments_product import RecurringDepositPaymentsProduct
from .rd_analytics_product import RecurringDepositAnalyticsProduct

__all__ = [
    "RecurringDepositsAccountsProduct",
    "RecurringDepositPaymentsProduct",
    "RecurringDepositAnalyticsProduct",
]
