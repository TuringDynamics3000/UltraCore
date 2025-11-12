"""Base Payment Event"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

from ultracore.events.base import DomainEvent


class PaymentEvent(DomainEvent):
    """
    Base class for payment events.
    
    Australian Payment Systems:
    - NPP (New Payments Platform): Instant 24/7 payments with PayID
    - BPAY: Bill payments (unique biller codes)
    - SWIFT: International payments (SWIFT network)
    - Direct Entry: Batch payments (legacy, being replaced by NPP)
    
    Kafka Topic: ultracore.payments.events
    """
    
    aggregate_type: str = "Payment"
    domain: str = "payments"
    
    kafka_topic: str = "ultracore.payments.events"
    kafka_partition_key: str = "payment_id"
    
    payment_id: str
    from_account_id: str
    amount: Decimal
    currency: str = "AUD"
    
    # UltraLedger
    ledger_entry_id: Optional[str] = None
    
    # Fraud detection
    fraud_score: Optional[float] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
