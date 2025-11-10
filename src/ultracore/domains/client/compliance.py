"""
Australian Banking Compliance Framework
Implements AUSTRAC, ASIC, and APRA requirements
"""
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, date
import re


class DocumentType(str, Enum):
    # Primary Photo ID (70 points)
    PASSPORT = 'PASSPORT'
    DRIVERS_LICENSE = 'DRIVERS_LICENSE'
    PROOF_OF_AGE_CARD = 'PROOF_OF_AGE_CARD'
    
    # Secondary ID (40 points)
    MEDICARE_CARD = 'MEDICARE_CARD'
    BIRTH_CERTIFICATE = 'BIRTH_CERTIFICATE'
    CITIZENSHIP_CERTIFICATE = 'CITIZENSHIP_CERTIFICATE'
    
    # Financial ID (25 points each)
    BANK_STATEMENT = 'BANK_STATEMENT'
    RATES_NOTICE = 'RATES_NOTICE'
    UTILITY_BILL = 'UTILITY_BILL'


class AustralianState(str, Enum):
    NSW = 'NSW'
    VIC = 'VIC'
    QLD = 'QLD'
    SA = 'SA'
    WA = 'WA'
    TAS = 'TAS'
    NT = 'NT'
    ACT = 'ACT'


class ComplianceService:
    """
    Australian Financial Services Compliance
    
    Implements:
    - AML/CTF Act 2006
    - AUSTRAC requirements
    - 100 Point ID Check
    - PEP screening
    - Sanctions checking
    """
    
    DOCUMENT_POINTS = {
        DocumentType.PASSPORT: 70,
        DocumentType.DRIVERS_LICENSE: 70,
        DocumentType.PROOF_OF_AGE_CARD: 70,
        DocumentType.MEDICARE_CARD: 40,
        DocumentType.BIRTH_CERTIFICATE: 70,
        DocumentType.CITIZENSHIP_CERTIFICATE: 70,
        DocumentType.BANK_STATEMENT: 25,
        DocumentType.RATES_NOTICE: 25,
        DocumentType.UTILITY_BILL: 25
    }
    
    @staticmethod
    def calculate_id_points(documents: List[Dict]) -> int:
        """
        Australian 100 Point ID Check
        
        Minimum requirement: 100 points from approved documents
        Must include at least one primary photo ID
        """
        total_points = 0
        has_primary_id = False
        
        for doc in documents:
            doc_type = doc.get('document_type')
            if doc_type in [DocumentType.PASSPORT.value, DocumentType.DRIVERS_LICENSE.value]:
                has_primary_id = True
            
            points = ComplianceService.DOCUMENT_POINTS.get(
                DocumentType(doc_type), 0
            )
            total_points += points
        
        return total_points if has_primary_id else 0
    
    @staticmethod
    def validate_tfn(tfn: Optional[str]) -> bool:
        """
        Validate Australian Tax File Number
        
        Format: XXX XXX XXX (9 digits)
        """
        if not tfn:
            return False
        
        # Remove spaces and hyphens
        tfn = tfn.replace(' ', '').replace('-', '')
        
        # Must be 9 digits
        if not re.match(r'^\d{9}$', tfn):
            return False
        
        # TFN algorithm validation
        weights = [1, 4, 3, 7, 5, 8, 6, 9, 10]
        total = sum(int(tfn[i]) * weights[i] for i in range(9))
        
        return total % 11 == 0
    
    @staticmethod
    def validate_abn(abn: Optional[str]) -> bool:
        """
        Validate Australian Business Number
        
        Format: XX XXX XXX XXX (11 digits)
        """
        if not abn:
            return False
        
        abn = abn.replace(' ', '').replace('-', '')
        
        if not re.match(r'^\d{11}$', abn):
            return False
        
        # ABN algorithm
        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        # Subtract 1 from first digit
        digits = [int(abn[0]) - 1] + [int(d) for d in abn[1:]]
        total = sum(digits[i] * weights[i] for i in range(11))
        
        return total % 89 == 0
    
    @staticmethod
    def check_age_restriction(date_of_birth: str, minimum_age: int = 18) -> Dict:
        """
        Verify customer meets minimum age requirement
        
        Australian banking: Must be 18+ for full account
        """
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            return {
                'meets_requirement': age >= minimum_age,
                'age': age,
                'minimum_age': minimum_age,
                'reason': None if age >= minimum_age else f'Customer is {age}, minimum is {minimum_age}'
            }
        except Exception as e:
            return {
                'meets_requirement': False,
                'age': None,
                'minimum_age': minimum_age,
                'reason': f'Invalid date of birth: {str(e)}'
            }
    
    @staticmethod
    def austrac_reporting_threshold_check(transaction_amount: float) -> Dict:
        """
        AUSTRAC Reporting Thresholds
        
        - Threshold Transaction Reports (TTR): AUD ,000+
        - Suspicious Matter Reports (SMR): Any amount if suspicious
        - International Funds Transfer Instructions (IFTI): All amounts
        """
        requires_ttr = transaction_amount >= 10000
        
        return {
            'amount': transaction_amount,
            'requires_ttr': requires_ttr,
            'threshold': 10000,
            'reporting_requirement': 'TTR required within 10 business days' if requires_ttr else None
        }
    
    @staticmethod
    def assess_aml_risk(customer_data: Dict) -> Dict:
        """
        AML/CTF Risk Assessment
        
        Risk factors:
        - High-risk occupation
        - High-risk country
        - Cash-intensive business
        - PEP status
        - Large transactions
        """
        risk_score = 0
        risk_factors = []
        
        # Check occupation
        high_risk_occupations = [
            'money transfer', 'currency exchange', 'casino', 
            'real estate', 'lawyer', 'accountant', 'trust provider'
        ]
        occupation = customer_data.get('occupation', '').lower()
        if any(occ in occupation for occ in high_risk_occupations):
            risk_score += 30
            risk_factors.append('HIGH_RISK_OCCUPATION')
        
        # Check transaction patterns
        expected_transactions = customer_data.get('expected_transaction_volume', 0)
        if expected_transactions > 100000:
            risk_score += 20
            risk_factors.append('HIGH_TRANSACTION_VOLUME')
        
        # Check PEP status
        if customer_data.get('is_pep', False):
            risk_score += 40
            risk_factors.append('POLITICALLY_EXPOSED_PERSON')
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'HIGH'
            enhanced_dd_required = True
        elif risk_score >= 40:
            risk_level = 'MEDIUM'
            enhanced_dd_required = True
        else:
            risk_level = 'LOW'
            enhanced_dd_required = False
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'enhanced_dd_required': enhanced_dd_required,
            'ongoing_monitoring': risk_level in ['MEDIUM', 'HIGH']
        }


