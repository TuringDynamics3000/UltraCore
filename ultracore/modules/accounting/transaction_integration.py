"""
Transaction Integration
Automatic journal entries for trades and settlements
"""

from typing import Dict, Any
from datetime import datetime
from ultracore.modules.accounting.journal_entry import (
    journal_entry_service, JournalEntry, JournalEntryLine
)
from ultracore.modules.accounting.general_ledger import general_ledger
from ultracore.modules.accounting.kafka_events import accounting_kafka, AccountingEventType

class TransactionAccountingIntegration:
    """
    Automatically create journal entries for transactions
    Integrates with Transaction Module
    """
    
    def __init__(self):
        # Subscribe to transaction events
        from ultracore.modules.transactions.kafka_events import transaction_kafka
        
        transaction_kafka.subscribe_to_trades(self._handle_trade_event)
        transaction_kafka.subscribe_to_settlement(self._handle_settlement_event)
    
    async def create_trade_journal_entry(
        self,
        trade_data: Dict[str, Any]
    ) -> JournalEntry:
        """
        Create journal entry for trade execution
        
        BUY Trade:
        DR  Investments              (increase asset)
        CR  Settlements Payable       (increase liability)
        
        SELL Trade:
        DR  Settlements Receivable    (increase asset)
        CR  Investments               (decrease asset)
        DR/CR  Realized G/L           (profit/loss)
        """
        
        trade_id = trade_data["trade_id"]
        ticker = trade_data["ticker"]
        side = trade_data["side"]
        quantity = trade_data["quantity"]
        price = trade_data["price"]
        value = trade_data["value"]
        
        entry = journal_entry_service.create_entry(
            description=f"Trade Execution: {side.upper()} {quantity} {ticker} @ ${price}",
            reference=trade_id,
            source_type="trade",
            source_id=trade_id
        )
        
        if side == "buy":
            # Debit: Investments (asset increase)
            entry.add_line(JournalEntryLine(
                account_number="1500",  # Investments - Equity Securities
                debit=value,
                description=f"Purchase {quantity} {ticker}"
            ))
            
            # Credit: Settlements Payable (liability increase)
            entry.add_line(JournalEntryLine(
                account_number="2000",  # Settlements Payable
                credit=value,
                description=f"Settlement due for {ticker} purchase"
            ))
        
        else:  # sell
            # Calculate realized gain/loss
            cost_basis = trade_data.get("cost_basis", value)
            realized_gl = value - cost_basis
            
            # Debit: Settlements Receivable (asset increase)
            entry.add_line(JournalEntryLine(
                account_number="1100",  # Settlements Receivable
                debit=value,
                description=f"Settlement receivable for {ticker} sale"
            ))
            
            # Credit: Investments (asset decrease)
            entry.add_line(JournalEntryLine(
                account_number="1500",  # Investments
                credit=cost_basis,
                description=f"Sale {quantity} {ticker}"
            ))
            
            # Realized Gain/Loss
            if realized_gl > 0:
                # Gain - Credit equity
                entry.add_line(JournalEntryLine(
                    account_number="3210",  # Realized G/L
                    credit=realized_gl,
                    description=f"Realized gain on {ticker}"
                ))
            elif realized_gl < 0:
                # Loss - Debit equity
                entry.add_line(JournalEntryLine(
                    account_number="3210",  # Realized G/L
                    debit=abs(realized_gl),
                    description=f"Realized loss on {ticker}"
                ))
        
        # Validate and post
        validation = entry.validate()
        if validation["valid"]:
            entry.post()
            general_ledger.post_journal_entry(entry)
            
            # Produce Kafka event
            await accounting_kafka.produce_journal_event(
                AccountingEventType.JOURNAL_ENTRY_POSTED,
                entry.to_dict()
            )
            
            print(f"✅ Journal entry posted: {entry.entry_id} for trade {trade_id}")
        else:
            print(f"❌ Invalid journal entry: {validation['error']}")
        
        return entry
    
    async def create_settlement_journal_entry(
        self,
        settlement_data: Dict[str, Any]
    ) -> JournalEntry:
        """
        Create journal entry for settlement (T+2)
        
        BUY Settlement:
        DR  Settlements Payable       (decrease liability)
        CR  Cash                      (decrease asset)
        
        SELL Settlement:
        DR  Cash                      (increase asset)
        CR  Settlements Receivable    (decrease asset)
        """
        
        settlement_id = settlement_data["settlement_id"]
        ticker = settlement_data["ticker"]
        side = settlement_data["side"]
        value = settlement_data["value"]
        
        entry = journal_entry_service.create_entry(
            description=f"Settlement: {side.upper()} {ticker}",
            reference=settlement_id,
            source_type="settlement",
            source_id=settlement_id
        )
        
        if side == "buy":
            # Debit: Settlements Payable (decrease liability)
            entry.add_line(JournalEntryLine(
                account_number="2000",  # Settlements Payable
                debit=value,
                description=f"Settlement of {ticker} purchase"
            ))
            
            # Credit: Cash (decrease asset)
            entry.add_line(JournalEntryLine(
                account_number="1010",  # Client Cash Accounts
                credit=value,
                description=f"Cash payment for {ticker}"
            ))
        
        else:  # sell
            # Debit: Cash (increase asset)
            entry.add_line(JournalEntryLine(
                account_number="1010",  # Client Cash Accounts
                debit=value,
                description=f"Cash received from {ticker} sale"
            ))
            
            # Credit: Settlements Receivable (decrease asset)
            entry.add_line(JournalEntryLine(
                account_number="1100",  # Settlements Receivable
                credit=value,
                description=f"Settlement of {ticker} sale"
            ))
        
        # Validate and post
        validation = entry.validate()
        if validation["valid"]:
            entry.post()
            general_ledger.post_journal_entry(entry)
            
            # Produce Kafka event
            await accounting_kafka.produce_journal_event(
                AccountingEventType.JOURNAL_ENTRY_POSTED,
                entry.to_dict()
            )
            
            print(f"✅ Settlement entry posted: {entry.entry_id} for {settlement_id}")
        else:
            print(f"❌ Invalid settlement entry: {validation['error']}")
        
        return entry
    
    async def create_fee_journal_entry(
        self,
        fee_data: Dict[str, Any]
    ) -> JournalEntry:
        """
        Create journal entry for fee revenue
        
        DR  Fees Receivable
        CR  Management Fees (revenue)
        """
        
        fee_amount = fee_data["amount"]
        client_id = fee_data["client_id"]
        
        entry = journal_entry_service.create_entry(
            description=f"Management fee for {client_id}",
            reference=fee_data.get("fee_id", ""),
            source_type="fee",
            source_id=fee_data.get("fee_id", "")
        )
        
        # Debit: Fees Receivable
        entry.add_line(JournalEntryLine(
            account_number="1110",  # Fees Receivable
            debit=fee_amount,
            description=f"Fee receivable from {client_id}"
        ))
        
        # Credit: Management Fees
        entry.add_line(JournalEntryLine(
            account_number="4000",  # Management Fees
            credit=fee_amount,
            description=f"Management fee revenue"
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
        
        return entry
    
    async def _handle_trade_event(self, event: Dict[str, Any]):
        """Handle trade execution events"""
        
        from ultracore.modules.transactions.kafka_events import TransactionEventType
        
        if event["event_type"] == TransactionEventType.TRADE_EXECUTED:
            await self.create_trade_journal_entry(event["data"])
    
    async def _handle_settlement_event(self, event: Dict[str, Any]):
        """Handle settlement events"""
        
        from ultracore.modules.transactions.kafka_events import TransactionEventType
        
        if event["event_type"] == TransactionEventType.SETTLEMENT_COMPLETED:
            await self.create_settlement_journal_entry(event["data"])

# Global instance
transaction_accounting = TransactionAccountingIntegration()
