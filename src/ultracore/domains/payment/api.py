"""
Payment Domain API
"""
from fastapi import APIRouter, HTTPException
from decimal import Decimal
import uuid

from ultracore.domains.payment.aggregate import (
    PaymentAggregate, CreatePaymentRequest, PaymentType
)

router = APIRouter()


@router.post('/')
async def create_payment(request: CreatePaymentRequest):
    '''Create and process a payment'''
    payment_id = f'PAY-{str(uuid.uuid4())[:8]}'
    
    payment = PaymentAggregate(payment_id)
    
    await payment.initiate_payment(
        from_account_id=request.from_account_id,
        to_account_id=request.to_account_id,
        amount=Decimal(str(request.amount)),
        payment_type=request.payment_type,
        description=request.description,
        reference=request.reference
    )
    
    fraud_passed = await payment.fraud_check()
    
    if not fraud_passed:
        return {
            'payment_id': payment_id,
            'status': 'FRAUD_HOLD',
            'fraud_score': payment.fraud_score
        }
    
    try:
        await payment.process()
    except ValueError as e:
        return {
            'payment_id': payment_id,
            'status': 'FAILED',
            'message': str(e)
        }
    
    return {
        'payment_id': payment_id,
        'status': 'COMPLETED',
        'amount': str(request.amount)
    }


@router.get('/{payment_id}')
async def get_payment(payment_id: str):
    '''Get payment details'''
    payment = PaymentAggregate(payment_id)
    await payment.load_from_events()
    
    if not payment.from_account_id:
        raise HTTPException(status_code=404, detail='Payment not found')
    
    return {
        'payment_id': payment.payment_id,
        'from_account': payment.from_account_id,
        'to_account': payment.to_account_id,
        'amount': str(payment.amount),
        'status': payment.status.value
    }
