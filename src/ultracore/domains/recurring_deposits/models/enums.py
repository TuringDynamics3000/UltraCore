"""Enumerations for Recurring Deposits Domain"""
from enum import Enum


class RecurringDepositStatus(str, Enum):
    """Recurring deposit account status."""
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    MATURED = "matured"
    CLOSED = "closed"
    PREMATURELY_CLOSED = "prematurely_closed"
    REJECTED = "rejected"
    DEFAULTED = "defaulted"  # Too many missed deposits


class DepositFrequency(str, Enum):
    """Frequency of recurring deposits."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class MaturityInstructionType(str, Enum):
    """Instructions for maturity proceeds."""
    TRANSFER_TO_SAVINGS = "transfer_to_savings"
    CONVERT_TO_FD = "convert_to_fd"
    TRANSFER_TO_ACCOUNT = "transfer_to_account"
    HOLD_FOR_WITHDRAWAL = "hold_for_withdrawal"
    OPEN_NEW_RD = "open_new_rd"


class PenaltyType(str, Enum):
    """Penalty types for RD."""
    MISSED_DEPOSIT_FEE = "missed_deposit_fee"
    PREMATURE_CLOSURE = "premature_closure"
    FORFEIT_INTEREST = "forfeit_interest"
    REDUCED_INTEREST_RATE = "reduced_interest_rate"
    NO_PENALTY = "no_penalty"


class InstallmentStatus(str, Enum):
    """Status of individual deposit installment."""
    PENDING = "pending"
    DUE = "due"
    PAID = "paid"
    LATE = "late"
    MISSED = "missed"
    WAIVED = "waived"
