"""
Holdings Integration
Automatic journal entries for position revaluation
"""

from typing import Dict, Any
from datetime import datetime
from ultracore.modules.accounting.journal_entry import (
    journal_entry_service, JournalEntry, JournalEntryLine
)
from ultracore.modules.accounting.general_ledger import general_ledger
from ultracore.modules.accounting.kafka_events import accounting_kafka, AccountingEventType

class HoldingsAccountingIntegration:
    """
    Automatically create journal entries for position valuations
    Integrates with Holdings Module
    """
    
    def __init__(self):
        # Subscribe to holdings events
        from ultracore.streaming.kafka_events import kafka_producer
        kafka_producer.subscribe("holdings.valuations", self._handle_valuation_event)
    
    async def create_valuation_journal_entry(
        self,
        position_data: Dict[str, Any],
        previous_value: float,
        new_value: float
    ) -> JournalEntry:
        """
        Create journal entry for position revaluation
        Records unrealized gains/losses
        
        Gain (increase in value):
        DR  Investments
        CR  Unrealized G/L
        
        Loss (decrease in value):
        DR  Unrealized G/L
        CR  Investments
        """
        
        position_id = position_data["position_id"]
        ticker = position_data["ticker"]
        value_change = new_value - previous_value
        
        if abs(value_change) < 0.01:
            # No significant change
            return None
        
        entry = journal_entry_service.create_entry(
            description=f"Revaluation: {ticker}",
            reference=position_id,
            source_type="valuation",
            source_id=position_id
        )
        
        if value_change > 0:
            # Unrealized Gain
            # Debit: Investments (increase asset)
            entry.add_line(JournalEntryLine(
                account_number="1500",  # Investments
                debit=value_change,
                description=f"Mark-to-market gain on {ticker}"
            ))
            
            # Credit: Unrealized G/L (increase equity)
            entry.add_line(JournalEntryLine(
                account_number="3200",  # Unrealized G/L
                credit=value_change,
                description=f"Unrealized gain on {ticker}"
            ))
        else:
            # Unrealized Loss
            # Debit: Unrealized G/L (decrease equity)
            entry.add_line(JournalEntryLine(
                account_number="3200",  # Unrealized G/L
                debit=abs(value_change),
                description=f"Unrealized loss on {ticker}"
            ))
            
            # Credit: Investments (decrease asset)
            entry.add_line(JournalEntryLine(
                account_number="1500",  # Investments
                credit=abs(value_change),
                description=f"Mark-to-market loss on {ticker}"
            ))
        
        # Post
        validation = entry.validate()
        if validation["valid"]:
            entry.post()
            general_ledger.post_journal_entry(entry)
            
            await accounting_kafka.produce_journal_event(
                AccountingEventType.JOURNAL_ENTRY_POSTED,
                entry.to_dict()
            )
            
            print(f"✅ Valuation entry posted: {entry.entry_id} for {ticker} (${value_change:+,.2f})")
        
        return entry
    
    async def revalue_all_positions(
        self,
        client_id: str
    ) -> Dict[str, Any]:
        """
        Revalue all positions for client
        Creates journal entries for all value changes
        """
        
        from ultracore.modules.holdings.holdings_service import holdings_service
        
        # Get current portfolio
        portfolio = await holdings_service.get_portfolio_value(client_id, real_time=True)
        
        positions = portfolio.get("positions", [])
        
        entries_created = []
        total_unrealized_change = 0.0
        
        for position in positions:
            cost_basis = position.get("cost_basis", 0)
            market_value = position.get("market_value", 0)
            
            # Get previous recorded value (simplified - would need to track this)
            previous_value = cost_basis  # Assuming first valuation
            
            if market_value != previous_value:
                entry = await self.create_valuation_journal_entry(
                    position,
                    previous_value,
                    market_value
                )
                
                if entry:
                    entries_created.append(entry.entry_id)
                    total_unrealized_change += (market_value - previous_value)
        
        return {
            "client_id": client_id,
            "positions_revalued": len(positions),
            "journal_entries_created": len(entries_created),
            "total_unrealized_change": total_unrealized_change,
            "entries": entries_created
        }
    
    async def _handle_valuation_event(self, event: Dict[str, Any]):
        """Handle position valuation events"""
        
        from ultracore.streaming.kafka_events import EventType
        
        if event["event_type"] == EventType.POSITION_VALUED:
            data = event["data"]
            
            # Create valuation entry if needed
            if "previous_value" in data and "market_value" in data:
                await self.create_valuation_journal_entry(
                    data,
                    data["previous_value"],
                    data["market_value"]
                )

# Global instance
holdings_accounting = HoldingsAccountingIntegration()
