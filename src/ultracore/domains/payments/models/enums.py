"""Payment Enumerations"""
from enum import Enum


class PaymentSystem(str, Enum):
    """Payment systems available in Australia."""
    NPP = "npp"  # New Payments Platform (instant)
    BPAY = "bpay"  # Bill payments
    SWIFT = "swift"  # International
    DIRECT_ENTRY = "direct_entry"  # Legacy batch (being replaced by NPP)


class PayIDType(str, Enum):
    """PayID types for NPP."""
    EMAIL = "email"
    MOBILE = "mobile"
    ABN = "abn"
    ORG_ID = "org_id"


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
