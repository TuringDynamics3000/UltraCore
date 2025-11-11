"""
UltraCore Account Management - AI Agents

Agentic AI for intelligent account management:
- Account Optimization Agent (rate maximization)
- Balance Forecasting Agent (cash flow prediction)
- Fee Optimization Agent (fee minimization)
- Liquidity Management Agent (reserve optimization)

Each agent:
- Has tools (functions they can call)
- Uses reasoning (explains decisions)
- Takes actions (autonomous operations)
- Learns from outcomes (reinforcement learning)
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import uuid

from ultracore.customers.agents.agent_base import (
    BaseAgent, AgentType, AgentTool, ToolType, AgentDecision
)
from ultracore.accounts.core.account_models import (
    Account, AccountType, Transaction
)
from ultracore.accounts.core.account_manager import get_account_manager
from ultracore.accounts.ml.account_ml_models import get_ml_model_manager


# ============================================================================
# Agent Models
# ============================================================================

class OptimizationGoal(str, Enum):
    """Optimization goals"""
    MAXIMIZE_INTEREST = "MAXIMIZE_INTEREST"
    MINIMIZE_FEES = "MINIMIZE_FEES"
    MAINTAIN_LIQUIDITY = "MAINTAIN_LIQUIDITY"
    BALANCE_ALL = "BALANCE_ALL"


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation from agent"""
    recommendation_id: str
    agent_id: str
    account_id: str
    
    # Recommendation
    action: str  # TRANSFER, UPGRADE_PRODUCT, CONSOLIDATE, etc.
    action_description: str
    
    # Expected impact
    expected_benefit: Decimal  # Expected financial benefit
    expected_cost: Decimal = Decimal('0.0')
    net_benefit: Decimal = Decimal('0.0')
    
    # Reasoning
    reasoning_steps: List[str] = field(default_factory=list)
    confidence: Decimal = Decimal('0.0')
    
    # Execution
    auto_executable: bool = False
    requires_approval: bool = True
    
    # Priority
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, URGENT
    valid_until: Optional[date] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Account Optimization Agent
# ============================================================================

