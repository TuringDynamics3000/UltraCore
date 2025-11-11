"""
Customer Event Handlers

Materialize customer events from Kafka to PostgreSQL
"""

from typing import Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ultracore.events.kafka_consumer import EventHandler
from ultracore.database.models.customers import Customer, CustomerTypeEnum

logger = logging.getLogger(__name__)


class CustomerCreatedHandler(EventHandler):
    """Handle CustomerCreated events"""
    
    async def handle_event(
        self,
        event: Dict[str, Any],
        session: AsyncSession
    ) -> bool:
        """Materialize CustomerCreated event to database"""
        
        try:
            data = event['event_data']
            
            # Create customer in read model
            customer = Customer(
                id=uuid.UUID(event['aggregate_id']),
                tenant_id=event['tenant_id'],
                customer_id=data['customer_id'],
                customer_type=CustomerTypeEnum[data['customer_type']],
                status=data.get('status', 'ACTIVE'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data['email'],
                mobile=data['mobile'],
                date_of_birth=data.get('date_of_birth'),
                created_by=event['user_id']
            )
            
            session.add(customer)
            
            logger.info(f"✓ Materialized CustomerCreated: {data['customer_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle CustomerCreated: {e}", exc_info=True)
            return False


class CustomerUpdatedHandler(EventHandler):
    """Handle CustomerUpdated events"""
    
    async def handle_event(
        self,
        event: Dict[str, Any],
        session: AsyncSession
    ) -> bool:
        """Update customer in read model"""
        
        try:
            data = event['event_data']
            customer_id = uuid.UUID(event['aggregate_id'])
            
            # Get customer
            result = await session.execute(
                select(Customer).where(Customer.id == customer_id)
            )
            customer = result.scalar_one_or_none()
            
            if not customer:
                logger.warning(f"Customer not found: {customer_id}")
                return False
            
            # Update fields
            for field, value in data.items():
                if hasattr(customer, field):
                    setattr(customer, field, value)
            
            customer.updated_by = event['user_id']
            
            logger.info(f"✓ Materialized CustomerUpdated: {customer.customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle CustomerUpdated: {e}", exc_info=True)
            return False


# Factory to get all customer handlers
def get_customer_handlers() -> Dict[str, EventHandler]:
    """Get all customer event handlers"""
    return {
        'CustomerCreated': CustomerCreatedHandler(),
        'CustomerUpdated': CustomerUpdatedHandler(),
    }
