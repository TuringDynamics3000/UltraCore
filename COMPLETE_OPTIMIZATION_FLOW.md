# Complete Optimization Flow
## From Risk Questionnaire to Portfolio Execution

**Version:** 1.0  
**Date:** November 15, 2025  
**System:** UltraWealth with UltraOptimiser Methodology  

---

## Overview: 8-Step Process

```
┌──────────────────────────────────────────────────────────────────┐
│                    CUSTOMER ONBOARDING                           │
│                                                                  │
│  Step 1: Risk Questionnaire                                     │
│  Step 2: Goal Definition                                        │
│  Step 3: Pod Allocation                                         │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    POD OPTIMIZATION                              │
│                                                                  │
│  Step 4: Pod-Level RL Optimization (4 Agents)                  │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                 MASTER PORTFOLIO OPTIMIZATION                    │
│                                                                  │
│  Step 5: Consolidation & Deduplication                          │
│  Step 6: Tax Optimization                                       │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    EXECUTION & MONITORING                        │
│                                                                  │
│  Step 7: Trade Execution (OpenMarkets)                          │
│  Step 8: Continuous Monitoring & Rebalancing                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Risk Questionnaire

### Input: Customer Information

```json
{
  "customer_id": "CUST_12345",
  "name": "Sarah Johnson",
  "age": 35,
  "income": 120000,
  "net_worth": 250000,
  "investment_capital": 100000,
  "investment_experience": "intermediate"
}
```

### Questionnaire (10 Questions)

**Q1: What is your age?**
- Under 30 → +20 points
- 30-45 → +15 points
- 45-60 → +10 points
- Over 60 → +5 points

**Q2: What is your investment time horizon?**
- 0-2 years → +5 points
- 2-5 years → +10 points
- 5-10 years → +15 points
- 10+ years → +20 points

**Q3: If your portfolio dropped 30% in a year, what would you do?**
- Sell everything → +0 points
- Sell some → +5 points
- Hold → +15 points
- Buy more → +20 points

**Q4: What is your primary investment goal?**
- Capital preservation → +5 points
- Income generation → +10 points
- Balanced growth → +15 points
- Maximum growth → +20 points

**Q5: How much investment experience do you have?**
- None → +5 points
- Beginner (< 2 years) → +10 points
- Intermediate (2-5 years) → +15 points
- Advanced (5+ years) → +20 points

**Q6: What is the maximum loss you can tolerate in a year?**
- 5% → +5 points
- 10% → +10 points
- 20% → +15 points
- 30%+ → +20 points

**Q7: How stable is your income?**
- Very unstable → +5 points
- Somewhat stable → +10 points
- Stable → +15 points
- Very stable → +20 points

**Q8: Do you need access to your investments in the next 2 years?**
- Yes, definitely → +0 points
- Maybe → +5 points
- Unlikely → +10 points
- No → +15 points

**Q9: How do you feel about market volatility?**
- Very uncomfortable → +5 points
- Uncomfortable → +10 points
- Neutral → +15 points
- Comfortable → +20 points

**Q10: What is your expected return?**
- 3-5% (conservative) → +5 points
- 5-7% (moderate) → +10 points
- 7-10% (growth) → +15 points
- 10%+ (aggressive) → +20 points

### Risk Score Calculation

```python
def calculate_risk_score(answers: Dict) -> int:
    """
    Calculate risk tolerance score (0-100)
    
    Scoring:
    0-30: Conservative
    31-60: Moderate
    61-80: Growth
    81-100: Aggressive
    """
    
    total_score = 0
    
    # Sum all question scores
    for question_id, answer in answers.items():
        total_score += answer['points']
    
    # Normalize to 0-100
    risk_score = min(total_score, 100)
    
    return risk_score
```

### Example Output

```json
{
  "risk_score": 65,
  "risk_category": "growth",
  "risk_description": "You have a growth-oriented risk profile with moderate tolerance for volatility. You're comfortable with market fluctuations and have a long-term investment horizon."
}
```

---

## Step 2: Goal Definition

### Input: Customer Goals

```python
@dataclass
class InvestmentGoal:
    goal_id: str
    goal_name: str
    target_amount: Decimal
    target_date: datetime
    priority: str  # "high", "medium", "low"
    flexibility: str  # "rigid", "flexible"
