"""
Account Domain API
"""
from fastapi import APIRouter, HTTPException
from decimal import Decimal
import uuid

from ultracore.domains.account.aggregate import (
    AccountAggregate, CreateAccountRequest, TransactionRequest, AccountType
)

router = APIRouter()


@router.post('/')
async def create_account(request: CreateAccountRequest):
    '''
    Create a new bank account
    
    Types: SAVINGS, CHECKING, TERM_DEPOSIT
    '''
    account_id = f'ACC-{str(uuid.uuid4())[:8]}'
    
    account = AccountAggregate(account_id)
    await account.create_account(
        client_id=request.client_id,
        account_type=request.account_type,
        currency=request.currency,
        initial_deposit=Decimal(str(request.initial_deposit))
    )
    
    # Auto-activate for now (in production, would require verification)
    await account.activate()
    
    return {
        'account_id': account_id,
        'client_id': request.client_id,
        'account_type': request.account_type.value,
        'balance': str(account.balance),
        'status': account.status.value,
        'currency': account.currency,
        'interest_rate': str(account.interest_rate)
    }


@router.get('/{account_id}')
async def get_account(account_id: str):
    '''Get account details and balance'''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    return {
        'account_id': account.account_id,
        'client_id': account.client_id,
        'account_type': account.account_type.value if account.account_type else None,
        'balance': str(account.balance),
        'status': account.status.value,
        'currency': account.currency,
        'interest_rate': str(account.interest_rate),
        'transaction_count': len(account.transactions)
    }


@router.post('/{account_id}/deposit')
async def deposit_money(account_id: str, request: TransactionRequest):
    '''
    Deposit money into account
    
    Posts to General Ledger automatically
    '''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    if account.status != 'ACTIVE':
        raise HTTPException(status_code=400, detail=f'Account is {account.status}')
    
    await account.deposit(
        amount=Decimal(str(request.amount)),
        description=request.description,
        reference=request.reference
    )
    
    return {
        'account_id': account_id,
        'transaction_type': 'DEPOSIT',
        'amount': str(request.amount),
        'new_balance': str(account.balance),
        'status': 'COMPLETED'
    }


@router.post('/{account_id}/withdraw')
async def withdraw_money(account_id: str, request: TransactionRequest):
    '''
    Withdraw money from account
    
    Validates sufficient funds
    Posts to General Ledger automatically
    '''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    if account.status != 'ACTIVE':
        raise HTTPException(status_code=400, detail=f'Account is {account.status}')
    
    try:
        await account.withdraw(
            amount=Decimal(str(request.amount)),
            description=request.description,
            reference=request.reference
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        'account_id': account_id,
        'transaction_type': 'WITHDRAWAL',
        'amount': str(request.amount),
        'new_balance': str(account.balance),
        'status': 'COMPLETED'
    }


@router.get('/{account_id}/transactions')
async def get_transactions(account_id: str):
    '''Get account transaction history'''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    return {
        'account_id': account_id,
        'transactions': account.transactions,
        'current_balance': str(account.balance)
    }


@router.get('/{account_id}/statement')
async def get_statement(account_id: str, period: str = 'current_month'):
    '''Generate account statement'''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    total_deposits = sum(
        Decimal(t['amount']) for t in account.transactions 
        if t['transaction_type'] == 'DEPOSIT'
    )
    
    total_withdrawals = sum(
        Decimal(t['amount']) for t in account.transactions 
        if t['transaction_type'] == 'WITHDRAWAL'
    )
    
    return {
        'account_id': account_id,
        'period': period,
        'opening_balance': '0.00',  # Would calculate from period start
        'closing_balance': str(account.balance),
        'total_deposits': str(total_deposits),
        'total_withdrawals': str(total_withdrawals),
        'transaction_count': len(account.transactions),
        'transactions': account.transactions
    }


@router.post('/{account_id}/freeze')
async def freeze_account(account_id: str, reason: str):
    '''Freeze account (fraud/suspicious activity)'''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    await account.freeze(reason)
    
    return {
        'account_id': account_id,
        'status': 'FROZEN',
        'reason': reason
    }


@router.post('/{account_id}/close')
async def close_account(account_id: str, reason: str = 'Customer request'):
    '''Close account'''
    account = AccountAggregate(account_id)
    await account.load_from_events()
    
    if not account.client_id:
        raise HTTPException(status_code=404, detail='Account not found')
    
    try:
        await account.close(reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        'account_id': account_id,
        'status': 'CLOSED',
        'reason': reason
    }
