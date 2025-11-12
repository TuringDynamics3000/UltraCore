"""Collateral Domain Models - Australian Compliant"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from .enums import (
    CollateralType,
    CollateralStatus,
    SecurityPosition,
    ValuationType,
    PPSRCollateralClass,
    AustralianState,
    InsuranceType,
    LandTitleSystem
)


class PPSRRegistration(BaseModel):
    """
    PPSR Registration details.
    
    Australian PPSA compliance for personal property security.
    """
    
    ppsr_registration_number: str = Field(..., description="16-digit registration number")
    registration_time: datetime = Field(..., description="Priority timestamp")
    registration_end_date: Optional[date] = None
    
    # Secured party
    secured_party_name: str
    secured_party_abn: Optional[str] = None
    secured_party_acn: Optional[str] = None
    
    # Grantor
    grantor_name: str
    grantor_abn: Optional[str] = None
    grantor_acn: Optional[str] = None
    
    # Collateral
    collateral_class: PPSRCollateralClass
    collateral_description: str
    serial_numbered: bool = False
    serial_number: Optional[str] = None
    
    # Security agreement
    security_agreement_date: date
    secured_amount: Optional[Decimal] = None
    
    # Status
    is_active: bool = True
    discharged_date: Optional[datetime] = None
    
    # Priority
    security_position: SecurityPosition
    subordinated_to: Optional[str] = None


class CollateralValuation(BaseModel):
    """
    Collateral valuation record.
    
    Australian compliance:
    - Must use certified valuer for > residential
    - Must comply with Australian Valuation Standards
    - LMI requires approved panel valuers
    """
    
    valuation_id: str
    valuation_date: date
    valuation_effective_date: date
    valuation_expiry_date: date
    
    # Values
    market_value: Decimal
    forced_sale_value: Optional[Decimal] = Field(
        None,
        description="Typically 70-80% of market value"
    )
    
    # Valuer
    valuer_name: str
    valuer_registration: str = Field(..., description="API registration number")
    valuation_firm: str
    valuation_type: ValuationType
    
    # Report
    valuation_report_reference: str
    confidence_level: str = "high"
    
    # Compliance
    australian_standards_compliant: bool = True
    lmi_approved_valuer: bool = False


class CollateralInsurance(BaseModel):
    """
    Insurance coverage for collateral.
    
    Protects lender's security interest.
    """
    
    policy_number: str
    insurer_name: str
    insurance_type: InsuranceType
    
    # Coverage
    sum_insured: Decimal
    premium_amount: Decimal
    
    # Dates
    policy_start_date: date
    policy_end_date: date
    renewal_date: date
    
    # Interest noting
    bank_noted_as_interested_party: bool = True
    
    # Status
    is_active: bool = True
    premium_paid_to_date: bool = True
    lapsed_date: Optional[date] = None


class RealPropertyCollateral(BaseModel):
    """
    Real property (land and buildings) collateral.
    
    Australian land title system (predominantly Torrens).
    """
    
    # Property identification
    property_address: str
    title_reference: str = Field(..., description="e.g., Lot 10 DP 12345")
    certificate_of_title: Optional[str] = None
    
    # State land registry
    state: AustralianState
    land_registry_office: str = Field(
        ...,
        description="NSW LRS, Land Use Victoria, Qld Land Titles, etc."
    )
    title_system: LandTitleSystem = LandTitleSystem.TORRENS
    
    # Property details
    property_type: str = Field(..., description="House, Unit, Townhouse, Land, etc.")
    land_area_sqm: Optional[Decimal] = None
    building_area_sqm: Optional[Decimal] = None
    zoning: Optional[str] = None
    
    # Bedrooms/bathrooms (if residential)
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    car_spaces: Optional[int] = None
    
    # Title details
    owners: List[str] = Field(default_factory=list)
    encumbrances: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Existing mortgages, easements, covenants"
    )
    
    # Strata (if applicable)
    is_strata: bool = False
    strata_plan_number: Optional[str] = None
    lot_number: Optional[str] = None
    body_corporate_fees_annual: Optional[Decimal] = None
    
    # Council
    council: str
    council_rates_annual: Decimal
    
    # Water
    water_rates_annual: Optional[Decimal] = None
    
    # Security
    caveat_lodged: bool = False
    caveat_number: Optional[str] = None
    caveat_date: Optional[date] = None
    mortgage_registered: bool = False
    mortgage_number: Optional[str] = None


class MotorVehicleCollateral(BaseModel):
    """
    Motor vehicle collateral.
    
    Must register on PPSR for perfection.
    """
    
    # Vehicle identification
    vin: str = Field(..., description="Vehicle Identification Number (VIN)")
    registration_number: str
    registration_state: AustralianState
    
    # Vehicle details
    make: str
    model: str
    year: int
    body_type: str
    colour: str
    
    # Engine
    engine_number: Optional[str] = None
    engine_capacity_cc: Optional[int] = None
    fuel_type: str
    transmission: str
    
    # Odometer
    odometer_reading_km: int
    odometer_reading_date: date
    
    # Registration
    registration_expiry: date
    registration_status: str = "current"
    
    # Finance
    ppsr_registration: Optional[PPSRRegistration] = None
    
    # Condition
    condition: str = Field(..., description="Excellent, Good, Fair, Poor")
    accident_history: bool = False
    
    # Value factors
    service_history_complete: bool = True
    modifications: List[str] = Field(default_factory=list)


class EquipmentCollateral(BaseModel):
    """
    Equipment/machinery collateral.
    
    Must register on PPSR for perfection.
    """
    
    # Equipment identification
    equipment_type: str
    manufacturer: str
    model: str
    serial_number: str
    year_of_manufacture: Optional[int] = None
    
    # Specifications
    description: str
    specifications: Dict[str, Any] = Field(default_factory=dict)
    
    # Location
    location_address: str
    is_mobile: bool = False
    
    # Condition
    condition: str
    last_service_date: Optional[date] = None
    service_history_available: bool = True
    
    # Finance
    ppsr_registration: Optional[PPSRRegistration] = None
    
    # Insurance
    replacement_value: Decimal
    age_years: int


class Collateral(BaseModel):
    """
    Main Collateral aggregate (event-sourced).
    
    Reconstructed from events in Kafka.
    """
    
    # Identity
    collateral_id: str
    loan_id: str
    customer_id: str
    
    # Collateral details
    collateral_type: CollateralType
    collateral_description: str
    status: CollateralStatus
    
    # Type-specific details
    real_property: Optional[RealPropertyCollateral] = None
    motor_vehicle: Optional[MotorVehicleCollateral] = None
    equipment: Optional[EquipmentCollateral] = None
    
    # Current valuation
    current_valuation: Optional[CollateralValuation] = None
    estimated_value: Decimal
    last_valuation_date: Optional[date] = None
    next_valuation_due_date: Optional[date] = None
    
    # Security details
    security_position: SecurityPosition
    loan_amount_secured: Decimal
    
    # LVR (Loan-to-Value Ratio)
    current_lvr: Decimal = Field(..., description="Current LVR percentage")
    policy_max_lvr: Decimal = Field(..., description="Maximum allowed LVR")
    lvr_breach: bool = False
    
    # Perfection
    is_perfected: bool = False
    perfection_method: Optional[str] = None
    perfection_date: Optional[date] = None
    
    # PPSR (if applicable)
    ppsr_registration: Optional[PPSRRegistration] = None
    
    # Insurance
    insurance: Optional[CollateralInsurance] = None
    insurance_required: bool = True
    insurance_compliant: bool = False
    
    # LMI (Lenders Mortgage Insurance)
    lmi_required: bool = Field(False, description="Required if LVR > 80%")
    lmi_policy_number: Optional[str] = None
    lmi_provider: Optional[str] = None
    
    # Monitoring
    last_inspection_date: Optional[date] = None
    next_inspection_due_date: Optional[date] = None
    
    # Compliance
    jurisdiction: AustralianState
    regulatory_compliant: bool = True
    
    # Risk scoring
    risk_score: float = Field(0.0, description="ML-computed risk score 0-100")
    risk_factors: List[str] = Field(default_factory=list)
    
    # Metadata
    registered_date: date
    created_at: datetime
    updated_at: datetime
    version: int = 0
    event_stream_version: int = 0
    
    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }
    
    def calculate_lvr(self) -> Decimal:
        """Calculate current LVR."""
        if self.estimated_value > 0:
            return (self.loan_amount_secured / self.estimated_value) * Decimal("100")
        return Decimal("0")
    
    def is_lvr_compliant(self) -> bool:
        """Check if LVR is within policy limits."""
        return self.current_lvr <= self.policy_max_lvr
    
    def is_insurance_compliant(self) -> bool:
        """Check if insurance is current and adequate."""
        if not self.insurance_required:
            return True
        
        if not self.insurance:
            return False
        
        if not self.insurance.is_active:
            return False
        
        if self.insurance.policy_end_date < date.today():
            return False
        
        if self.insurance.sum_insured < self.estimated_value:
            return False
        
        return True
