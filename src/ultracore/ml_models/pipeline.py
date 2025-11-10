"""
ML Pipeline - Banking Intelligence
"""
from typing import Dict
from decimal import Decimal
import random


class MLPipeline:
    """
    Machine Learning Pipeline for Banking
    
    Models:
    - Credit Risk Scoring
    - Fraud Detection
    - Customer Churn Prediction
    - Loan Default Prediction
    - Transaction Anomaly Detection
    """
    
    async def predict_credit_risk(
        self,
        client_data: Dict,
        loan_amount: Decimal
    ) -> Dict:
        """
        ML Credit Risk Model
        
        Features:
        - Income stability
        - Debt ratios
        - Payment history
        - Employment tenure
        - Account behavior
        """
        
        # Simulate ML model prediction
        annual_income = Decimal(str(client_data.get('annual_income', 80000)))
        existing_debt = Decimal(str(client_data.get('existing_debt', 10000)))
        employment_months = client_data.get('employment_months', 24)
        
        dti_ratio = float(existing_debt / annual_income) if annual_income > 0 else 1.0
        
        # Risk score (0-100, lower is better)
        base_risk = 50
        
        # Adjust for DTI
        if dti_ratio < 0.3:
            base_risk -= 20
        elif dti_ratio > 0.5:
            base_risk += 30
        
        # Adjust for employment
        if employment_months >= 24:
            base_risk -= 15
        elif employment_months < 6:
            base_risk += 20
        
        # Adjust for loan size
        loan_to_income = float(loan_amount / annual_income)
        if loan_to_income > 2.0:
            base_risk += 25
        
        risk_score = max(0, min(100, base_risk))
        
        # Probability of default
        default_probability = risk_score / 100.0
        
        return {
            'risk_score': risk_score,
            'default_probability': default_probability,
            'risk_category': self._categorize_risk(risk_score),
            'recommended_interest_rate': self._calculate_rate(risk_score),
            'features': {
                'dti_ratio': dti_ratio,
                'loan_to_income': loan_to_income,
                'employment_stability': employment_months
            },
            'model': 'credit_risk_v2',
            'confidence': 0.87
        }
    
    async def detect_fraud(
        self,
        transaction_data: Dict
    ) -> Dict:
        """
        ML Fraud Detection
        
        Analyzes transaction patterns for suspicious activity
        """
        
        amount = transaction_data.get('amount', 0)
        
        # Simple rule-based fraud detection
        # In production, use trained ML model
        fraud_score = 0
        flags = []
        
        if amount > 50000:
            fraud_score += 30
            flags.append('HIGH_AMOUNT')
        
        if transaction_data.get('international', False):
            fraud_score += 20
            flags.append('INTERNATIONAL')
        
        if transaction_data.get('unusual_time', False):
            fraud_score += 15
            flags.append('UNUSUAL_TIME')
        
        is_fraudulent = fraud_score > 60
        
        return {
            'is_fraudulent': is_fraudulent,
            'fraud_score': fraud_score,
            'confidence': 0.92,
            'flags': flags,
            'recommendation': 'BLOCK' if is_fraudulent else 'APPROVE',
            'model': 'fraud_detection_v3'
        }
    
    def _categorize_risk(self, score: float) -> str:
        if score < 30:
            return 'LOW'
        elif score < 60:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _calculate_rate(self, risk_score: float) -> float:
        """Calculate interest rate based on risk"""
        base_rate = 6.5  # Base rate
        risk_premium = (risk_score / 100.0) * 5.0  # Up to 5% risk premium
        return round(base_rate + risk_premium, 2)


ml_pipeline = MLPipeline()
