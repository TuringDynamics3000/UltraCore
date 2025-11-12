"""Payment Models - Event-Sourced"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel

from .enums import PaymentSystem, PaymentStatus, PayIDType


class Payment(BaseModel):
    """Base payment model."""
    
    payment_id: str
    payment_system: PaymentSystem
    
    # From/To
    from_account_id: str
    from_customer_id: str
    
    # Amount
    amount: Decimal
    currency: str = "AUD"
    
    # Description
    description: str
    reference: Optional[str] = None
    
    # Status
    status: PaymentStatus = PaymentStatus.PENDING
    
    # Timing
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Fraud
    fraud_score: Optional[float] = None
    fraud_check_passed: bool = True
    
    # UltraLedger
    ledger_entry_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class NPPPayment(Payment):
    """NPP (New Payments Platform) Payment - Instant."""
    
    payment_system: PaymentSystem = PaymentSystem.NPP
    
    # PayID or BSB+Account
    to_payid: Optional[str] = None
    to_payid_type: Optional[PayIDType] = None
    to_bsb: Optional[str] = None
    to_account_number: Optional[str] = None
    to_account_name: Optional[str] = None
    
    # NPP transaction ID
    npp_transaction_id: Optional[str] = None
    npp_settlement_id: Optional[str] = None
    
    # Processing time (milliseconds)
    processing_time_ms: Optional[int] = None


class BPAYPayment(Payment):
    """BPAY Bill Payment."""
    
    payment_system: PaymentSystem = PaymentSystem.BPAY
    
    # Biller details
    biller_code: str  # 6 digits
    biller_name: str
    reference_number: str  # Customer ref at biller
    
    # Payment date
    payment_date: date
    expected_settlement_date: date
    
    # BPAY receipt
    bpay_receipt_number: Optional[str] = None


class SWIFTPayment(Payment):
    """SWIFT International Payment."""
    
    payment_system: PaymentSystem = PaymentSystem.SWIFT
    
    # Beneficiary
    beneficiary_name: str
    beneficiary_account: str
    beneficiary_bank_name: str
    beneficiary_bank_swift: str  # BIC code
    beneficiary_bank_address: str
    beneficiary_country: str
    beneficiary_iban: Optional[str] = None
    
    # Currency conversion
    original_currency: str = "AUD"
    target_currency: str
    exchange_rate: Optional[Decimal] = None
    
    # Purpose
    purpose_code: str
    payment_purpose: str
    
    # Fees
    fee_option: str = "SHA"  # Shared
    correspondent_fees: Optional[Decimal] = None
    
    # SWIFT reference
    swift_reference: Optional[str] = None  # UETR
    swift_message_type: str = "MT103"
    
    # Expected delivery
    expected_delivery_date: date
