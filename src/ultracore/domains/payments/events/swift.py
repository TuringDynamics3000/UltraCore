"""SWIFT Events"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from .base import PaymentEvent


class SWIFTPaymentInitiatedEvent(PaymentEvent):
    """
    SWIFT payment initiated (international).
    
    SWIFT: Society for Worldwide Interbank Financial Telecommunication
    - BIC/SWIFT codes: 8 or 11 characters (bank identifier)
    - IBAN: International Bank Account Number (where applicable)
    - Processing: 1-5 business days
    - Fees: Correspondent bank fees may apply
    """
    
    event_type: str = "SWIFTPaymentInitiated"
    
    payment_system: str = "SWIFT"
    
    # Beneficiary
    beneficiary_name: str
    beneficiary_account: str
    beneficiary_bank_name: str
    beneficiary_bank_swift: str  # BIC/SWIFT code
    beneficiary_bank_address: str
    beneficiary_country: str
    
    # IBAN (if applicable)
    beneficiary_iban: Optional[str] = None
    
    # Amount
    amount: Decimal
    currency: str  # USD, EUR, GBP, etc.
    
    # Exchange rate (if currency conversion)
    exchange_rate: Optional[Decimal] = None
    aud_equivalent: Optional[Decimal] = None
    
    # Purpose
    purpose_code: str
    payment_purpose: str  # Remittance information
    
    # Fees
    fee_option: str = "SHA"  # SHA (shared), OUR (sender pays all), BEN (beneficiary pays)
    estimated_correspondent_fees: Optional[Decimal] = None
    
    # Initiated
    initiated_at: datetime
    initiated_by: str
    
    # Processing
    expected_delivery_date: date


class SWIFTPaymentCompletedEvent(PaymentEvent):
    """SWIFT payment sent successfully."""
    
    event_type: str = "SWIFTPaymentCompleted"
    
    payment_system: str = "SWIFT"
    
    # SWIFT details
    swift_message_type: str = "MT103"  # Customer transfer
    swift_reference: str  # UETR (Unique End-to-End Transaction Reference)
    
    # Completion
    completed_at: datetime
    
    # Tracking
    correspondent_banks: list = []
    current_status: str = "in_transit"
