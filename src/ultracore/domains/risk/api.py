"""
Risk Domain API
"""
from fastapi import APIRouter, HTTPException
import uuid

from ultracore.domains.risk.aggregate import (
    RiskAggregate, RiskAssessmentRequest, RiskType
)

router = APIRouter()


@router.post('/assess')
async def assess_risk(request: RiskAssessmentRequest):
    '''Conduct risk assessment'''
    risk_id = f'RISK-{str(uuid.uuid4())[:8]}'
    
    risk = RiskAggregate(risk_id)
    
    entity_data = {
        'annual_income': 80000,
        'existing_debt': 15000,
        'employment_months': 36,
        'loan_amount': 50000
    }
    
    result = await risk.assess_risk(
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        risk_type=request.risk_type,
        data=entity_data
    )
    
    return {
        'risk_id': risk_id,
        'entity_id': request.entity_id,
        'risk_type': request.risk_type.value,
        'risk_score': risk.risk_score,
        'risk_level': risk.risk_level.value,
        'result': result
    }


@router.get('/{risk_id}')
async def get_risk_assessment(risk_id: str):
    '''Get risk assessment details'''
    risk = RiskAggregate(risk_id)
    await risk.load_from_events()
    
    if not risk.entity_id:
        raise HTTPException(status_code=404, detail='Risk assessment not found')
    
    return {
        'risk_id': risk.risk_id,
        'entity_id': risk.entity_id,
        'entity_type': risk.entity_type,
        'risk_type': risk.risk_type.value if risk.risk_type else None,
        'risk_score': risk.risk_score,
        'risk_level': risk.risk_level.value
    }


@router.get('/portfolio/overview')
async def get_portfolio_risk():
    '''Get overall portfolio risk metrics'''
    return {
        'total_assessments': 0,
        'high_risk_entities': 0,
        'average_risk_score': 0.0,
        'risk_distribution': {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'CRITICAL': 0
        }
    }
