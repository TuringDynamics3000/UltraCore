"""NPP (New Payments Platform) Events"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import Field

from .base import PaymentEvent


class NPPPaymentInitiatedEvent(PaymentEvent):
    """
    NPP Payment initiated.
    
    NPP (New Payments Platform):
    - Real-time payments (seconds, not days)
    - 24/7/365 availability
    - PayID addressing (email, mobile, ABN)
    - Rich payment data (up to 280 characters)
    - Instant settlement
    
    Operated by: NPPA (New Payments Platform Australia)
    Clearing: Real-Time Gross Settlement (RTGS)
    """
    
    event_type: str = "NPPPaymentInitiated"
    
    # NPP specific
    payment_system: str = "NPP"
    
    # Destination
    to_payid: Optional[str] = None  # email, mobile, or ABN
    to_payid_type: Optional[Literal["email", "mobile", "abn"]] = None
    to_bsb: Optional[str] = None
    to_account_number: Optional[str] = None
    to_account_name: Optional[str] = None
    
    # Payment details
    amount: Decimal
    currency: str = "AUD"
    description: str
    reference: Optional[str] = None  # Up to 280 chars
    
    # Timing
    initiated_at: datetime
    expected_completion: datetime  # Usually within seconds
    
    # Initiated by
    initiated_by: str
    
    # Fraud checks
    fraud_check_passed: bool = True
    fraud_score: Optional[float] = None


class NPPPaymentCompletedEvent(PaymentEvent):
    """
    NPP Payment completed successfully.
    
    Settlement is instant via RTGS.
    """
    
    event_type: str = "NPPPaymentCompleted"
    
    payment_system: str = "NPP"
    
    # NPP transaction ID
    npp_transaction_id: str
    npp_settlement_id: str
    
    # Timing
    completed_at: datetime
    processing_time_ms: int  # Usually < 5000ms
    
    # Confirmation
    recipient_notified: bool = True


class NPPPaymentFailedEvent(PaymentEvent):
    """NPP Payment failed."""
    
    event_type: str = "NPPPaymentFailed"
    
    payment_system: str = "NPP"
    
    failure_reason: str
    failure_code: str
    
    failed_at: datetime
    
    # Retry
    can_retry: bool = False
    retry_after: Optional[datetime] = None


class PayIDRegisteredEvent(PaymentEvent):
    """
    PayID registered for account.
    
    PayID: Easy-to-remember identifiers for NPP payments
    - Email address
    - Mobile number
    - ABN (Australian Business Number)
    """
    
    event_type: str = "PayIDRegistered"
    
    account_id: str
    customer_id: str
    
    payid: str  # The PayID value
    payid_type: Literal["email", "mobile", "abn"]
    
    # Account linking
    bsb: str
    account_number: str
    account_name: str
    
    # Registration
    registered_at: datetime
    registered_by: str
    
    # Verification
    verification_required: bool = True
    verification_code_sent: bool = True
