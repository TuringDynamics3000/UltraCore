"""
UltraCore Account Management Module

Deposits, Transactions, Interest, ML, AI Agents, Payment Rails
"""

__version__ = "1.0.0"

# Core exports
from ultracore.accounts.core.account_models import (
    Account,
    AccountType,
    AccountStatus,
    Transaction,
    TransactionType,
    TransactionStatus,
    AccountBalance,
    AccountHold,
    HoldType,
    InterestRate,
    InterestCalculationMethod
)

from ultracore.accounts.core.account_manager import (
    get_account_manager,
    AccountManager,
    TransactionEngine
)

from ultracore.accounts.core.interest_engine import (
    get_interest_engine,
    InterestEngine,
    InterestAccrual,
    InterestPayment
)

# ML Models
from ultracore.accounts.ml.account_ml_models import (
    get_ml_model_manager,
    MLModelManager,
    BalancePredictionModel,
    TransactionCategorizationModel,
    ChurnPredictionModel,
    AnomalyDetectionModel,
    LifetimeValueModel
)

# AI Agents
from ultracore.accounts.agents.account_agents import (
    get_account_agent_manager,
    AccountAgentManager,
    AccountOptimizationAgent,
    BalanceForecastingAgent,
    FeeOptimizationAgent,
    LiquidityManagementAgent
)

# Payment Rails
from ultracore.accounts.mcp.mcp_payment_rails import (
    get_payment_rail_manager,
    PaymentRailManager,
    PaymentRail,
    PaymentRequest,
    PaymentResponse,
    NPPConnector,
    BPAYConnector,
    SWIFTConnector
)

__all__ = [
    # Core Models
    'Account',
    'AccountType',
    'AccountStatus',
    'Transaction',
    'TransactionType',
    'TransactionStatus',
    'AccountBalance',
    'AccountHold',
    'HoldType',
    'InterestRate',
    'InterestCalculationMethod',
    
    # Managers
    'get_account_manager',
    'AccountManager',
    'TransactionEngine',
    'get_interest_engine',
    'InterestEngine',
    'InterestAccrual',
    'InterestPayment',
    
    # ML Models
    'get_ml_model_manager',
    'MLModelManager',
    'BalancePredictionModel',
    'TransactionCategorizationModel',
    'ChurnPredictionModel',
    'AnomalyDetectionModel',
    'LifetimeValueModel',
    
    # AI Agents
    'get_account_agent_manager',
    'AccountAgentManager',
    'AccountOptimizationAgent',
    'BalanceForecastingAgent',
    'FeeOptimizationAgent',
    'LiquidityManagementAgent',
    
    # Payment Rails
    'get_payment_rail_manager',
    'PaymentRailManager',
    'PaymentRail',
    'PaymentRequest',
    'PaymentResponse',
    'NPPConnector',
    'BPAYConnector',
    'SWIFTConnector',
]
