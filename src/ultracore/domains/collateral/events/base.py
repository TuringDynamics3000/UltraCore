"""Base Event for Collateral Management Domain"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

from ultracore.events.base import DomainEvent


class CollateralEvent(DomainEvent):
    """
    Base class for all Collateral Management domain events.
    
    Australian Compliance:
    - PPSA (Personal Property Securities Act 2009)
    - PPSR (Personal Property Securities Register) integration
    - State-based land title systems (Torrens)
    - National Consumer Credit Protection Act
    - Australian Valuation Standards
    
    Kafka Topic: ultracore.collateral.events
    Partition Key: collateral_id
    
    All events published to Kafka for:
    - Event sourcing (complete audit trail)
    - Regulatory compliance (ASIC reporting)
    - Data mesh integration
    - ML model training
    - Risk monitoring
    - PPSR integration
    """
    
    aggregate_type: str = "Collateral"
    domain: str = "collateral"
    
    # Kafka configuration
    kafka_topic: str = "ultracore.collateral.events"
    kafka_partition_key: str = "collateral_id"
    
    # Common fields
    collateral_id: str
    loan_id: str
    customer_id: str
    
    # Australian compliance
    jurisdiction: str = "AU"  # State: NSW, VIC, QLD, SA, WA, TAS, NT, ACT
    
    # Event metadata
    event_version: str = "1.0.0"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Compliance tracking
    regulatory_event: bool = False  # Requires ASIC reporting
    ppsr_relevant: bool = False  # Affects PPSR registration
    
    # AI/ML context
    ml_prediction_confidence: Optional[float] = None
    anya_context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
