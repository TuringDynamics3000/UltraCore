"""BPAY Events"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from .base import PaymentEvent


class BPAYPaymentInitiatedEvent(PaymentEvent):
    """
    BPAY payment initiated.
    
    BPAY: Australian bill payment system
    - Biller Code: Unique identifier for biller (6 digits)
    - Reference Number: Customer reference at biller (up to 20 digits)
    - Processing: 1-3 business days
    - Available: 24/7 payment submission, batch processing
    """
    
    event_type: str = "BPAYPaymentInitiated"
    
    payment_system: str = "BPAY"
    
    # BPAY identifiers
    biller_code: str  # 6 digits
    biller_name: str
    reference_number: str  # Customer ref at biller
    
    # Amount
    amount: Decimal
    currency: str = "AUD"
    
    # Payment date
    payment_date: date  # When biller will receive
    
    # Initiated
    initiated_at: datetime
    initiated_by: str
    
    # Processing
    expected_settlement_date: date  # 1-3 business days


class BPAYPaymentCompletedEvent(PaymentEvent):
    """BPAY payment completed and sent to biller."""
    
    event_type: str = "BPAYPaymentCompleted"
    
    payment_system: str = "BPAY"
    
    # BPAY receipt
    bpay_receipt_number: str
    
    # Biller details
    biller_code: str
    reference_number: str
    
    # Completion
    completed_at: datetime
    settlement_date: date
    
    # Confirmation
    biller_notified: bool = True
