"""Fixed Deposits API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date

from ..commands import (
    SubmitFixedDepositApplicationCommand,
    ApproveFixedDepositCommand,
    ActivateFixedDepositCommand
)
from ..models import (
    FixedDepositAccount,
    FixedDepositApplication,
    FixedDepositProduct
)
from ..services import FixedDepositService
from ultracore.api.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/fixed-deposits", tags=["Fixed Deposits"])


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_application(
    command: SubmitFixedDepositApplicationCommand,
    current_user = Depends(get_current_user),
    fd_service: FixedDepositService = Depends()
):
    """
    Submit new fixed deposit application.
    
    Publishes: FixedDepositApplicationSubmittedEvent to Kafka
    """
    try:
        application = await fd_service.submit_application(
            customer_id=command.customer_id,
            product=None,  # Get from product service
            deposit_amount=command.deposit_amount,
            term_months=command.term_months,
            source_account_id=command.source_account_id,
            maturity_instruction=command.maturity_instruction,
            submitted_by=command.submitted_by
        )
        
        return {
            "application_id": application.application_id,
            "status": application.status,
            "message": "Application submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    command: ApproveFixedDepositCommand,
    current_user = Depends(get_current_user),
    fd_service: FixedDepositService = Depends()
):
    """
    Approve fixed deposit application (maker-checker).
    
    Publishes: FixedDepositApprovedEvent to Kafka
    """
    await fd_service.approve_application(
        application_id=application_id,
        approved_by=command.approved_by,
        approval_notes=command.approval_notes
    )
    
    return {"message": "Application approved", "application_id": application_id}


@router.post("/applications/{application_id}/activate")
async def activate_account(
    application_id: str,
    command: ActivateFixedDepositCommand,
    current_user = Depends(get_current_user),
    fd_service: FixedDepositService = Depends()
):
    """
    Activate fixed deposit account.
    
    Publishes: FixedDepositActivatedEvent to Kafka
    """
    account = await fd_service.activate_account(
        application_id=application_id,
        activation_date=command.activation_date,
        source_account_id="",  # From command
        certificate_number=command.certificate_number
    )
    
    return {
        "account_id": account.account_id,
        "account_number": account.account_number,
        "status": account.status,
        "message": "Account activated successfully"
    }


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: str,
    current_user = Depends(get_current_user),
    fd_service: FixedDepositService = Depends()
) -> FixedDepositAccount:
    """
    Get fixed deposit account details (reconstructed from events).
    
    Event sourcing: Account state is rebuilt from event stream.
    """
    account = await fd_service.get_account(account_id)
    return account


@router.get("/products")
async def list_products(
    current_user = Depends(get_current_user)
) -> List[FixedDepositProduct]:
    """List available fixed deposit products."""
    # Query product catalog
    products = []
    return products


@router.get("/rates")
async def get_current_rates(
    term_months: Optional[int] = None,
    amount: Optional[float] = None
):
    """
    Get current fixed deposit interest rates.
    
    Public endpoint - no authentication required.
    """
    rates = {
        3: 4.5,
        6: 4.75,
        12: 5.0,
        24: 5.25,
        36: 5.5
    }
    
    if term_months and term_months in rates:
        return {
            "term_months": term_months,
            "interest_rate": rates[term_months],
            "effective_date": date.today()
        }
    
    return {
        "rates": rates,
        "effective_date": date.today(),
        "note": "Rates are indicative and may vary by amount"
    }
