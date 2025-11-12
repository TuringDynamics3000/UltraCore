"""
Accounting Kafka Events
Event streaming for all accounting activities
"""

from typing import Dict, Any
from datetime import datetime
from enum import Enum

class AccountingEventType(str, Enum):
    # Journal Entry Events
    JOURNAL_ENTRY_CREATED = "journal_entry_created"
    JOURNAL_ENTRY_POSTED = "journal_entry_posted"
    JOURNAL_ENTRY_REVERSED = "journal_entry_reversed"
    
    # Ledger Events
    LEDGER_UPDATED = "ledger_updated"
    ACCOUNT_BALANCE_CHANGED = "account_balance_changed"
    
    # Statement Events
    TRIAL_BALANCE_GENERATED = "trial_balance_generated"
    BALANCE_SHEET_GENERATED = "balance_sheet_generated"
    INCOME_STATEMENT_GENERATED = "income_statement_generated"
    CASH_FLOW_GENERATED = "cash_flow_generated"
    
    # Reconciliation Events
    RECONCILIATION_STARTED = "reconciliation_started"
    RECONCILIATION_COMPLETED = "reconciliation_completed"
    RECONCILIATION_FAILED = "reconciliation_failed"
    
    # Period Close Events
    PERIOD_CLOSE_STARTED = "period_close_started"
    PERIOD_CLOSE_COMPLETED = "period_close_completed"

class AccountingKafkaProducer:
    """
    Kafka producer for accounting events
    """
    
    def __init__(self):
        from ultracore.streaming.kafka_events import kafka_producer
        self.kafka = kafka_producer
        
        self.topics = {
            "accounting.journal": "Journal entry events",
            "accounting.ledger": "General ledger events",
            "accounting.statements": "Financial statement events",
            "accounting.reconciliation": "Reconciliation events",
            "accounting.period_close": "Period close events"
        }
    
    async def produce_journal_event(
        self,
        event_type: AccountingEventType,
        journal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce journal entry event"""
        
        event = await self.kafka.produce(
            topic="accounting.journal",
            event_type=event_type,
            data=journal_data,
            key=journal_data.get("entry_id")
        )
        
        return event
    
    async def produce_ledger_event(
        self,
        event_type: AccountingEventType,
        ledger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce ledger event"""
        
        event = await self.kafka.produce(
            topic="accounting.ledger",
            event_type=event_type,
            data=ledger_data,
            key=ledger_data.get("account_number")
        )
        
        return event
    
    async def produce_statement_event(
        self,
        event_type: AccountingEventType,
        statement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce statement event"""
        
        event = await self.kafka.produce(
            topic="accounting.statements",
            event_type=event_type,
            data=statement_data,
            key=statement_data.get("statement")
        )
        
        return event
    
    async def produce_reconciliation_event(
        self,
        event_type: AccountingEventType,
        reconciliation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce reconciliation event"""
        
        event = await self.kafka.produce(
            topic="accounting.reconciliation",
            event_type=event_type,
            data=reconciliation_data,
            key=reconciliation_data.get("reconciliation_id")
        )
        
        return event
    
    def subscribe_to_journal(self, callback):
        """Subscribe to journal events"""
        self.kafka.subscribe("accounting.journal", callback)
    
    def subscribe_to_ledger(self, callback):
        """Subscribe to ledger events"""
        self.kafka.subscribe("accounting.ledger", callback)
    
    def subscribe_to_statements(self, callback):
        """Subscribe to statement events"""
        self.kafka.subscribe("accounting.statements", callback)

# Global instance
accounting_kafka = AccountingKafkaProducer()