```

### Example Goals

```json
{
  "goals": [
    {
      "goal_id": "GOAL_001",
      "goal_name": "Car Purchase",
      "target_amount": 50000,
      "target_date": "2026-11-15",
      "years_to_goal": 2,
      "priority": "high",
      "flexibility": "rigid"
    },
    {
      "goal_id": "GOAL_002",
      "goal_name": "House Deposit",
      "target_amount": 150000,
      "target_date": "2029-11-15",
      "years_to_goal": 5,
      "priority": "high",
      "flexibility": "flexible"
    },
    {
      "goal_id": "GOAL_003",
      "goal_name": "Retirement",
      "target_amount": 1500000,
      "target_date": "2054-11-15",
      "years_to_goal": 30,
      "priority": "medium",
      "flexibility": "flexible"
    }
  ]
}
```

### Goal-to-Pod Mapping

```python
def map_goal_to_pod(goal: InvestmentGoal) -> str:
    """
    Map investment goal to appropriate pod
    
    Rules:
    - 0-2 years → POD 1 (Preservation)
    - 2-5 years → POD 2 (Income)
    - 5-10 years → POD 3 (Growth)
    - 10+ years → POD 3 (Growth) or POD 4 (Opportunistic)
    """
    
    years_to_goal = (goal.target_date - datetime.now()).days / 365
    
    if years_to_goal < 2:
        return "POD1"  # Preservation
    elif years_to_goal < 5:
        return "POD2"  # Income
    elif years_to_goal < 10:
        return "POD3"  # Growth
    else:
        # Long-term goals: split between Growth and Opportunistic
        if goal.priority == "high":
            return "POD3"  # Growth (safer)
        else:
            return "POD4"  # Opportunistic (higher risk/return)
```

### Example Output

```json
{
  "goal_mappings": [
    {
      "goal_id": "GOAL_001",
      "goal_name": "Car Purchase",
      "pod": "POD1",
      "pod_name": "Preservation"
    },
    {
      "goal_id": "GOAL_002",
      "goal_name": "House Deposit",
      "pod": "POD2",
      "pod_name": "Income"
    },
    {
      "goal_id": "GOAL_003",
      "goal_name": "Retirement",
      "pod": "POD3",
      "pod_name": "Growth"
    }
  ]
}
```

---

## Step 3: Pod Allocation

### Algorithm: Dynamic Pod Weight Calculation

```python
def calculate_pod_weights(
    risk_score: int,
    age: int,
    goals: List[InvestmentGoal],
    total_capital: Decimal
) -> Dict[str, float]:
    """
    Calculate optimal pod weights
    
    Factors:
    1. Risk tolerance (primary)
    2. Age (glide path)
    3. Goal distribution
    4. Capital allocation
    """
    
    # Base allocation by risk score
    if risk_score < 30:  # Conservative
        base_weights = {
            "POD1": 0.40,
            "POD2": 0.40,
            "POD3": 0.15,
            "POD4": 0.05
        }
    elif risk_score < 60:  # Moderate
        base_weights = {
            "POD1": 0.20,
            "POD2": 0.30,
            "POD3": 0.40,
            "POD4": 0.10
        }
    elif risk_score < 80:  # Growth
        base_weights = {
            "POD1": 0.15,
            "POD2": 0.25,
            "POD3": 0.50,
            "POD4": 0.10
        }
    else:  # Aggressive
        base_weights = {
            "POD1": 0.10,
            "POD2": 0.15,
            "POD3": 0.55,
            "POD4": 0.20
        }
    
    # Age-based glide path adjustment
    if age > 60:
        base_weights["POD1"] += 0.10
        base_weights["POD3"] -= 0.10
    elif age < 30:
        base_weights["POD1"] -= 0.05
        base_weights["POD3"] += 0.05
    
    # Goal-based adjustment
    goal_weights = {"POD1": 0, "POD2": 0, "POD3": 0, "POD4": 0}
    total_goal_amount = sum(g.target_amount for g in goals)
    
    for goal in goals:
        pod = map_goal_to_pod(goal)
        goal_weight = float(goal.target_amount / total_goal_amount)
        goal_weights[pod] += goal_weight * 0.2  # 20% influence
    
    # Combine base and goal weights
    final_weights = {}
    for pod in ["POD1", "POD2", "POD3", "POD4"]:
        final_weights[pod] = base_weights[pod] * 0.8 + goal_weights[pod]
    
    # Normalize to 100%
    total = sum(final_weights.values())
    final_weights = {k: v/total for k, v in final_weights.items()}
    
    return final_weights
