"""
ETF Aggregate - Domain model for Exchange Traded Funds
Implements Event Sourcing pattern for complete audit trail
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from ultracore.event_sourcing.base import AggregateRoot
from ultracore.market_data.etf.events import (
    ETFCreatedEvent,
    ETFDataUpdatedEvent,
    ETFPriceUpdatedEvent,
    ETFMetadataUpdatedEvent,
    ETFDelistedEvent
)


@dataclass
class ETFPriceData:
    """Price data for a specific date"""
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adj_close: Decimal
    volume: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "adj_close": float(self.adj_close),
            "volume": self.volume
        }


@dataclass
class ETFMetadata:
    """ETF metadata and characteristics"""
    name: str
    issuer: str
    category: str
    benchmark: Optional[str] = None
    management_fee: Optional[Decimal] = None
    inception_date: Optional[date] = None
    description: Optional[str] = None
    website: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "issuer": self.issuer,
            "category": self.category,
            "benchmark": self.benchmark,
            "management_fee": float(self.management_fee) if self.management_fee else None,
            "inception_date": self.inception_date.isoformat() if self.inception_date else None,
            "description": self.description,
            "website": self.website
        }


class ETFAggregate(AggregateRoot):
    """
    ETF Aggregate Root - manages ETF lifecycle and historical data
    Uses Event Sourcing to maintain complete history of all changes
    """
    
    def __init__(self, etf_id: UUID, ticker: str):
        super().__init__(etf_id)
        self.ticker = ticker
        self.metadata: Optional[ETFMetadata] = None
        self.price_history: List[ETFPriceData] = []
        self.is_active: bool = True
        self.last_updated: Optional[datetime] = None
        self.data_source: str = "yahoo_finance"
        self.created_at: Optional[datetime] = None
        
    @classmethod
    def create(cls, ticker: str, metadata: ETFMetadata) -> "ETFAggregate":
        """Create a new ETF aggregate"""
        etf_id = uuid4()
        etf = cls(etf_id, ticker)
        
        event = ETFCreatedEvent(
            aggregate_id=etf_id,
            ticker=ticker,
            metadata=metadata.to_dict(),
            timestamp=datetime.utcnow()
        )
        
        etf.apply_event(event)
        return etf
    
    def update_metadata(self, metadata: ETFMetadata) -> None:
        """Update ETF metadata"""
        event = ETFMetadataUpdatedEvent(
            aggregate_id=self.id,
            ticker=self.ticker,
            metadata=metadata.to_dict(),
            timestamp=datetime.utcnow()
        )
        
        self.apply_event(event)
    
    def add_price_data(self, price_data: List[ETFPriceData]) -> None:
        """Add historical price data"""
        event = ETFDataUpdatedEvent(
            aggregate_id=self.id,
            ticker=self.ticker,
            price_data=[p.to_dict() for p in price_data],
            data_points=len(price_data),
            timestamp=datetime.utcnow()
        )
        
        self.apply_event(event)
    
    def update_latest_price(self, price_data: ETFPriceData) -> None:
        """Update with latest daily price"""
        event = ETFPriceUpdatedEvent(
            aggregate_id=self.id,
            ticker=self.ticker,
            price_data=price_data.to_dict(),
            timestamp=datetime.utcnow()
        )
        
        self.apply_event(event)
    
    def delist(self, reason: str) -> None:
        """Mark ETF as delisted"""
        event = ETFDelistedEvent(
            aggregate_id=self.id,
            ticker=self.ticker,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        
        self.apply_event(event)
    
    # Event handlers
    def _apply_etf_created(self, event: ETFCreatedEvent) -> None:
        """Apply ETF created event"""
        self.metadata = ETFMetadata(**event.metadata)
        self.created_at = event.timestamp
        self.last_updated = event.timestamp
    
    def _apply_etf_metadata_updated(self, event: ETFMetadataUpdatedEvent) -> None:
        """Apply metadata updated event"""
        self.metadata = ETFMetadata(**event.metadata)
        self.last_updated = event.timestamp
    
    def _apply_etf_data_updated(self, event: ETFDataUpdatedEvent) -> None:
        """Apply data updated event"""
        new_prices = [
            ETFPriceData(
                date=datetime.fromisoformat(p["date"]).date(),
                open=Decimal(str(p["open"])),
                high=Decimal(str(p["high"])),
                low=Decimal(str(p["low"])),
                close=Decimal(str(p["close"])),
                adj_close=Decimal(str(p["adj_close"])),
                volume=p["volume"]
            )
            for p in event.price_data
        ]
        
        # Merge with existing data, avoiding duplicates
        existing_dates = {p.date for p in self.price_history}
        for price in new_prices:
            if price.date not in existing_dates:
                self.price_history.append(price)
        
        # Sort by date
        self.price_history.sort(key=lambda x: x.date)
        self.last_updated = event.timestamp
    
    def _apply_etf_price_updated(self, event: ETFPriceUpdatedEvent) -> None:
        """Apply price updated event"""
        price_data = ETFPriceData(
            date=datetime.fromisoformat(event.price_data["date"]).date(),
            open=Decimal(str(event.price_data["open"])),
            high=Decimal(str(event.price_data["high"])),
            low=Decimal(str(event.price_data["low"])),
            close=Decimal(str(event.price_data["close"])),
            adj_close=Decimal(str(event.price_data["adj_close"])),
            volume=event.price_data["volume"]
        )
        
        # Update or append
        existing_dates = {p.date for p in self.price_history}
        if price_data.date in existing_dates:
            # Replace existing
            self.price_history = [p for p in self.price_history if p.date != price_data.date]
        
        self.price_history.append(price_data)
        self.price_history.sort(key=lambda x: x.date)
        self.last_updated = event.timestamp
    
    def _apply_etf_delisted(self, event: ETFDelistedEvent) -> None:
        """Apply delisted event"""
        self.is_active = False
        self.last_updated = event.timestamp
    
    def get_price_range(self, start_date: date, end_date: date) -> List[ETFPriceData]:
        """Get price data for a specific date range"""
        return [
            p for p in self.price_history
            if start_date <= p.date <= end_date
        ]
    
    def get_latest_price(self) -> Optional[ETFPriceData]:
        """Get the most recent price data"""
        return self.price_history[-1] if self.price_history else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "ticker": self.ticker,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "is_active": self.is_active,
            "data_points": len(self.price_history),
            "earliest_date": self.price_history[0].date.isoformat() if self.price_history else None,
            "latest_date": self.price_history[-1].date.isoformat() if self.price_history else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
