"""
AI-Powered KYC Verification Service
Uses OpenAI GPT-4 for document analysis
"""
from typing import Dict, Optional
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class KYCVerificationService:
    """
    AI-powered KYC verification
    
    Analyzes documents and customer data for compliance
    """
    
    def __init__(self):
        self.model = 'gpt-4-turbo-preview'
    
    async def verify_identity(
        self,
        customer_data: Dict,
        documents: list
    ) -> Dict:
        """
        Verify customer identity using AI
        
        Returns:
            - verification_result: 'APPROVED' or 'REJECTED' or 'MANUAL_REVIEW'
            - risk_score: 0-100 (lower is better)
            - confidence: 0.0 to 1.0
            - reasons: List of findings
            - compliance_checks: Dictionary of checks performed
        """
        
        prompt = f"""You are a KYC (Know Your Customer) compliance officer at TuringDynamics Bank in Australia.

Analyze this customer for identity verification and AML/CTF compliance.

CUSTOMER INFORMATION:
Name: {customer_data.get('first_name')} {customer_data.get('last_name')}
Date of Birth: {customer_data.get('date_of_birth')}
Email: {customer_data.get('email')}
Phone: {customer_data.get('phone')}
Address: {customer_data.get('address')}

DOCUMENTS SUBMITTED:
{self._format_documents(documents)}

AUSTRALIAN REGULATORY REQUIREMENTS:
- AML/CTF Act 2006 compliance
- 100 point ID check
- Enhanced due diligence for high-risk customers
- AUSTRAC reporting obligations
- Privacy Act 1988 compliance

Perform comprehensive KYC verification and respond in EXACT JSON format:
{{
    "verification_result": "APPROVED or REJECTED or MANUAL_REVIEW",
    "risk_score": 25,
    "confidence": 0.92,
    "identity_verified": true,
    "document_authenticity": "GENUINE or SUSPICIOUS or UNCLEAR",
    "aml_cft_check": "PASS or FAIL or REVIEW_REQUIRED",
    "reasons": ["reason1", "reason2"],
    "red_flags": ["flag1", "flag2"],
    "compliance_checks": {{
        "id_verification_100_points": true,
        "address_verification": true,
        "pep_screening": false,
        "sanctions_check": true,
        "adverse_media": false
    }},
    "recommended_actions": ["action1", "action2"],
    "notes": "Additional compliance notes"
}}

Respond ONLY with valid JSON."""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a KYC compliance expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent compliance checks
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            analysis_text = analysis_text.replace('`json', '').replace('`', '').strip()
            analysis = json.loads(analysis_text)
            
            return {
                'service': 'KYC_AI',
                'model': self.model,
                'verification': analysis
            }
            
        except Exception as e:
            return {
                'service': 'KYC_AI',
                'model': self.model,
                'error': str(e),
                'verification': {
                    'verification_result': 'MANUAL_REVIEW',
                    'risk_score': 50,
                    'confidence': 0.0,
                    'identity_verified': False,
                    'document_authenticity': 'UNCLEAR',
                    'aml_cft_check': 'REVIEW_REQUIRED',
                    'reasons': [f'AI verification failed: {str(e)}'],
                    'red_flags': ['AI_VERIFICATION_ERROR'],
                    'compliance_checks': {},
                    'recommended_actions': ['Manual review by compliance officer'],
                    'notes': 'Escalate to human verification'
                }
            }
    
    async def analyze_document(
        self,
        document_type: str,
        document_number: str,
        issuing_country: str,
        expiry_date: str
    ) -> Dict:
        """
        Analyze individual document
        """
        
        prompt = f"""Analyze this identity document for authenticity and validity:

Document Type: {document_type}
Document Number: {document_number}
Issuing Country: {issuing_country}
Expiry Date: {expiry_date}

Check for:
1. Valid format for document type
2. Expiry status
3. Country of issue authenticity
4. Suspicious patterns

Respond in JSON format:
{{
    "valid_format": true,
    "expired": false,
    "authenticity_score": 0.95,
    "suspicious_indicators": [],
    "notes": "Assessment notes"
}}"""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document authentication expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            analysis_text = analysis_text.replace('`json', '').replace('`', '').strip()
            return json.loads(analysis_text)
            
        except Exception as e:
            return {
                'valid_format': False,
                'expired': False,
                'authenticity_score': 0.5,
                'suspicious_indicators': ['AI_ANALYSIS_FAILED'],
                'notes': f'Error: {str(e)}'
            }
    
    def _format_documents(self, documents: list) -> str:
        """Format documents for prompt"""
        if not documents:
            return "- No documents submitted yet"
        
        formatted = []
        for i, doc in enumerate(documents, 1):
            formatted.append(
                f"{i}. {doc.get('document_type', 'Unknown')}: "
                f"{doc.get('document_number', 'N/A')} "
                f"(Expires: {doc.get('expiry_date', 'N/A')})"
            )
        
        return '\n'.join(formatted)


kyc_service = KYCVerificationService()