```

### Example Output

```json
{
  "pod_allocation": {
    "POD1": {
      "weight": 0.15,
      "capital": 15000,
      "name": "Preservation",
      "goal": "Car Purchase"
    },
    "POD2": {
      "weight": 0.25,
      "capital": 25000,
      "name": "Income",
      "goal": "House Deposit"
    },
    "POD3": {
      "weight": 0.50,
      "capital": 50000,
      "name": "Growth",
      "goal": "Retirement"
    },
    "POD4": {
      "weight": 0.10,
      "capital": 10000,
      "name": "Opportunistic",
      "goal": "Alpha Generation"
    }
  },
  "total_capital": 100000
}
```

---

## Step 4: Pod-Level RL Optimization

### Process: 4 Agents Optimize Independently

```python
async def optimize_all_pods(
    pod_allocation: Dict,
    customer_profile: CustomerProfile
) -> Dict:
    """
    Run all 4 RL agents in parallel
    """
    
    # Initialize agents
    agents = {
        "POD1": AlphaAgent(),   # Q-Learning
        "POD2": BetaAgent(),    # Policy Gradient
        "POD3": GammaAgent(),   # DQN
        "POD4": DeltaAgent()    # A3C
    }
    
    # Optimize each pod
    pod_results = {}
    
    for pod_id, agent in agents.items():
        pod_capital = pod_allocation[pod_id]["capital"]
        pod_goals = [g for g in customer_profile.goals if map_goal_to_pod(g) == pod_id]
        
        result = await agent.optimize(
            capital=pod_capital,
            goals=pod_goals,
            risk_tolerance=customer_profile.risk_tolerance_score
        )
        
        pod_results[pod_id] = result
    
    return pod_results
