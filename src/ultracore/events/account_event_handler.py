"""
Account Event Handlers

Materialize account and transaction events from Kafka to PostgreSQL
"""

from typing import Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from decimal import Decimal

from ultracore.events.kafka_consumer import EventHandler
from ultracore.database.models.accounts import (
    Account, AccountBalance, Transaction,
    AccountTypeEnum, TransactionTypeEnum
)

logger = logging.getLogger(__name__)


class AccountOpenedHandler(EventHandler):
    """Handle AccountOpened events"""
    
    async def handle_event(
        self,
        event: Dict[str, Any],
        session: AsyncSession
    ) -> bool:
        """Materialize AccountOpened event"""
        
        try:
            data = event['event_data']
            
            # Create account
            account = Account(
                id=uuid.UUID(event['aggregate_id']),
                tenant_id=event['tenant_id'],
                account_id=data['account_id'],
                account_number=data['account_number'],
                customer_id=uuid.UUID(data['customer_id']),
                account_type=AccountTypeEnum[data['account_type']],
                status=data.get('status', 'ACTIVE'),
                currency=data.get('currency', 'AUD'),
                interest_bearing=data.get('interest_bearing', False),
                opened_date=data['opened_date'],
                created_by=event['user_id']
            )
            
            session.add(account)
            
            # Create initial balance
            balance = AccountBalance(
                tenant_id=event['tenant_id'],
                account_id=account.id,
                ledger_balance=Decimal(str(data.get('initial_balance', 0))),
                available_balance=Decimal(str(data.get('initial_balance', 0))),
                pending_credits=Decimal('0'),
                pending_debits=Decimal('0'),
                held_amount=Decimal('0'),
                last_balance_update=data['opened_date'],
                created_by=event['user_id']
            )
            
            session.add(balance)
            
            logger.info(f"✓ Materialized AccountOpened: {data['account_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle AccountOpened: {e}", exc_info=True)
            return False


class TransactionPostedHandler(EventHandler):
    """Handle TransactionPosted events"""
    
    async def handle_event(
        self,
        event: Dict[str, Any],
        session: AsyncSession
    ) -> bool:
        """Materialize transaction and update balance"""
        
        try:
            data = event['event_data']
            
            # Create transaction
            transaction = Transaction(
                tenant_id=event['tenant_id'],
                transaction_id=data['transaction_id'],
                account_id=uuid.UUID(data['account_id']),
                transaction_type=TransactionTypeEnum[data['transaction_type']],
                status=data.get('status', 'POSTED'),
                amount=Decimal(str(data['amount'])),
                currency=data.get('currency', 'AUD'),
                balance_before=Decimal(str(data['balance_before'])),
                balance_after=Decimal(str(data['balance_after'])),
                description=data.get('description'),
                reference=data.get('reference'),
                transaction_date=data['transaction_date'],
                value_date=data['value_date'],
                posted_date=data.get('posted_date'),
                created_by=event['user_id']
            )
            
            session.add(transaction)
            
            # Update account balance
            account_uuid = uuid.UUID(data['account_id'])
            result = await session.execute(
                select(AccountBalance).where(
                    AccountBalance.account_id == account_uuid
                )
            )
            balance = result.scalar_one_or_none()
            
            if balance:
                balance.ledger_balance = Decimal(str(data['balance_after']))
                balance.available_balance = Decimal(str(data['balance_after']))
                balance.last_balance_update = data['transaction_date']
            
            logger.info(f"✓ Materialized TransactionPosted: {data['transaction_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle TransactionPosted: {e}", exc_info=True)
            return False


def get_account_handlers() -> Dict[str, EventHandler]:
    """Get all account event handlers"""
    return {
        'AccountOpened': AccountOpenedHandler(),
        'TransactionPosted': TransactionPostedHandler(),
    }
