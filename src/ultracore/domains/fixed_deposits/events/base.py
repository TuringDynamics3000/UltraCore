"""Base Event for Fixed Deposits Domain"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

from ultracore.events.base import DomainEvent


class FixedDepositEvent(DomainEvent):
    """
    Base class for all Fixed Deposit domain events.
    
    All events are published to Kafka for:
    - Event sourcing (complete audit trail)
    - Data mesh integration
    - Real-time analytics
    - ML model training
    - Compliance reporting
    """
    
    aggregate_type: str = "FixedDeposit"
    domain: str = "fixed_deposits"
    
    # Kafka configuration
    kafka_topic: str = "ultracore.fixed_deposits.events"
    kafka_partition_key: str = "account_id"  # Partition by account for ordering
    
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