```

### Example Output: POD 1 (Alpha Agent)

```json
{
  "pod_id": "POD1",
  "pod_name": "Preservation",
  "capital": 15000,
  "optimization_result": {
    "allocation": {
      "BILL": 0.60,
      "VAF": 0.30,
      "VAS": 0.10
    },
    "expected_return": 0.04,
    "expected_volatility": 0.08,
    "sharpe_ratio": 0.50,
    "max_drawdown": -0.05,
    "liquidity_score": 0.95,
    "agent_confidence": 0.88
  }
}
```

### Example Output: POD 2 (Beta Agent)

```json
{
  "pod_id": "POD2",
  "pod_name": "Income",
  "capital": 25000,
  "optimization_result": {
    "allocation": {
      "VAF": 0.30,
      "VHY": 0.25,
      "VAP": 0.15,
      "VAS": 0.20,
      "GOLD": 0.10
    },
    "expected_return": 0.06,
    "expected_yield": 0.045,
    "franking_credits": 0.015,
    "expected_volatility": 0.12,
    "sharpe_ratio": 0.50,
    "agent_confidence": 0.85
  }
}
```

### Example Output: POD 3 (Gamma Agent)

```json
{
  "pod_id": "POD3",
  "pod_name": "Growth",
  "capital": 50000,
  "optimization_result": {
    "allocation": {
      "VGS": 0.35,
      "VTS": 0.25,
      "VAS": 0.15,
      "NDQ": 0.10,
      "VAF": 0.10,
      "GOLD": 0.05
    },
    "expected_return": 0.10,
    "expected_volatility": 0.20,
    "sharpe_ratio": 0.50,
    "max_drawdown": -0.15,
    "diversification_score": 0.82,
    "agent_confidence": 0.90
  }
}
```

### Example Output: POD 4 (Delta Agent)

```json
{
  "pod_id": "POD4",
  "pod_name": "Opportunistic",
  "capital": 10000,
  "optimization_result": {
    "allocation": {
      "TECH": 0.25,
      "ROBO": 0.25,
      "SEMI": 0.20,
      "NDQ": 0.15,
      "ASIA": 0.15
    },
    "expected_return": 0.15,
    "expected_alpha": 0.03,
    "expected_volatility": 0.30,
    "sharpe_ratio": 0.50,
    "max_drawdown": -0.25,
    "agent_confidence": 0.75
  }
}
```

---

## Step 5: Consolidation & Deduplication

### Process: Master Portfolio Optimization

```python
def consolidate_pod_results(
    pod_results: Dict,
    pod_allocation: Dict
) -> Dict:
    """
    Consolidate all pod allocations into master portfolio
    
    Steps:
    1. Merge all ETF holdings
    2. Identify duplicates
    3. Calculate total allocation per ETF
    4. Prepare for master optimization
    """
    
    consolidated = {}
    
    for pod_id, result in pod_results.items():
        pod_capital = pod_allocation[pod_id]["capital"]
        
        for etf, weight in result["allocation"].items():
            if etf not in consolidated:
                consolidated[etf] = {
                    "total_value": 0,
                    "pods": [],
                    "weights_by_pod": {}
                }
            
            etf_value = pod_capital * weight
            consolidated[etf]["total_value"] += etf_value
            consolidated[etf]["pods"].append(pod_id)
            consolidated[etf]["weights_by_pod"][pod_id] = weight
    
    return consolidated
```

### Example Output: Consolidated Holdings

```json
{
  "consolidated_holdings": {
    "BILL": {
      "total_value": 9000,
      "pods": ["POD1"],
      "weights_by_pod": {"POD1": 0.60}
    },
    "VAF": {
      "total_value": 13500,
      "pods": ["POD1", "POD2", "POD3"],
      "weights_by_pod": {"POD1": 0.30, "POD2": 0.30, "POD3": 0.10},
      "duplicate": true
    },
    "VAS": {
      "total_value": 14000,
      "pods": ["POD1", "POD2", "POD3"],
      "weights_by_pod": {"POD1": 0.10, "POD2": 0.20, "POD3": 0.15},
      "duplicate": true
    },
    "VHY": {
      "total_value": 6250,
      "pods": ["POD2"],
      "weights_by_pod": {"POD2": 0.25}
    },
    "VAP": {
      "total_value": 3750,
      "pods": ["POD2"],
      "weights_by_pod": {"POD2": 0.15}
    },
    "GOLD": {
      "total_value": 5000,
      "pods": ["POD2", "POD3"],
      "weights_by_pod": {"POD2": 0.10, "POD3": 0.05},
      "duplicate": true
    },
    "VGS": {
      "total_value": 17500,
      "pods": ["POD3"],
      "weights_by_pod": {"POD3": 0.35}
    },
    "VTS": {
      "total_value": 12500,
      "pods": ["POD3"],
      "weights_by_pod": {"POD3": 0.25}
    },
    "NDQ": {
      "total_value": 6500,
      "pods": ["POD3", "POD4"],
      "weights_by_pod": {"POD3": 0.10, "POD4": 0.15},
      "duplicate": true
    },
    "TECH": {
      "total_value": 2500,
      "pods": ["POD4"],
      "weights_by_pod": {"POD4": 0.25}
    },
    "ROBO": {
      "total_value": 2500,
      "pods": ["POD4"],
      "weights_by_pod": {"POD4": 0.25}
    },
    "SEMI": {
      "total_value": 2000,
      "pods": ["POD4"],
      "weights_by_pod": {"POD4": 0.20}
    },
    "ASIA": {
      "total_value": 1500,
      "pods": ["POD4"],
      "weights_by_pod": {"POD4": 0.15}
    }
  },
  "total_unique_etfs": 13,
  "duplicated_etfs": ["VAF", "VAS", "GOLD", "NDQ"]
}
```

### Master Optimization

```python
def optimize_master_portfolio(
    consolidated: Dict,
    pod_results: Dict,
    pod_allocation: Dict
) -> Dict:
    """
    Optimize master portfolio with constraints
    
    Objectives:
    1. Preserve pod objectives (60%)
    2. Minimize duplication penalty (20%)
    3. Minimize transaction costs (10%)
    4. Maximize tax efficiency (10%)
    
    Constraints:
    - Each pod meets its objectives
    - Max 12 ETFs
    - Max 30% per ETF
    - Min 2% per ETF (if included)
    """
    
    # ... (optimization code from MASTER_PORTFOLIO_OPTIMIZATION.md)
    
    return master_portfolio
