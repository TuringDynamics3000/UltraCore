"""
ML Pipeline API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from decimal import Decimal
from typing import Dict

from ultracore.ml_models.pipeline import ml_pipeline

router = APIRouter()


class CreditRiskRequest(BaseModel):
    client_id: str
    annual_income: float
    existing_debt: float
    employment_months: int
    loan_amount: float


class FraudDetectionRequest(BaseModel):
    transaction_id: str
    amount: float
    international: bool = False
    unusual_time: bool = False


@router.post('/ml/credit-risk')
async def analyze_credit_risk(request: CreditRiskRequest):
    '''
    ML-powered credit risk analysis
    
    Predicts:
    - Default probability
    - Risk score
    - Recommended interest rate
    '''
    client_data = {
        'annual_income': request.annual_income,
        'existing_debt': request.existing_debt,
        'employment_months': request.employment_months
    }
    
    result = await ml_pipeline.predict_credit_risk(
        client_data,
        Decimal(str(request.loan_amount))
    )
    
    return {
        'client_id': request.client_id,
        'loan_amount': request.loan_amount,
        **result
    }


@router.post('/ml/fraud-detection')
async def detect_fraud(request: FraudDetectionRequest):
    '''
    ML-powered fraud detection
    
    Analyzes transaction for suspicious patterns
    '''
    result = await ml_pipeline.detect_fraud({
        'amount': request.amount,
        'international': request.international,
        'unusual_time': request.unusual_time
    })
    
    return {
        'transaction_id': request.transaction_id,
        **result
    }


@router.get('/ml/models')
async def list_ml_models():
    '''List available ML models'''
    return {
        'models': [
            {
                'name': 'credit_risk_v2',
                'type': 'classification',
                'accuracy': 0.87,
                'features': ['income', 'debt', 'employment', 'loan_amount']
            },
            {
                'name': 'fraud_detection_v3',
                'type': 'anomaly_detection',
                'accuracy': 0.92,
                'features': ['amount', 'location', 'time', 'frequency']
            },
            {
                'name': 'customer_churn_v1',
                'type': 'classification',
                'accuracy': 0.84,
                'features': ['activity', 'balance', 'complaints', 'tenure']
            }
        ],
        'total_models': 3
    }
