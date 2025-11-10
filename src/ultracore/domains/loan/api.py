"""
PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2025 Richelou Pty Ltd. All Rights Reserved.
TuringDynamics Division
"""

from fastapi import APIRouter
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter()

class LoanApplicationRequest(BaseModel):
    customer_id: str
    amount: Decimal
    term_months: int
    purpose: str

@router.post("/")
async def apply_for_loan(request: LoanApplicationRequest):
    return {
        "message": "Loan application received",
        "customer_id": request.customer_id,
        "amount": float(request.amount)
    }

@router.get("/{loan_id}")
async def get_loan(loan_id: str):
    return {"loan_id": loan_id, "status": "pending"}
