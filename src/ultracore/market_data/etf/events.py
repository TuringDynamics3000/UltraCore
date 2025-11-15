"""
ETF Domain Events - Event Sourcing
All changes to ETF data are captured as immutable events
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID

from ultracore.event_sourcing.domain_event import DomainEvent


@dataclass
class ETFCreatedEvent(DomainEvent):
    """Event fired when a new ETF is added to the system"""
    ticker: str
    metadata: Dict[str, Any]
    
    @property
    def event_type(self) -> str:
        return "etf.created"


@dataclass
class ETFMetadataUpdatedEvent(DomainEvent):
    """Event fired when ETF metadata is updated"""
    ticker: str
    metadata: Dict[str, Any]
    
    @property
    def event_type(self) -> str:
        return "etf.metadata.updated"


@dataclass
class ETFDataUpdatedEvent(DomainEvent):
    """Event fired when historical price data is added/updated"""
    ticker: str
    price_data: List[Dict[str, Any]]
    data_points: int
    
    @property
    def event_type(self) -> str:
        return "etf.data.updated"


@dataclass
class ETFPriceUpdatedEvent(DomainEvent):
    """Event fired when latest daily price is updated"""
    ticker: str
    price_data: Dict[str, Any]
    
    @property
    def event_type(self) -> str:
        return "etf.price.updated"


@dataclass
class ETFDelistedEvent(DomainEvent):
    """Event fired when an ETF is delisted"""
    ticker: str
    reason: str
    
    @property
    def event_type(self) -> str:
        return "etf.delisted"


@dataclass
class ETFDataCollectionStartedEvent(DomainEvent):
    """Event fired when data collection job starts"""
    job_id: UUID
    etf_count: int
    collection_type: str  # "initial" or "update"
    
    @property
    def event_type(self) -> str:
        return "etf.collection.started"


@dataclass
class ETFDataCollectionCompletedEvent(DomainEvent):
    """Event fired when data collection job completes"""
    job_id: UUID
    successful: int
    failed: int
    duration_seconds: float
    
    @property
    def event_type(self) -> str:
        return "etf.collection.completed"


@dataclass
class ETFDataCollectionFailedEvent(DomainEvent):
    """Event fired when data collection fails for an ETF"""
    ticker: str
    error: str
    retry_count: int
    
    @property
    def event_type(self) -> str:
        return "etf.collection.failed"
