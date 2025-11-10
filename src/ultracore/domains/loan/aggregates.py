"""
PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2025 Richelou Pty Ltd. All Rights Reserved.
TuringDynamics Division
"""

from decimal import Decimal
from typing import List
from enum import Enum

class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Loan:
    def __init__(self, loan_id: str):
        self.loan_id = loan_id
        self.status = LoanStatus.PENDING
        self.version = 0
    
    def to_dict(self):
        return {
            "loan_id": self.loan_id,
            "status": self.status.value,
            "version": self.version
        }
