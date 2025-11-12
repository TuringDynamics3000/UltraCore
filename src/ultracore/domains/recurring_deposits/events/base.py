"""Base Event for Recurring Deposits Domain"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

from ultracore.events.base import DomainEvent


class RecurringDepositEvent(DomainEvent):
    """
    Base class for all Recurring Deposit domain events.
    
    Kafka Topic: ultracore.recurring_deposits.events
    Partition Key: account_id
    
    All events published to Kafka for:
    - Event sourcing (complete audit trail)
    - Data mesh integration
    - Real-time analytics
    - ML model training
    - Compliance reporting
    - Auto-debit processing
    """
    
    aggregate_type: str = "RecurringDeposit"
    domain: str = "recurring_deposits"
    
    # Kafka configuration
    kafka_topic: str = "ultracore.recurring_deposits.events"
    kafka_partition_key: str = "account_id"
    
    # Common fields
    account_id: str
    customer_id: str
    product_id: str
    currency: str = "AUD"
    
    # Event metadata
    event_version: str = "1.0.0"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # AI/ML context
    ml_prediction_confidence: Optional[float] = None
    anya_context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
