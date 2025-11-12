"""Loan Restructuring Domain Events - Australian NCCP Compliant"""
from .base import LoanRestructuringEvent
from .hardship import (
    HardshipApplicationSubmittedEvent,
    HardshipApplicationApprovedEvent,
    HardshipApplicationRejectedEvent,
    PaymentHolidayGrantedEvent,
    PaymentHolidayEndedEvent
)
from .modifications import (
    TermExtensionAppliedEvent,
    InterestRateModifiedEvent,
    PaymentAmountReducedEvent,
    DebtConsolidationCompletedEvent,
    RestructuringCompletedEvent
)
from .monitoring import (
    RestructuredLoanDefaultedEvent,
    RestructuringSuccessConfirmedEvent,
    FinancialCounsellingReferredEvent
)

__all__ = [
    "LoanRestructuringEvent",
    "HardshipApplicationSubmittedEvent",
    "HardshipApplicationApprovedEvent",
    "HardshipApplicationRejectedEvent",
    "PaymentHolidayGrantedEvent",
    "PaymentHolidayEndedEvent",
    "TermExtensionAppliedEvent",
    "InterestRateModifiedEvent",
    "PaymentAmountReducedEvent",
    "DebtConsolidationCompletedEvent",
    "RestructuringCompletedEvent",
    "RestructuredLoanDefaultedEvent",
    "RestructuringSuccessConfirmedEvent",
    "FinancialCounsellingReferredEvent",
]
