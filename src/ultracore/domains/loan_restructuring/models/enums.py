"""Enumerations for Loan Restructuring - Australian NCCP"""
from enum import Enum


class HardshipReason(str, Enum):
    """Reasons for hardship under Australian NCCP."""
    JOB_LOSS = "job_loss"
    REDUCED_INCOME = "reduced_income"
    ILLNESS_INJURY = "illness_injury"
    FAMILY_BREAKDOWN = "family_breakdown"
    BUSINESS_FAILURE = "business_failure"
    NATURAL_DISASTER = "natural_disaster"
    UNEXPECTED_EXPENSES = "unexpected_expenses"
    OTHER = "other"


class ReliefType(str, Enum):
    """Types of hardship relief."""
    PAYMENT_HOLIDAY = "payment_holiday"
    TERM_EXTENSION = "term_extension"
    INTEREST_RATE_REDUCTION = "interest_rate_reduction"
    PAYMENT_AMOUNT_REDUCTION = "payment_amount_reduction"
    DEBT_CONSOLIDATION = "debt_consolidation"
    ARREARS_CAPITALIZATION = "arrears_capitalization"
    FORBEARANCE = "forbearance"


class RestructuringStatus(str, Enum):
    """Restructuring status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"
    CANCELLED = "cancelled"


class ApplicationStatus(str, Enum):
    """Hardship application status."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
