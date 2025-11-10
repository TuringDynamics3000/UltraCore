"""
BPAY Integration - Australian bill payment system
"""
from typing import Dict, Optional
from decimal import Decimal
from enum import Enum


class BPAYStatus(str, Enum):
    INITIATED = 'INITIATED'
    VALIDATED = 'VALIDATED'
    SUBMITTED = 'SUBMITTED'
    SETTLED = 'SETTLED'


class BillerDirectory:
    """BPAY Biller Directory"""
    
    def __init__(self):
        self.billers = {
            '12345': {
                'biller_code': '12345',
                'biller_name': 'Telstra',
                'crn_min_length': 10,
                'crn_max_length': 10
            }
        }
    
    def lookup_biller(self, biller_code: str) -> Optional[Dict]:
        """Lookup biller by code"""
        return self.billers.get(biller_code)
    
    def validate_crn(self, biller_code: str, crn: str) -> bool:
        """Validate Customer Reference Number"""
        biller = self.lookup_biller(biller_code)
        if not biller:
            return False
        return len(crn) >= biller['crn_min_length'] and len(crn) <= biller['crn_max_length']


class BPAYPayment:
    """BPAY payment processing"""
    
    def __init__(self, payment_id: str):
        self.payment_id = payment_id
        self.status = BPAYStatus.INITIATED
    
    async def initiate(
        self,
        biller_code: str,
        crn: str,
        amount: Decimal,
        from_bsb: str,
        from_account: str
    ):
        """Initiate BPAY payment"""
        biller_directory = BillerDirectory()
        biller = biller_directory.lookup_biller(biller_code)
        
        if not biller:
            raise ValueError(f'Invalid biller code: {biller_code}')
        
        if not biller_directory.validate_crn(biller_code, crn):
            raise ValueError(f'Invalid CRN for biller {biller_code}')
        
        from ultracore.ml_models.scoring_engine import get_scoring_engine, ModelType
        
        scoring_engine = get_scoring_engine()
        fraud_check = await scoring_engine.score(
            model_type=ModelType.FRAUD_DETECTION,
            input_data={'amount': float(amount), 'payment_type': 'BPAY'}
        )
        
        if fraud_check.get('is_fraudulent'):
            raise ValueError('Payment blocked: Fraud detected')
        
        self.biller_code = biller_code
        self.crn = crn
        self.amount = amount
        self.status = BPAYStatus.VALIDATED