```

### Example Output: Optimized Master Portfolio

```json
{
  "master_portfolio": {
    "BILL": {
      "weight": 0.09,
      "value": 9000,
      "pods": ["POD1"]
    },
    "VAF": {
      "weight": 0.135,
      "value": 13500,
      "pods": ["POD1", "POD2", "POD3"],
      "consolidated": true
    },
    "VAS": {
      "weight": 0.14,
      "value": 14000,
      "pods": ["POD1", "POD2", "POD3"],
      "consolidated": true
    },
    "VHY": {
      "weight": 0.0625,
      "value": 6250,
      "pods": ["POD2"]
    },
    "VAP": {
      "weight": 0.0375,
      "value": 3750,
      "pods": ["POD2"]
    },
    "GOLD": {
      "weight": 0.05,
      "value": 5000,
      "pods": ["POD2", "POD3"],
      "consolidated": true
    },
    "VGS": {
      "weight": 0.175,
      "value": 17500,
      "pods": ["POD3"]
    },
    "VTS": {
      "weight": 0.125,
      "value": 12500,
      "pods": ["POD3"]
    },
    "NDQ": {
      "weight": 0.065,
      "value": 6500,
      "pods": ["POD3", "POD4"],
      "consolidated": true
    },
    "TECH": {
      "weight": 0.025,
      "value": 2500,
      "pods": ["POD4"]
    },
    "ROBO": {
      "weight": 0.025,
      "value": 2500,
      "pods": ["POD4"]
    },
    "SEMI": {
      "weight": 0.02,
      "value": 2000,
      "pods": ["POD4"]
    },
    "ASIA": {
      "weight": 0.015,
      "value": 1500,
      "pods": ["POD4"]
    }
  },
  "total_etfs": 13,
  "total_value": 100000,
  "optimization_metrics": {
    "pod_objectives_preserved": true,
    "duplication_eliminated": 4,
    "transaction_cost": 130,
    "tax_efficiency_score": 0.85
  }
}
```

---

## Step 6: Tax Optimization

### Australian Tax Optimization

```python
def optimize_tax(master_portfolio: Dict, customer_profile: CustomerProfile) -> Dict:
    """
    Optimize portfolio for Australian tax
    
    Strategies:
    1. Maximize franking credits (Australian dividends)
    2. Minimize CGT (hold >12 months for 50% discount)
    3. Tax-loss harvesting
    4. Optimize dividend timing
    """
    
    tax_analysis = {
        "franking_credits": 0,
        "cgt_liability": 0,
        "income_tax": 0,
        "net_after_tax_return": 0
    }
    
    # Calculate franking credits
    for etf, holding in master_portfolio.items():
        if etf in ["VAS", "VHY", "VAP"]:  # Australian equity ETFs
            dividend_yield = get_dividend_yield(etf)
            franking_rate = get_franking_rate(etf)
            
            gross_dividend = holding["value"] * dividend_yield
            franking_credit = gross_dividend * franking_rate * 0.30 / 0.70
            
            tax_analysis["franking_credits"] += franking_credit
    
    # CGT optimization
    for etf, holding in master_portfolio.items():
        purchase_price = get_purchase_price(etf)
        current_price = get_current_price(etf)
        
        if current_price > purchase_price:
            # Unrealized gain
            gain = (current_price - purchase_price) * holding["value"] / current_price
            
            # Hold >12 months for 50% CGT discount
            holding_period = get_holding_period(etf)
            if holding_period > 365:
                taxable_gain = gain * 0.5
            else:
                taxable_gain = gain
            
            tax_analysis["cgt_liability"] += taxable_gain * customer_profile.marginal_tax_rate
    
    return tax_analysis
