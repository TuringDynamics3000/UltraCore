"""Enumerations for Fixed Deposits Domain"""
from enum import Enum


class FixedDepositStatus(str, Enum):
    """Fixed deposit account status."""
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    MATURED = "matured"
    CLOSED = "closed"
    PREMATURELY_CLOSED = "prematurely_closed"
    REJECTED = "rejected"


class InterestCalculationMethod(str, Enum):
    """Interest calculation methods."""
    SIMPLE = "simple"
    COMPOUND_MONTHLY = "compound_monthly"
    COMPOUND_QUARTERLY = "compound_quarterly"
    COMPOUND_HALF_YEARLY = "compound_half_yearly"
    COMPOUND_ANNUAL = "compound_annual"


class MaturityInstructionType(str, Enum):
    """Instructions for maturity proceeds."""
    TRANSFER_TO_SAVINGS = "transfer_to_savings"
    RENEW_DEPOSIT = "renew_deposit"
    TRANSFER_TO_ACCOUNT = "transfer_to_account"
    HOLD_FOR_WITHDRAWAL = "hold_for_withdrawal"


class PrematureClosurePenaltyType(str, Enum):
    """Penalty calculation methods for premature closure."""
    PERCENTAGE_OF_INTEREST = "percentage_of_interest"
    FLAT_FEE = "flat_fee"
    REDUCED_INTEREST_RATE = "reduced_interest_rate"
    FORFEIT_ALL_INTEREST = "forfeit_all_interest"
    NO_PENALTY = "no_penalty"


class InterestPostingFrequency(str, Enum):
    """Frequency of interest posting."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"
    AT_MATURITY = "at_maturity"
