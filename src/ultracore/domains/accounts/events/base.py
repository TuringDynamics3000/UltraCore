"""Base Event for Accounts Domain - UltraLedger Integration"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

from ultracore.events.base import DomainEvent


class AccountEvent(DomainEvent):
    """
    Base class for all Account domain events.
    
    Integration Points:
    - Kafka: Event streaming and audit trail
    - UltraLedger: Bitemporal ledger entries (double-entry bookkeeping)
    - Data Mesh: Real-time account state products
    - ML: Transaction pattern analysis
    
    Australian Compliance:
    - APRA prudential standards
    - ASIC reporting requirements
    - AUSTRAC (AML/CTF) reporting
    - BSB + Account Number system
    
    Kafka Topic: ultracore.accounts.events
    Partition Key: account_id
    
    UltraLedger Integration:
    Every account event creates corresponding ledger entries:
    - Transaction time: When event occurred
    - Valid time: When it's effective (for backdating, corrections)
    - Immutable audit trail
    - Point-in-time balance queries
    """
    
    aggregate_type: str = "Account"
    domain: str = "accounts"
    
    # Kafka configuration
    kafka_topic: str = "ultracore.accounts.events"
    kafka_partition_key: str = "account_id"
    
    # Common fields
    account_id: str
    customer_id: str
    bsb: Optional[str] = None  # Australian Bank State Branch code
    account_number: Optional[str] = None
    
    # UltraLedger integration
    ledger_entry_id: Optional[str] = None
    transaction_time: datetime = Field(default_factory=datetime.utcnow)
    valid_time: datetime = Field(default_factory=datetime.utcnow)
    
    # Balance tracking (for quick queries)
    balance_before: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None
    available_balance_before: Optional[Decimal] = None
    available_balance_after: Optional[Decimal] = None
    
    # Event metadata
    event_version: str = "1.0.0"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Regulatory flags
    regulatory_event: bool = False
    austrac_reportable: bool = False  # AML/CTF reporting
    large_cash_transaction: bool = False  # >$10,000 AUD
    international_funds_transfer: bool = False
    
    # AI/ML context
    fraud_score: Optional[float] = None
    ml_anomaly_detected: bool = False
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
