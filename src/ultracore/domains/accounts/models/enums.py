"""Enumerations for Accounts Domain"""
from enum import Enum


class AccountType(str, Enum):
    """Account types in Australian banking."""
    TRANSACTIONAL = "transactional"  # Everyday transaction account
    SAVINGS = "savings"  # Interest-bearing savings
    TERM_DEPOSIT = "term_deposit"  # Fixed term (handled in separate module)


class AccountStatus(str, Enum):
    """Account status."""
    PENDING = "pending"  # Awaiting activation
    ACTIVE = "active"  # Operational
    DORMANT = "dormant"  # Inactive (12+ months)
    FROZEN = "frozen"  # Temporarily suspended
    CLOSED = "closed"  # Permanently closed


class TransactionType(str, Enum):
    """Transaction types."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"
    INTEREST_CREDIT = "interest_credit"
    FEE_CHARGE = "fee_charge"
    PAYMENT_NPP = "payment_npp"  # NPP payment
    PAYMENT_BPAY = "payment_bpay"  # BPAY payment
    PAYMENT_SWIFT = "payment_swift"  # International SWIFT
    DIRECT_DEBIT = "direct_debit"
    CARD_PURCHASE = "card_purchase"
    CARD_WITHDRAWAL = "card_withdrawal"
    REVERSAL = "reversal"


class TransactionStatus(str, Enum):
    """Transaction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"