```

### Example Output: Tax Analysis

```json
{
  "tax_analysis": {
    "gross_income": 4500,
    "franking_credits": 450,
    "income_tax": 1200,
    "after_tax_income": 3750,
    "cgt_liability": 0,
    "net_after_tax_return": 0.082,
    "tax_efficiency_score": 0.85,
    "recommendations": [
      "Hold VAS for 12+ months to qualify for 50% CGT discount",
      "Maximize franking credits by overweighting VHY in POD 2",
      "Consider tax-loss harvesting in POD 4 (TECH, ROBO)"
    ]
  }
}
```

---

## Step 7: Trade Execution

### Integration with OpenMarkets

```python
async def execute_trades(
    master_portfolio: Dict,
    customer_profile: CustomerProfile
) -> Dict:
    """
    Execute trades via OpenMarkets API
    
    Steps:
    1. Generate trade orders
    2. Submit to OpenMarkets
    3. Monitor execution
    4. Confirm fills
    5. Publish events
    """
    
    trades = []
    
    for etf, holding in master_portfolio.items():
        # Calculate shares to buy
        current_price = await get_current_price(etf)
        shares = int(holding["value"] / current_price)
        
        # Create order
        order = {
            "etf": etf,
            "action": "BUY",
            "shares": shares,
            "order_type": "MARKET",
            "estimated_cost": shares * current_price
        }
        
        trades.append(order)
    
    # Submit to OpenMarkets
    execution_results = await openmarkets_api.submit_orders(trades)
    
    # Publish event
    event = TradesExecuted(
        customer_id=customer_profile.customer_id,
        trades=execution_results,
        total_cost=sum(t["executed_cost"] for t in execution_results)
    )
    await event_store.publish(event)
    
    return execution_results
```

### Example Output: Trade Execution

```json
{
  "execution_results": [
    {
      "etf": "BILL",
      "action": "BUY",
      "shares": 1800,
      "price": 5.00,
      "total_cost": 9000,
      "status": "FILLED",
      "execution_time": "2025-11-15T14:30:00Z"
    },
    {
      "etf": "VAF",
      "action": "BUY",
      "shares": 291,
      "price": 46.40,
      "total_cost": 13502,
      "status": "FILLED",
      "execution_time": "2025-11-15T14:30:05Z"
    },
    // ... (11 more trades)
  ],
  "total_trades": 13,
  "total_cost": 100130,
  "transaction_costs": 130,
  "execution_summary": {
    "successful": 13,
    "failed": 0,
    "partial": 0
  }
}
```

---

## Step 8: Continuous Monitoring & Rebalancing

### Event-Driven Monitoring

```python
class PortfolioMonitor:
    """
    Continuous portfolio monitoring
    
    Monitors:
    - Daily price updates
    - Volatility spikes
    - Drift from target allocation
    - Pod objective violations
    - Market regime changes
    """
    
    async def monitor(self):
        """
        Run continuous monitoring loop
        """
        
        while True:
            # Check all customer portfolios
            for customer in await get_all_customers():
                portfolio = await get_customer_portfolio(customer.customer_id)
                
                # Check for rebalancing triggers
                triggers = await self.check_rebalancing_triggers(portfolio)
                
                if triggers:
                    # Trigger rebalancing
                    await self.trigger_rebalancing(customer, portfolio, triggers)
            
            # Sleep for 1 hour
            await asyncio.sleep(3600)
    
    async def check_rebalancing_triggers(self, portfolio: Dict) -> List[str]:
        """
        Check if rebalancing is needed
        
        Triggers:
        1. Drift > 5% from target allocation
        2. Pod volatility exceeds limit
        3. Market regime change
        4. Goal approaching (< 6 months)
        5. Tax-loss harvesting opportunity
        """
        
        triggers = []
        
        # 1. Drift check
        current_allocation = await get_current_allocation(portfolio)
        target_allocation = portfolio["target_allocation"]
        
        for etf in target_allocation:
            drift = abs(current_allocation[etf] - target_allocation[etf])
            if drift > 0.05:
                triggers.append(f"DRIFT: {etf} drifted {drift:.1%}")
        
        # 2. Volatility check
        for pod_id in ["POD1", "POD2", "POD3", "POD4"]:
            current_vol = await calculate_pod_volatility(portfolio, pod_id)
            target_vol = portfolio["pod_objectives"][pod_id]["max_volatility"]
            
            if current_vol > target_vol:
                triggers.append(f"VOLATILITY: {pod_id} volatility {current_vol:.1%} exceeds {target_vol:.1%}")
        
        # 3. Market regime change
        current_regime = await detect_market_regime()
        if current_regime != portfolio["market_regime"]:
            triggers.append(f"REGIME_CHANGE: {portfolio['market_regime']} → {current_regime}")
        
        # 4. Goal approaching
        for goal in portfolio["goals"]:
            days_to_goal = (goal["target_date"] - datetime.now()).days
            if days_to_goal < 180:  # 6 months
                triggers.append(f"GOAL_APPROACHING: {goal['name']} in {days_to_goal} days")
        
        # 5. Tax-loss harvesting
        tax_opportunities = await check_tax_loss_harvesting(portfolio)
        if tax_opportunities:
            triggers.append(f"TAX_OPPORTUNITY: {len(tax_opportunities)} positions")
        
        return triggers
