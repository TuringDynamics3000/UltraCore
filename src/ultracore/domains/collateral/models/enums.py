"""Enumerations for Collateral Management - Australian Specific"""
from enum import Enum


class AustralianState(str, Enum):
    """Australian states and territories."""
    NSW = "NSW"  # New South Wales
    VIC = "VIC"  # Victoria
    QLD = "QLD"  # Queensland
    SA = "SA"    # South Australia
    WA = "WA"    # Western Australia
    TAS = "TAS"  # Tasmania
    NT = "NT"    # Northern Territory
    ACT = "ACT"  # Australian Capital Territory


class CollateralType(str, Enum):
    """Types of collateral under Australian law."""
    REAL_PROPERTY_RESIDENTIAL = "real_property_residential"
    REAL_PROPERTY_COMMERCIAL = "real_property_commercial"
    MOTOR_VEHICLE = "motor_vehicle"
    WATERCRAFT = "watercraft"
    AIRCRAFT = "aircraft"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    SHARES = "shares"
    OTHER_PERSONAL_PROPERTY = "other_personal_property"


class CollateralStatus(str, Enum):
    """Collateral lifecycle status."""
    REGISTERED = "registered"
    VALUATION_PENDING = "valuation_pending"
    PERFECTED = "perfected"  # PPSR registered or title secured
    ACTIVE = "active"
    LVR_BREACH = "lvr_breach"
    INSURANCE_LAPSED = "insurance_lapsed"
    UNDER_REVIEW = "under_review"
    RELEASED = "released"
    SEIZED = "seized"
    DISPOSED = "disposed"


class SecurityPosition(str, Enum):
    """Priority position of security interest."""
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    SUBSEQUENT = "subsequent"
    UNSECURED = "unsecured"


class ValuationType(str, Enum):
    """Valuation methods under Australian standards."""
    FULL_INSPECTION = "full_inspection"  # API CPV inspection
    DESKTOP = "desktop"  # Desktop valuation
    KERBSIDE = "kerbside"  # Drive-by valuation
    AVM = "avm"  # Automated Valuation Model
    FORCED_SALE = "forced_sale"  # Mortgagee sale valuation


class PPSRCollateralClass(str, Enum):
    """
    PPSR collateral classes under PPSA.
    
    Reference: Personal Property Securities Regulations 2010
    """
    MOTOR_VEHICLE = "motor_vehicle"
    WATERCRAFT = "watercraft"
    AIRCRAFT = "aircraft"
    AGRICULTURAL = "agricultural"
    ALL_PAP = "all_present_and_after_acquired_property"
    ALL_PRESENT = "all_present_property"
    ACCOUNTS = "accounts"
    CROPS = "crops"
    NEGOTIABLE_INSTRUMENTS = "negotiable_instruments"
    INVENTORY = "inventory"
    OTHER = "other"


class InsuranceType(str, Enum):
    """Insurance types for collateral."""
    COMPREHENSIVE = "comprehensive"
    THIRD_PARTY = "third_party"
    FIRE_AND_THEFT = "fire_and_theft"
    BUILDING = "building"
    CONTENTS = "contents"
    PUBLIC_LIABILITY = "public_liability"
    MARINE = "marine"


class LandTitleSystem(str, Enum):
    """Land title registration systems in Australia."""
    TORRENS = "torrens"  # Most common in Australia
    OLD_SYSTEM = "old_system"  # Rare, mainly NSW
    STRATA = "strata"  # Unit titles
    COMMUNITY = "community"  # Community titles
