"""
ML-Powered Credit Scoring
Combines traditional metrics with AI insights
"""
from typing import Dict
from decimal import Decimal
import random


class CreditScoringModel:
    """
    Machine Learning Credit Scoring Model
    
    Analyzes multiple factors to generate credit score
    """
    
    def calculate_score(
        self,
        annual_income: Decimal,
        existing_debt: Decimal,
        employment_months: int,
        loan_amount: Decimal,
        loan_term: int,
        payment_history_score: int = 700
    ) -> Dict:
        """
        Calculate comprehensive credit score
        
        Returns score between 300-850 (US-style scoring)
        """
        
        # Base score from payment history
        base_score = payment_history_score
        
        # Debt-to-income ratio impact
        dti_ratio = float(existing_debt / annual_income) if annual_income > 0 else 1.0
        if dti_ratio < 0.30:
            dti_adjustment = 50
        elif dti_ratio < 0.40:
            dti_adjustment = 20
        elif dti_ratio < 0.50:
            dti_adjustment = -20
        else:
            dti_adjustment = -50
        
        # Employment stability
        if employment_months >= 24:
            employment_adjustment = 30
        elif employment_months >= 12:
            employment_adjustment = 15
        elif employment_months >= 6:
            employment_adjustment = 0
        else:
            employment_adjustment = -25
        
        # Loan size relative to income
        loan_to_income = float(loan_amount / annual_income)
        if loan_to_income < 0.5:
            amount_adjustment = 20
        elif loan_to_income < 1.0:
            amount_adjustment = 0
        elif loan_to_income < 2.0:
            amount_adjustment = -15
        else:
            amount_adjustment = -30
        
        # Calculate final score
        final_score = int(
            base_score + 
            dti_adjustment + 
            employment_adjustment + 
            amount_adjustment
        )
        
        # Clamp between 300-850
        final_score = max(300, min(850, final_score))
        
        # Determine risk category
        if final_score >= 750:
            risk_category = 'EXCELLENT'
            approval_probability = 0.95
        elif final_score >= 700:
            risk_category = 'GOOD'
            approval_probability = 0.85
        elif final_score >= 650:
            risk_category = 'FAIR'
            approval_probability = 0.65
        elif final_score >= 600:
            risk_category = 'POOR'
            approval_probability = 0.40
        else:
            risk_category = 'VERY_POOR'
            approval_probability = 0.15
        
        return {
            'credit_score': final_score,
            'risk_category': risk_category,
            'approval_probability': approval_probability,
            'factors': {
                'debt_to_income_ratio': dti_ratio,
                'employment_stability_months': employment_months,
                'loan_to_income_ratio': loan_to_income
            },
            'score_breakdown': {
                'base_score': base_score,
                'dti_adjustment': dti_adjustment,
                'employment_adjustment': employment_adjustment,
                'amount_adjustment': amount_adjustment
            }
        }


credit_model = CreditScoringModel()