```

### Rebalancing Process

```python
async def trigger_rebalancing(
    customer: CustomerProfile,
    portfolio: Dict,
    triggers: List[str]
) -> Dict:
    """
    Execute rebalancing
    
    Steps:
    1. Re-run optimization (Stages 4-6)
    2. Calculate trades needed
    3. Execute trades
    4. Update portfolio
    5. Publish events
    """
    
    # Re-run optimization
    pod_results = await optimize_all_pods(portfolio["pod_allocation"], customer)
    master_portfolio = optimize_master_portfolio(pod_results, portfolio["pod_allocation"])
    
    # Calculate trades
    trades = calculate_rebalancing_trades(portfolio, master_portfolio)
    
    # Execute trades
    execution_results = await execute_trades(trades, customer)
    
    # Update portfolio
    updated_portfolio = await update_portfolio(customer.customer_id, master_portfolio)
    
    # Publish event
    event = PortfolioRebalanced(
        customer_id=customer.customer_id,
        triggers=triggers,
        trades=execution_results,
        new_allocation=master_portfolio
    )
    await event_store.publish(event)
    
    return updated_portfolio
```

---

## Summary: Complete Flow

### Timeline

| Step | Duration | Responsible |
|------|----------|-------------|
| 1. Risk Questionnaire | 5 minutes | Customer |
| 2. Goal Definition | 5 minutes | Customer |
| 3. Pod Allocation | 1 second | System |
| 4. Pod Optimization | 5 seconds | RL Agents |
| 5. Master Optimization | 2 seconds | System |
| 6. Tax Optimization | 1 second | System |
| 7. Trade Execution | 30 seconds | OpenMarkets |
| 8. Monitoring | Continuous | System |

**Total onboarding time:** ~10 minutes (customer input) + ~40 seconds (system processing)

### Event Sourcing

All steps publish events:

```
CustomerOnboarded
RiskQuestionnaireCompleted
GoalsDefined
PodAllocationCalculated
PodOptimized (×4)
MasterPortfolioOptimized
TaxOptimizationCompleted
TradesExecuted
PortfolioCreated
PortfolioMonitoringStarted
PortfolioRebalanced (future)
```

### Data Mesh

Data products consumed:

- ETF Data Product (137 ASX ETFs)
- Market Data Product (prices, volatility)
- Tax Data Product (franking, CGT)
- Customer Data Product (profiles, goals)

---

**Status:** Complete optimization flow documented  
**Next:** Create presentation slides for client pitch
