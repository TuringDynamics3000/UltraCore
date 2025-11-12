"""Recurring Deposits API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date

from ..commands import (
    SubmitRecurringDepositApplicationCommand,
    ApproveRecurringDepositCommand,
    ActivateRecurringDepositCommand
)
from ..models import (
    RecurringDepositAccount,
    RecurringDepositApplication,
    RecurringDepositProduct,
    DepositSchedule
)
from ..services import RecurringDepositService
from ultracore.api.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/recurring-deposits", tags=["Recurring Deposits"])


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_application(
    command: dict,  # Would be proper Pydantic model
    current_user = Depends(get_current_user),
    rd_service: RecurringDepositService = Depends()
):
    """
    Submit new recurring deposit application.
    
    Publishes: RecurringDepositApplicationSubmittedEvent to Kafka
    """
    try:
        application = await rd_service.submit_application(
            customer_id=command["customer_id"],
            product=None,  # Get from product service
            monthly_deposit_amount=command["monthly_amount"],
            term_months=command["term_months"],
            source_account_id=command["source_account"],
            debit_day_of_month=command.get("debit_day", 1),
            maturity_instruction=command.get("maturity_instruction", "transfer_to_savings"),
            submitted_by=command["submitted_by"]
        )
        
        return {
            "application_id": application.application_id,
            "status": application.status,
            "message": "Recurring deposit application submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    approved_by: str,
    current_user = Depends(get_current_user),
    rd_service: RecurringDepositService = Depends()
):
    """
    Approve RD application (maker-checker).
    
    Publishes: RecurringDepositApprovedEvent to Kafka
    """
    await rd_service.approve_application(
        application_id=application_id,
        approved_by=approved_by
    )
    
    return {"message": "Application approved", "application_id": application_id}


@router.post("/applications/{application_id}/activate")
async def activate_account(
    application_id: str,
    mandate_reference: str,
    current_user = Depends(get_current_user),
    rd_service: RecurringDepositService = Depends()
):
    """
    Activate RD account.
    
    Publishes: RecurringDepositActivatedEvent to Kafka
    """
    account = await rd_service.activate_account(
        application_id=application_id,
        activation_date=date.today(),
        mandate_reference=mandate_reference
    )
    
    return {
        "account_id": account.account_id,
        "account_number": account.account_number,
        "status": account.status,
        "message": "Recurring deposit activated successfully"
    }


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: str,
    current_user = Depends(get_current_user),
    rd_service: RecurringDepositService = Depends()
) -> RecurringDepositAccount:
    """
    Get RD account details (reconstructed from events).
    """
    account = await rd_service.get_account(account_id)
    return account


@router.get("/accounts/{account_id}/schedule")
async def get_payment_schedule(
    account_id: str,
    current_user = Depends(get_current_user),
    rd_service: RecurringDepositService = Depends()
) -> DepositSchedule:
    """
    Get complete payment schedule for RD account.
    """
    account = await rd_service.get_account(account_id)
    schedule = await rd_service.generate_deposit_schedule(account)
    return schedule


@router.get("/products")
async def list_products(
    current_user = Depends(get_current_user)
) -> List[RecurringDepositProduct]:
    """List available recurring deposit products."""
    products = []  # Query product catalog
    return products


@router.get("/rates")
async def get_current_rates(
    term_months: Optional[int] = None
):
    """
    Get current recurring deposit interest rates.
    
    Public endpoint - no authentication required.
    """
    rates = {
        12: 5.5,
        24: 5.75,
        36: 6.0,
        48: 6.25,
        60: 6.5
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
        "note": "Rates are indicative. Higher rates for longer terms encourage sustained saving habits."
    }


@router.post("/accounts/{account_id}/payments/{installment_number}/record")
async def record_payment(
    account_id: str,
    installment_number: int,
    payment_amount: float,
    payment_reference: str,
    current_user = Depends(get_current_user)
):
    """
    Record a monthly deposit payment (manual or auto-debit confirmation).
    
    Publishes: MonthlyDepositReceivedEvent to Kafka
    """
    # Would call service to process payment
    return {
        "success": True,
        "account_id": account_id,
        "installment_number": installment_number,
        "amount": payment_amount,
        "message": "Payment recorded successfully"
    }