class AustralianKYCRequirements:
    """
    Complete Australian KYC Requirements
    """
    
    REQUIRED_CHECKS = [
        'identity_verification',
        'age_verification',
        '100_point_check',
        'address_verification',
        'aml_screening',
        'sanctions_screening',
        'pep_screening'
    ]
    
    ENHANCED_DUE_DILIGENCE_TRIGGERS = [
        'pep_identified',
        'high_risk_country',
        'cash_intensive_business',
        'large_transactions',
        'complex_ownership_structure'
    ]
    
    @staticmethod
    def get_compliance_checklist() -> Dict:
        return {
            'customer_identification': {
                'full_name': 'REQUIRED',
                'date_of_birth': 'REQUIRED',
                'residential_address': 'REQUIRED',
                'contact_details': 'REQUIRED'
            },
            'identity_documents': {
                'primary_photo_id': 'REQUIRED (70 points)',
                'secondary_documents': 'REQUIRED (minimum 100 points total)',
                'document_verification': 'REQUIRED (DVS check)'
            },
            'aml_ctf_checks': {
                'pep_screening': 'REQUIRED',
                'sanctions_screening': 'REQUIRED',
                'adverse_media_check': 'RECOMMENDED',
                'source_of_funds': 'REQUIRED for high-risk'
            },
            'ongoing_requirements': {
                'transaction_monitoring': 'REQUIRED',
                'annual_review': 'REQUIRED for high-risk',
                'record_retention': 'REQUIRED (7 years)'
            }
        }
