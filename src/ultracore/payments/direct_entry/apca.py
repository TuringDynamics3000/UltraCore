"""
Direct Entry (DE) System - APCA-compliant bulk payment processing
"""
from typing import Dict, List
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum


class DETransactionCode(str, Enum):
    DEBIT_13 = '13'
    DEBIT_50 = '50'
    CREDIT_53 = '53'
    CREDIT_54 = '54'


class DirectEntryFile:
    """Generate APCA Direct Entry files"""
    
    def __init__(self, user_id: str, user_name: str, apca_id: str):
        self.user_id = user_id
        self.user_name = user_name
        self.apca_id = apca_id
        self.transactions: List[Dict] = []
    
    def add_transaction(
        self,
        transaction_code: DETransactionCode,
        bsb: str,
        account_number: str,
        amount: Decimal,
        account_name: str,
        reference: str,
        remitter_name: str
    ):
        """Add transaction to DE batch"""
        self.transactions.append({
            'transaction_code': transaction_code.value,
            'bsb': bsb.replace('-', ''),
            'account_number': account_number.ljust(9),
            'amount': amount,
            'account_name': account_name[:32].ljust(32),
            'reference': reference[:18].ljust(18),
            'remitter_name': remitter_name[:16].ljust(16)
        })
    
    def generate_file(self) -> str:
        """Generate APCA DE file (120 chars per line)"""
        lines = []
        
        # Descriptive record
        record = '0' + ' ' * 17 + '01'
        record += self.user_name[:26].ljust(26)
        record += self.apca_id.rjust(6, '0')
        lines.append(record.ljust(120))
        
        # Detail records
        for txn in self.transactions:
            record = '1' + txn['bsb'] + txn['account_number']
            record += ' ' + txn['transaction_code']
            record += str(int(txn['amount'] * 100)).rjust(10, '0')
            record += txn['account_name']
            lines.append(record.ljust(120))
        
        # File total
        total = sum(t['amount'] for t in self.transactions)
        record = '7999-999' + ' ' * 12
        record += str(int(total * 100)).rjust(10, '0')
        lines.append(record.ljust(120))
        
        return '\n'.join(lines)


class DirectEntryBatch:
    """Direct Entry batch processing"""
    
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.status = 'CREATED'
    
    async def create_batch(
        self,
        user_id: str,
        user_name: str,
        apca_id: str,
        transactions: List[Dict]
    ):
        """Create DE batch"""
        from ultracore.ml_models.scoring_engine import get_scoring_engine, ModelType
        
        scoring_engine = get_scoring_engine()
        fraud_check = await scoring_engine.score(
            model_type=ModelType.AML_MONITORING,
            input_data={'transactions': transactions}
        )
        
        if fraud_check.get('is_suspicious'):
            raise ValueError('Batch flagged for AML review')
        
        de_file = DirectEntryFile(user_id, user_name, apca_id)
        for txn in transactions:
            de_file.add_transaction(
                DETransactionCode(txn['transaction_code']),
                txn['bsb'],
                txn['account_number'],
                Decimal(str(txn['amount'])),
                txn['account_name'],
                txn['reference'],
                txn['remitter_name']
            )
        
        self.de_file = de_file.generate_file()
        self.status = 'VALIDATED'