class AccountOptimizationAgent(BaseAgent):
    """
    Account optimization agent
    
    Optimizes:
    - Interest earnings (rate shopping)
    - Fee minimization (fee waivers, product changes)
    - Account consolidation
    - Balance allocation
    - Product mix
    
    Autonomous actions:
    - Move funds to higher-interest accounts
    - Consolidate low-balance accounts
    - Request fee waivers
    - Recommend product upgrades
    """
    
    def __init__(self):
        system_prompt = """You are an expert account optimization agent.
Your goal is to maximize customer value by optimizing account settings and balances.

You must:
- Analyze customer's account portfolio
- Identify optimization opportunities
- Calculate expected benefits
- Recommend optimal actions
- Explain reasoning clearly
- Prioritize by impact

You balance financial optimization with customer convenience."""

        super().__init__(
            agent_id=f"AGENT-ACCOPT-{uuid.uuid4().hex[:8].upper()}",
            agent_type=AgentType.RECOMMENDATION,
            agent_name="Account Optimization Agent",
            system_prompt=system_prompt
        )
        
        self.account_manager = get_account_manager()
        self.ml_models = get_ml_model_manager()
        
        # Recommendations storage
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
    
    def _register_tools(self):
        """Register optimization tools"""
        
        self.register_tool(AgentTool(
            tool_id="analyze_portfolio",
            tool_name="analyze_account_portfolio",
            tool_type=ToolType.CALCULATION,
            description="Analyze customer's complete account portfolio",
            parameters={
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'string'}
                },
                'required': ['customer_id']
            },
            function=self._analyze_portfolio
        ))
        
        self.register_tool(AgentTool(
            tool_id="calculate_interest_opportunity",
            tool_name="calculate_interest_opportunity",
            tool_type=ToolType.CALCULATION,
            description="Calculate potential interest earnings from optimization",
            parameters={
                'type': 'object',
                'properties': {
                    'account_id': {'type': 'string'},
                    'target_rate': {'type': 'number'}
                },
                'required': ['account_id', 'target_rate']
            },
            function=self._calculate_interest_opportunity
        ))
        
        self.register_tool(AgentTool(
            tool_id="find_fee_waivers",
            tool_name="find_fee_waiver_opportunities",
            tool_type=ToolType.CALCULATION,
            description="Find opportunities to waive fees",
            parameters={
                'type': 'object',
                'properties': {
                    'account_id': {'type': 'string'}
                },
                'required': ['account_id']
            },
            function=self._find_fee_waivers
        ))
    
    async def _make_decision(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> AgentDecision:
        """Make optimization decision"""
        
        decision_id = f"DEC-{uuid.uuid4().hex[:12].upper()}"
        customer_id = context.get('customer_id')
        
        reasoning_steps = []
        evidence = {}
        recommendations = []
        
        # Analyze portfolio
        portfolio_analysis = await self._analyze_portfolio(customer_id=customer_id)
        
        reasoning_steps.append(f"Analyzed portfolio: {portfolio_analysis['account_count']} accounts")
        reasoning_steps.append(f"Total balance: ${portfolio_analysis['total_balance']}")
        reasoning_steps.append(f"Current annual interest: ${portfolio_analysis['current_annual_interest']}")
        
        evidence['portfolio'] = portfolio_analysis
        
        # Find optimization opportunities
        for account_id in portfolio_analysis['account_ids']:
            account = await self.account_manager.get_account(account_id)
            
            if not account:
                continue
            
            # Check interest rate optimization
            if account.interest_bearing:
                opportunity = await self._calculate_interest_opportunity(
                    account_id=account_id,
                    target_rate=5.0  # Target 5% APR
                )
                
                if opportunity['additional_annual_interest'] > Decimal('100.0'):
                    rec = OptimizationRecommendation(
                        recommendation_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                        agent_id=self.agent_id,
                        account_id=account_id,
                        action="UPGRADE_RATE",
                        action_description=f"Move to higher-rate product (current: {opportunity['current_rate']}%, target: {opportunity['target_rate']}%)",
                        expected_benefit=opportunity['additional_annual_interest'],
                        net_benefit=opportunity['additional_annual_interest'],
                        confidence=Decimal('0.85'),
                        priority="HIGH"
                    )
                    
                    rec.reasoning_steps = [
                        f"Current rate: {opportunity['current_rate']}%",
                        f"Available rate: {opportunity['target_rate']}%",
                        f"Additional annual interest: ${opportunity['additional_annual_interest']}"
                    ]
                    
                    recommendations.append(rec)
                    self.recommendations[rec.recommendation_id] = rec
                    
                    reasoning_steps.append(f"💡 Opportunity: Increase rate on account {account.account_number}")
            
            # Check fee optimization
            fee_opportunities = await self._find_fee_waivers(account_id=account_id)
            
            if fee_opportunities['potential_savings'] > Decimal('50.0'):
                rec = OptimizationRecommendation(
                    recommendation_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                    agent_id=self.agent_id,
                    account_id=account_id,
                    action="WAIVE_FEES",
                    action_description=f"Request fee waivers (potential savings: ${fee_opportunities['potential_savings']}/year)",
                    expected_benefit=fee_opportunities['potential_savings'],
                    net_benefit=fee_opportunities['potential_savings'],
                    confidence=Decimal('0.75'),
                    priority="MEDIUM"
                )
                
                rec.reasoning_steps = fee_opportunities['eligible_waivers']
                
                recommendations.append(rec)
                self.recommendations[rec.recommendation_id] = rec
                
                reasoning_steps.append(f"💡 Opportunity: Waive fees on account {account.account_number}")
        
        # Calculate total potential benefit
        total_benefit = sum(r.net_benefit for r in recommendations)
        
        reasoning_steps.append(f"\n🎯 Total optimization potential: ${total_benefit}/year")
        reasoning_steps.append(f"📊 Recommendations: {len(recommendations)}")
        
        evidence['recommendations'] = [
            {
                'action': r.action,
                'benefit': float(r.expected_benefit),
                'priority': r.priority
            }
            for r in recommendations
        ]
        
        decision = AgentDecision(
            decision_id=decision_id,
            agent_id=self.agent_id,
            decision_type="OPTIMIZE",
            decision=recommendations,
            confidence=0.8,
            reasoning=reasoning_steps,
            evidence=evidence
        )
        
        return decision
    
    async def _analyze_portfolio(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """Analyze customer's account portfolio"""
        
        accounts = await self.account_manager.get_customer_accounts(customer_id)
        
        total_balance = sum(a.balance.ledger_balance for a in accounts)
        
        # Calculate current annual interest
        current_annual_interest = Decimal('0.0')
        for account in accounts:
            if account.interest_bearing and account.current_interest_rate:
                rate = account.current_interest_rate.annual_rate / Decimal('100')
                annual_interest = account.balance.ledger_balance * rate
                current_annual_interest += annual_interest
        
        # Calculate current annual fees
        current_annual_fees = Decimal('0.0')
        for account in accounts:
            for fee in account.fee_structure:
                if fee.active and fee.frequency == 'MONTHLY':
                    current_annual_fees += fee.amount * 12
        
        return {
            'customer_id': customer_id,
            'account_count': len(accounts),
            'account_ids': [a.account_id for a in accounts],
            'total_balance': total_balance,
            'current_annual_interest': current_annual_interest,
            'current_annual_fees': current_annual_fees,
            'net_earnings': current_annual_interest - current_annual_fees
        }
    
    async def _calculate_interest_opportunity(
        self,
        account_id: str,
        target_rate: float
    ) -> Dict[str, Any]:
        """Calculate interest rate optimization opportunity"""
        
        account = await self.account_manager.get_account(account_id)
        if not account or not account.interest_bearing:
            return {'additional_annual_interest': Decimal('0.0')}
        
        current_rate = Decimal('0.0')
        if account.current_interest_rate:
            current_rate = account.current_interest_rate.annual_rate
        
        target_rate_decimal = Decimal(str(target_rate))
        
        # Calculate additional interest
        current_annual = account.balance.ledger_balance * (current_rate / Decimal('100'))
        target_annual = account.balance.ledger_balance * (target_rate_decimal / Decimal('100'))
        additional = target_annual - current_annual
        
        return {
            'account_id': account_id,
            'current_rate': float(current_rate),
            'target_rate': target_rate,
            'balance': account.balance.ledger_balance,
            'current_annual_interest': current_annual,
            'target_annual_interest': target_annual,
            'additional_annual_interest': additional
        }
    
    async def _find_fee_waivers(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """Find fee waiver opportunities"""
        
        account = await self.account_manager.get_account(account_id)
        if not account:
            return {'potential_savings': Decimal('0.0')}
        
        potential_savings = Decimal('0.0')
        eligible_waivers = []
        
        for fee in account.fee_structure:
            if fee.active and fee.can_be_waived:
                # Check waiver conditions
                conditions_met = True
                
                for condition in fee.waiver_conditions:
                    if condition == "MIN_BALANCE_5000":
                        if account.balance.ledger_balance >= Decimal('5000.0'):
                            conditions_met = True
                        else:
                            conditions_met = False
                    elif condition == "MONTHLY_DEPOSIT_1000":
                        # In production: check actual deposits
                        conditions_met = True
                
                if conditions_met:
                    if fee.frequency == 'MONTHLY':
                        annual_savings = fee.amount * 12
                    else:
                        annual_savings = fee.amount
                    
                    potential_savings += annual_savings
                    eligible_waivers.append(f"Waive {fee.fee_name}: ${annual_savings}/year")
        
        return {
            'account_id': account_id,
            'potential_savings': potential_savings,
            'eligible_waivers': eligible_waivers
        }


# ============================================================================
# Balance Forecasting Agent
# ============================================================================

class BalanceForecastingAgent(BaseAgent):
    """
    Balance forecasting agent using ML
    
    Forecasts:
    - Future balances (30, 60, 90 days)
    - Cash flow patterns
    - Liquidity needs
    - Overdraft risk
    
    Actions:
    - Alert on low balance prediction
    - Recommend fund transfers
    - Suggest overdraft protection
    - Optimize sweep accounts
    """
    
    def __init__(self):
        system_prompt = """You are an expert balance forecasting agent.
Your goal is to predict future account balances and cash flow needs.

You must:
- Analyze historical transaction patterns
- Predict future balances with confidence
- Identify liquidity risks
- Recommend proactive actions
- Explain predictions clearly

You help customers avoid overdrafts and optimize cash management."""

        super().__init__(
            agent_id=f"AGENT-BALFC-{uuid.uuid4().hex[:8].upper()}",
            agent_type=AgentType.RECOMMENDATION,
            agent_name="Balance Forecasting Agent",
            system_prompt=system_prompt
        )
        
        self.account_manager = get_account_manager()
        self.ml_models = get_ml_model_manager()
    
    def _register_tools(self):
        """Register forecasting tools"""
        
        self.register_tool(AgentTool(
            tool_id="forecast_balance",
            tool_name="forecast_future_balance",
            tool_type=ToolType.ML_MODEL,
            description="Forecast future account balance using ML",
            parameters={
                'type': 'object',
                'properties': {
                    'account_id': {'type': 'string'},
                    'days_ahead': {'type': 'integer'}
                },
                'required': ['account_id', 'days_ahead']
            },
            function=self._forecast_balance
        ))
        
        self.register_tool(AgentTool(
            tool_id="assess_liquidity_risk",
            tool_name="assess_liquidity_risk",
            tool_type=ToolType.CALCULATION,
            description="Assess risk of insufficient funds",
            parameters={
                'type': 'object',
                'properties': {
                    'account_id': {'type': 'string'}
                },
                'required': ['account_id']
            },
            function=self._assess_liquidity_risk
        ))
    
    async def _make_decision(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> AgentDecision:
        """Make forecasting decision"""
        
        decision_id = f"DEC-{uuid.uuid4().hex[:12].upper()}"
        account_id = context.get('account_id')
        
        reasoning_steps = []
        evidence = {}
        
        # Forecast balance
        forecast = await self._forecast_balance(
            account_id=account_id,
            days_ahead=30
        )
        
        reasoning_steps.append(f"30-day forecast generated")
        reasoning_steps.append(f"Current balance: ${forecast['current_balance']}")
        reasoning_steps.append(f"Predicted balance (30d): ${forecast['predicted_balance']}")
        reasoning_steps.append(f"Confidence: {float(forecast['confidence']) * 100:.1f}%")
        
        # Assess liquidity risk
        liquidity_risk = await self._assess_liquidity_risk(account_id=account_id)
        
        reasoning_steps.append(f"\nLiquidity risk: {liquidity_risk['risk_level']}")
        
        if liquidity_risk['risk_level'] in ['HIGH', 'CRITICAL']:
            reasoning_steps.append(f"⚠️ WARNING: Low balance predicted in {liquidity_risk['days_until_low_balance']} days")
            reasoning_steps.append(f"Recommended action: {liquidity_risk['recommendation']}")
        
        evidence['forecast'] = forecast
        evidence['liquidity_risk'] = liquidity_risk
        
        decision = AgentDecision(
            decision_id=decision_id,
            agent_id=self.agent_id,
            decision_type="FORECAST",
            decision=forecast,
            confidence=float(forecast['confidence']),
            reasoning=reasoning_steps,
            evidence=evidence
        )
        
        return decision
    
    async def _forecast_balance(
        self,
        account_id: str,
        days_ahead: int
    ) -> Dict[str, Any]:
        """Forecast future balance using ML"""
        
        account = await self.account_manager.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Use ML model for prediction
        predictions = await self.ml_models.balance_predictor.predict_balance(
            account,
            prediction_days=days_ahead
        )
        
        if predictions:
            final_prediction = predictions[-1]
            
            return {
                'account_id': account_id,
                'current_balance': account.balance.ledger_balance,
                'predicted_balance': final_prediction.predicted_balance,
                'confidence': final_prediction.confidence,
                'prediction_date': final_prediction.prediction_date.isoformat(),
                'confidence_lower': final_prediction.confidence_interval_lower,
                'confidence_upper': final_prediction.confidence_interval_upper
            }
        
        return {
            'account_id': account_id,
            'current_balance': account.balance.ledger_balance,
            'predicted_balance': account.balance.ledger_balance,
            'confidence': Decimal('0.5')
        }
    
    async def _assess_liquidity_risk(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """Assess liquidity risk"""
        
        account = await self.account_manager.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Get 30-day forecast
        predictions = await self.ml_models.balance_predictor.predict_balance(
            account,
            prediction_days=30
        )
        
        # Find first day balance goes below threshold
        threshold = account.balance.minimum_balance or Decimal('0.0')
        days_until_low = None
        
        for i, pred in enumerate(predictions):
            if pred.predicted_balance < threshold:
                days_until_low = i + 1
                break
        
        # Determine risk level
        if days_until_low is None:
            risk_level = "LOW"
            recommendation = "No action needed"
        elif days_until_low <= 7:
            risk_level = "CRITICAL"
            recommendation = "Transfer funds immediately"
        elif days_until_low <= 14:
            risk_level = "HIGH"
            recommendation = "Plan fund transfer within 7 days"
        else:
            risk_level = "MEDIUM"
            recommendation = "Monitor balance closely"
        
        return {
            'account_id': account_id,
            'risk_level': risk_level,
            'days_until_low_balance': days_until_low,
            'threshold': threshold,
            'recommendation': recommendation
        }


# ============================================================================
# Fee Optimization Agent
# ============================================================================

class FeeOptimizationAgent(BaseAgent):
    """
    Fee optimization agent
    
    Minimizes:
    - Account maintenance fees
    - Transaction fees
    - Overdraft fees
    - ATM fees
    
    Strategies:
    - Meet fee waiver conditions
    - Consolidate accounts
    - Change to fee-free products
    - Negotiate fee reductions
    """
    
    def __init__(self):
        system_prompt = """You are an expert fee optimization agent.
Your goal is to minimize fees while maintaining service quality.

You must:
- Identify all fees being charged
- Find waiver opportunities
- Recommend product changes
- Calculate potential savings
- Prioritize by impact

You help customers keep more of their money."""

        super().__init__(
            agent_id=f"AGENT-FEEOPT-{uuid.uuid4().hex[:8].upper()}",
            agent_type=AgentType.RECOMMENDATION,
            agent_name="Fee Optimization Agent",
            system_prompt=system_prompt
        )
        
        self.account_manager = get_account_manager()


# ============================================================================
# Liquidity Management Agent
# ============================================================================

class LiquidityManagementAgent(BaseAgent):
    """
    Liquidity management agent for bank operations
    
    Manages:
    - Reserve requirements
    - Interbank lending
    - Cash positioning
    - Funding optimization
    
    Bank-level operations (not customer-facing)
    """
    
    def __init__(self):
        system_prompt = """You are an expert liquidity management agent.
Your goal is to optimize the bank's liquidity position.

You must:
- Monitor reserve requirements
- Optimize funding costs
- Manage cash positions
- Minimize idle cash
- Ensure regulatory compliance

You balance safety, liquidity, and profitability."""

        super().__init__(
            agent_id=f"AGENT-LIQMGMT-{uuid.uuid4().hex[:8].upper()}",
            agent_type=AgentType.RISK_ASSESSMENT,
            agent_name="Liquidity Management Agent",
            system_prompt=system_prompt
        )


# ============================================================================
# Agent Manager
# ============================================================================

class AccountAgentManager:
    """Central manager for all account agents"""
    
    def __init__(self):
        self.optimization_agent = AccountOptimizationAgent()
        self.forecasting_agent = BalanceForecastingAgent()
        self.fee_optimization_agent = FeeOptimizationAgent()
        self.liquidity_agent = LiquidityManagementAgent()
    
    async def run_optimization(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """Run all optimization agents"""
        
        results = {}
        
        # Account optimization
        opt_decision = await self.optimization_agent.process(
            "",
            context={'customer_id': customer_id}
        )
        results['optimization'] = opt_decision
        
        return results


# ============================================================================
# Global Singleton
# ============================================================================

_account_agent_manager: Optional[AccountAgentManager] = None

def get_account_agent_manager() -> AccountAgentManager:
    """Get singleton account agent manager"""
    global _account_agent_manager
    if _account_agent_manager is None:
        _account_agent_manager = AccountAgentManager()
    return _account_agent_manager
