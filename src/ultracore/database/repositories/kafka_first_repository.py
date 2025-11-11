"""
UltraCore Base Repository - Kafka-First Edition

KAFKA-FIRST ARCHITECTURE:
1. Write event to Kafka (source of truth)
2. Kafka consumers materialize to PostgreSQL (read model)
3. Repository reads from PostgreSQL (optimized for queries)

This ensures:
- Kafka = immutable event log
- PostgreSQL = materialized view
- Event replay capability
- True CQRS
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime
import json

from ultracore.database.models.base import BaseModel
from ultracore.database.config import get_cache_manager
from ultracore.events.kafka_producer import get_kafka_producer, EventTopic
import uuid

T = TypeVar('T', bound=BaseModel)


class KafkaFirstRepository(Generic[T]):
    """
    Kafka-first repository pattern
    
    WRITE PATH:
    1. Validate business rules
    2. Write event to Kafka (source of truth)
    3. Return immediately (async materialization)
    
    READ PATH:
    1. Read from PostgreSQL (materialized view)
    2. Use caching for performance
    """
    
    def __init__(
        self,
        model: Type[T],
        session: AsyncSession,
        tenant_id: str,
        event_topic: EventTopic
    ):
        self.model = model
        self.session = session
        self.tenant_id = tenant_id
        self.event_topic = event_topic
        self.cache = get_cache_manager()
        self.kafka_producer = get_kafka_producer()
    
    # ========================================================================
    # WRITE OPERATIONS (Kafka-first)
    # ========================================================================
    
    async def create_event(
        self,
        event_type: str,
        aggregate_id: str,
        event_data: Dict[str, Any],
        created_by: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Create event (WRITE to Kafka first)
        
        This is the PRIMARY write operation.
        Materialization happens asynchronously via consumers.
        
        Returns:
            Event ID
        """
        # Publish to Kafka (source of truth)
        event_id = await self.kafka_producer.publish_event(
            topic=self.event_topic,
            event_type=event_type,
            aggregate_type=self.model.__name__,
            aggregate_id=aggregate_id,
            event_data=event_data,
            tenant_id=self.tenant_id,
            user_id=created_by,
            correlation_id=correlation_id
        )
        
        # Invalidate cache
        cache_key = f"{self.model.__name__}:{self.tenant_id}:{aggregate_id}"
        await self.cache.delete(cache_key)
        
        return event_id
    
    # ========================================================================
    # READ OPERATIONS (PostgreSQL - materialized view)
    # ========================================================================
    
    async def get_by_id(
        self,
        entity_id: uuid.UUID,
        include_deleted: bool = False
    ) -> Optional[T]:
        """
        Get entity by ID (from materialized view)
        
        Reads from PostgreSQL (optimized for queries)
        """
        # Try cache first
        cache_key = f"{self.model.__name__}:{self.tenant_id}:{entity_id}"
        cached = await self.cache.get(cache_key)
        
        if cached:
            return self._dict_to_entity(json.loads(cached))
        
        # Query database
        query = select(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.tenant_id == self.tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()
        
        # Cache result
        if entity:
            await self.cache.set(
                cache_key,
                json.dumps(self._entity_to_dict(entity)),
                expiry=3600
            )
        
        return entity
    
    async def get_by_business_id(
        self,
        business_id: str,
        business_id_field: str = 'customer_id'
    ) -> Optional[T]:
        """Get entity by business ID"""
        query = select(self.model).where(
            and_(
                getattr(self.model, business_id_field) == business_id,
                self.model.tenant_id == self.tenant_id,
                self.model.deleted_at.is_(None)
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[T]:
        """List entities (from materialized view)"""
        query = select(self.model).where(
            self.model.tenant_id == self.tenant_id
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        else:
            query = query.order_by(self.model.created_at.desc())
        
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """Count entities"""
        query = select(func.count(self.model.id)).where(
            self.model.tenant_id == self.tenant_id
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        result = {}
        for column in entity.__table__.columns:
            value = getattr(entity, column.name)
            
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        
        return result
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to entity"""
        entity = self.model()
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        return entity
