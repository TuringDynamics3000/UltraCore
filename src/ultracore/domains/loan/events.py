"""
PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2025 Richelou Pty Ltd. All Rights Reserved.
TuringDynamics Division
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

@dataclass
class Event:
    event_id: str
    aggregate_id: str
    timestamp: datetime
    version: int

@dataclass
class LoanAppliedEvent(Event):
    customer_id: str
    amount: Decimal
    term_months: int
    purpose: str
