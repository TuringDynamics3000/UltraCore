"""Base Event for Loan Restructuring Domain"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

from ultracore.events.base import DomainEvent


class LoanRestructuringEvent(DomainEvent):
    """
    Base class for all Loan Restructuring domain events.
    
    Australian NCCP Compliance:
    - Hardship provisions (NCCP Section 72)
    - Responsible lending obligations
    - Financial counselling referrals
    - Consumer protections
    - Regulatory reporting (ASIC)
    
    Kafka Topic: ultracore.loan_restructuring.events
    Partition Key: loan_id
    
    All events published to Kafka for:
    - Event sourcing (complete audit trail)
    - Regulatory compliance (ASIC reporting)
    - Data mesh integration
    - ML model training
    - Customer support optimization
    """
    
    aggregate_type: str = "LoanRestructuring"
    domain: str = "loan_restructuring"
    
    # Kafka configuration
    kafka_topic: str = "ultracore.loan_restructuring.events"
    kafka_partition_key: str = "loan_id"
    
    # Common fields
    loan_id: str
    customer_id: str
    restructuring_id: Optional[str] = None
    
    # Australian compliance
    nccp_compliant: bool = True
    hardship_case: bool = False
    
    # Event metadata
    event_version: str = "1.0.0"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Regulatory flags
    regulatory_event: bool = False
    asic_reportable: bool = False
    
    # AI/ML context
    ml_prediction_confidence: Optional[float] = None
    anya_context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
