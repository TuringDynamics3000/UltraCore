"""
UltraCore Customer Management Module

Customer lifecycle, KYC/AML, Graph, AI Agents
"""

__version__ = "1.0.0"

# Core exports
from ultracore.customers.core.customer_models import (
    Customer,
    CustomerType,
    CustomerStatus,
    CustomerSegment,
    RiskRating,
    PEPStatus,
    KYCVerification,
    KYCStatus
)

from ultracore.customers.core.customer_manager import (
    get_customer_manager,
    CustomerManager
)

from ultracore.customers.core.customer_graph import (
    get_customer_graph,
    CustomerGraph,
    RelationshipType
)

# AI Agents
from ultracore.customers.agents.kyc_aml_agent import (
    get_kyc_aml_agent,
    KYCAMLAgent
)

from ultracore.customers.agents.fraud_detection_agent import (
    get_fraud_detection_agent,
    FraudDetectionAgent
)

from ultracore.customers.agents.risk_assessment_agent import (
    get_risk_assessment_agent,
    RiskAssessmentAgent
)

from ultracore.customers.agents.recommendation_agent import (
    get_recommendation_agent,
    RecommendationAgent
)

__all__ = [
    # Core
    'Customer',
    'CustomerType',
    'CustomerStatus',
    'CustomerSegment',
    'RiskRating',
    'PEPStatus',
    'KYCVerification',
    'KYCStatus',
    'get_customer_manager',
    'CustomerManager',
    'get_customer_graph',
    'CustomerGraph',
    'RelationshipType',
    
    # AI Agents
    'get_kyc_aml_agent',
    'KYCAMLAgent',
    'get_fraud_detection_agent',
    'FraudDetectionAgent',
    'get_risk_assessment_agent',
    'RiskAssessmentAgent',
    'get_recommendation_agent',
    'RecommendationAgent',
]
