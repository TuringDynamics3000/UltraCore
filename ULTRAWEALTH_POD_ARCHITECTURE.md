# UltraWealth Pod System Architecture
## Goal-Based Investing with Agentic AI, RL/ML, Data Mesh & Event Sourcing

**Version:** 2.0  
**Date:** November 15, 2025  
**Status:** Design Specification  

---

## Executive Summary

UltraWealth uses a **4-pod architecture** wrapped in a **Master Portfolio** to deliver goal-based investing powered by:

- **UltraOptimiser** (not plain MPT) - Advanced RL/ML optimization
- **Data Mesh** - Decentralized data architecture
- **Event Sourcing** - Complete audit trail via Kafka
- **Agentic AI** - Autonomous pod management agents

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    MASTER PORTFOLIO WRAPPER                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Customer Risk Profile + Goals → Master Allocation Engine  │  │
│  │  • Event-Sourced State                                     │  │
│  │  • Auto-Rebalancing (Event-Driven)                         │  │
│  │  • Tax Optimization Layer                                  │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────┬──────────────┬──────────────┬──────────────┬─────────┘
            │              │              │              │
    ┌───────▼──────┐ ┌────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
    │   POD 1:     │ │  POD 2:   │ │  POD 3:   │ │  POD 4:   │
    │ PRESERVATION │ │  INCOME   │ │  GROWTH   │ │ OPPORTUN. │
    │              │ │           │ │           │ │           │
    │ Agent: Alpha │ │Agent:Beta │ │Agent:Gamma│ │Agent:Delta│
    │ RL Model: A  │ │RL Model:B │ │RL Model:C │ │RL Model:D │
    └──────────────┘ └───────────┘ └───────────┘ └───────────┘
            │              │              │              │
    ┌───────▼──────────────▼──────────────▼──────────────▼───────┐
    │              DATA MESH (ETF Data Product)                   │
    │  • 137 ASX ETFs                                             │
    │  • Real-time pricing                                        │
    │  • Historical returns                                       │
    │  • Risk metrics                                             │
    │  • Event-sourced updates                                    │
    └─────────────────────────────────────────────────────────────┘
```

---

## 1. Four-Pod Architecture

### Pod 1: PRESERVATION POD
**Goal:** Capital protection, emergency fund, short-term goals (<2 years)

**Characteristics:**
- **Risk Level:** Very Conservative (5-10% volatility target)
- **Time Horizon:** 0-2 years
- **Asset Mix:** 80% cash/bonds, 20% defensive equities
- **Rebalancing:** Monthly
- **Downside Protection:** Aggressive (circuit breaker at -3%)

**ETF Universe:**
- BILL (iShares Core Cash) - 60%
- VAF (Vanguard Australian Fixed Interest) - 20%
- VGB (Vanguard Australian Government Bond) - 10%
- VAS (Vanguard Australian Shares) - 10%

**Agentic AI Agent:** **Alpha Agent**
- **Role:** Capital preservation, liquidity management
- **RL Model:** Conservative Q-learning (maximize stability)
- **Actions:** Rebalance to cash, trigger circuit breakers
- **Reward Function:** Minimize drawdown, maintain liquidity

---

### Pod 2: INCOME POD
**Goal:** Generate regular income, retirement income, dividend yield

**Characteristics:**
- **Risk Level:** Conservative-Moderate (10-15% volatility target)
- **Time Horizon:** 2-5 years
- **Asset Mix:** 40% bonds, 40% dividend equities, 20% growth
- **Rebalancing:** Quarterly
- **Downside Protection:** Moderate (circuit breaker at -5%)

**ETF Universe:**
- VAF (Vanguard Australian Fixed Interest) - 30%
- VHY (Vanguard Australian High Dividend) - 25%
- VAP (Vanguard Australian Property) - 15%
- EINC (BetaShares Enhanced Income) - 15%
- VAS (Vanguard Australian Shares) - 10%
- GOLD (Gold ETF) - 5% (diversifier)

**Agentic AI Agent:** **Beta Agent**
- **Role:** Income optimization, yield maximization
- **RL Model:** Policy gradient (maximize income + franking credits)
- **Actions:** Dividend capture, franking credit optimization
- **Reward Function:** Maximize after-tax income + capital stability

---

### Pod 3: GROWTH POD
**Goal:** Long-term wealth accumulation, retirement savings, house deposit

**Characteristics:**
- **Risk Level:** Moderate-Aggressive (15-25% volatility target)
- **Time Horizon:** 5-10 years
- **Asset Mix:** 80% equities, 15% bonds, 5% alternatives
- **Rebalancing:** Semi-annually
- **Downside Protection:** Light (circuit breaker at -15%)

**ETF Universe:**
- VGS (Vanguard International Shares) - 35%
- VTS (Vanguard US Total Market) - 25%
- VAS (Vanguard Australian Shares) - 15%
- NDQ (BetaShares NASDAQ 100) - 10%
- VAF (Vanguard Australian Fixed Interest) - 10%
- GOLD (Gold ETF) - 5%

**Agentic AI Agent:** **Gamma Agent**
- **Role:** Growth maximization, risk-adjusted returns
- **RL Model:** Deep Q-Network (DQN) - maximize Sharpe ratio
- **Actions:** Dynamic rebalancing, momentum capture
- **Reward Function:** Maximize returns / volatility (Sharpe)

---

### Pod 4: OPPORTUNISTIC POD
**Goal:** Tactical allocation, thematic investing, alpha generation

**Characteristics:**
- **Risk Level:** Aggressive (25-35% volatility target)
- **Time Horizon:** 10+ years or flexible
- **Asset Mix:** 100% equities (sector rotation)
- **Rebalancing:** Monthly (tactical)
- **Downside Protection:** Minimal (circuit breaker at -20%)

**ETF Universe:**
- TECH (BetaShares Global Cybersecurity) - 20%
- ROBO (BetaShares Global Robotics) - 20%
- SEMI (BetaShares Global Semiconductors) - 15%
- NDQ (BetaShares NASDAQ 100) - 15%
- ASIA (BetaShares Asia Technology) - 10%
- HACK (BetaShares Global Cybersecurity) - 10%
- GOLD (Gold ETF) - 10% (hedge)

**Agentic AI Agent:** **Delta Agent**
- **Role:** Alpha generation, tactical allocation
- **RL Model:** Actor-Critic (A3C) - explore/exploit strategies
- **Actions:** Sector rotation, momentum trading, mean reversion
- **Reward Function:** Maximize absolute returns (alpha vs benchmark)

---

## 2. Master Portfolio Wrapper

### Components

#### 2.1 Risk Questionnaire Integration

**Input Parameters:**
```python
{
    "age": 35,
    "income": 120000,
    "net_worth": 250000,
    "investment_experience": "intermediate",
    "risk_tolerance_score": 65,  # 0-100
    "time_horizon_years": 20,
    "goals": [
        {
            "goal_type": "car_purchase",
            "target_amount": 50000,
            "target_date": "2027-06-01",
            "priority": "high"
        },
        {
            "goal_type": "house_deposit",
            "target_amount": 150000,
            "target_date": "2030-01-01",
            "priority": "high"
        },
        {
            "goal_type": "retirement",
            "target_amount": 1500000,
            "target_date": "2055-01-01",
            "priority": "medium"
        }
    ]
}
```

#### 2.2 Pod Allocation Algorithm

**Step 1: Map Goals to Pods**

```python
def map_goals_to_pods(goals, risk_profile):
    """
    Map customer goals to appropriate pods based on:
    - Time horizon
    - Risk tolerance
    - Goal priority
    - Required return
    """
    
    pod_mapping = {
        "PRESERVATION": [],  # <2 years, low risk
        "INCOME": [],        # 2-5 years, moderate risk
        "GROWTH": [],        # 5-10 years, higher risk
        "OPPORTUNISTIC": []  # 10+ years, aggressive risk
    }
    
    for goal in goals:
        years_to_goal = (goal.target_date - today).days / 365
        
        if years_to_goal < 2:
            pod_mapping["PRESERVATION"].append(goal)
        elif years_to_goal < 5:
            pod_mapping["INCOME"].append(goal)
        elif years_to_goal < 10:
            pod_mapping["GROWTH"].append(goal)
        else:
            # Split between GROWTH and OPPORTUNISTIC based on risk tolerance
            if risk_profile.score > 70:
                pod_mapping["OPPORTUNISTIC"].append(goal)
            else:
                pod_mapping["GROWTH"].append(goal)
    
    return pod_mapping
```

**Step 2: Calculate Pod Weights**

```python
def calculate_pod_weights(pod_mapping, total_capital):
    """
    Calculate capital allocation to each pod based on:
    - Goal amounts
    - Goal priorities
    - Time to goal
    - Required returns
    """
    
    pod_weights = {}
    
    for pod_name, goals in pod_mapping.items():
        if not goals:
            pod_weights[pod_name] = 0
            continue
        
        # Sum required capital for goals in this pod
        required_capital = sum(goal.target_amount for goal in goals)
        
        # Adjust for time value (discount back to present)
        present_value = sum(
            goal.target_amount / (1 + expected_return) ** years_to_goal
            for goal in goals
        )
        
        # Weight by priority
        priority_weight = sum(
            goal.priority_score * goal.target_amount
            for goal in goals
        )
        
        pod_weights[pod_name] = present_value * priority_weight
    
    # Normalize to 100%
    total = sum(pod_weights.values())
    return {k: v/total for k, v in pod_weights.items()}
```

**Example Output:**

```python
{
    "PRESERVATION": 0.15,  # 15% - Car purchase (2 years)
    "INCOME": 0.25,        # 25% - House deposit (5 years)
    "GROWTH": 0.50,        # 50% - Retirement (30 years)
    "OPPORTUNISTIC": 0.10  # 10% - Tactical/Alpha
}
```

#### 2.3 Event-Driven Rebalancing

**Event Types:**

1. **Scheduled Rebalancing** (Quarterly)
2. **Drift Rebalancing** (When allocation drifts >5%)
3. **Goal Milestone** (Approaching target date)
4. **Market Event** (Volatility spike, circuit breaker)
5. **Contribution Event** (New money added)
6. **Withdrawal Event** (Goal achieved, funds needed)

**Event Flow:**

```
Customer Contribution
        │
        ▼
┌───────────────────┐
│ ContributionMade  │ Event published to Kafka
│ Event             │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Master Portfolio  │ Listens to events
│ Rebalancer        │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Calculate Drift   │ Check if rebalancing needed
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Trigger Pod       │ Each pod agent optimizes
│ Agents            │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Execute Trades    │ Via OpenMarkets integration
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Publish           │ PodRebalanced events
│ Rebalancing       │
│ Events            │
└───────────────────┘
```

---

## 3. Agentic AI Pod Managers

### Agent Architecture

Each pod has an autonomous AI agent that:

1. **Monitors** pod state via event sourcing
2. **Optimizes** portfolio using RL/ML models
3. **Executes** rebalancing decisions
4. **Learns** from outcomes (reinforcement learning)
5. **Reports** to master portfolio

### Agent Components

```python
class PodAgent:
    """
    Autonomous agent managing a single investment pod
    """
    
    def __init__(self, pod_id, pod_type, rl_model):
        self.pod_id = pod_id
        self.pod_type = pod_type  # PRESERVATION, INCOME, GROWTH, OPPORTUNISTIC
        self.rl_model = rl_model  # Trained RL model
        self.state = PodState()
        self.event_store = EventStore()
    
    async def observe(self):
        """Observe current pod state from event sourcing"""
        events = await self.event_store.get_events(self.pod_id)
        self.state = self.rebuild_state_from_events(events)
        return self.state
    
    async def decide(self, state):
        """Use RL model to decide optimal action"""
        # State: current allocation, market conditions, goal progress
        # Action: rebalance weights, trigger circuit breaker, etc.
        action = self.rl_model.predict(state)
        return action
    
    async def act(self, action):
        """Execute the decided action"""
        if action.type == "REBALANCE":
            await self.execute_rebalance(action.target_weights)
        elif action.type == "CIRCUIT_BREAKER":
            await self.trigger_circuit_breaker()
        
        # Publish event
        event = PodActionExecuted(pod_id=self.pod_id, action=action)
        await self.event_store.publish(event)
    
    async def learn(self, reward):
        """Update RL model based on outcome"""
        self.rl_model.update(state, action, reward, next_state)
```

### RL Models by Pod

| Pod | RL Algorithm | State Space | Action Space | Reward Function |
|-----|--------------|-------------|--------------|-----------------|
| **PRESERVATION** | Q-Learning | Allocation, volatility, drawdown | Rebalance to cash/bonds | -drawdown - volatility |
| **INCOME** | Policy Gradient | Allocation, yield, franking | Dividend optimization | income + franking - volatility |
| **GROWTH** | Deep Q-Network (DQN) | Allocation, returns, Sharpe | Dynamic rebalancing | Sharpe ratio |
| **OPPORTUNISTIC** | Actor-Critic (A3C) | Allocation, momentum, sectors | Sector rotation | Absolute returns - benchmark |

---

## 4. Data Mesh Integration

### ETF Data Product

**Already Implemented:**
- 137 ASX ETFs
- Event-sourced updates
- Real-time pricing
- Historical returns (2007-2025)
- Risk metrics (Sharpe, Sortino, Max DD)
- Correlation matrices

**Data Mesh Principles:**

1. **Domain-Oriented** - ETF data owned by market data domain
2. **Self-Serve** - Pods consume via ETFDataProvider
3. **Product Thinking** - Data as a product with SLA
4. **Federated Governance** - Decentralized data ownership

### Event Sourcing

**Event Types:**

```python
# Pod Lifecycle Events
- PodCreated
- PodOptimized
- PodActivated
- PodRebalanced
- PodCompleted
- PodClosed

# Market Data Events
- ETFPriceUpdated
- ETFDataCollected
- MarketVolatilityAlert

# Customer Events
- ContributionMade
- WithdrawalExecuted
- GoalParametersUpdated
- RiskToleranceChanged

# Agent Events
- AgentDecisionMade
- CircuitBreakerTriggered
- GlidePathTransitionExecuted
```

**Event Store:** Kafka topics
- `pod-lifecycle-events`
- `market-data-events`
- `customer-events`
- `agent-decisions`

---

## 5. UltraOptimiser Integration

### Not Plain MPT!

**UltraOptimiser uses:**

1. **Reinforcement Learning** - Agents learn optimal strategies
2. **Deep Learning** - Neural networks for return prediction
3. **Multi-Objective Optimization** - Balance return, risk, tax, fees
4. **Adaptive Algorithms** - Adjust to market regimes
5. **Ensemble Methods** - Combine multiple models

### Optimization Flow

```
Customer Risk Profile + Goals
        │
        ▼
┌────────────────────────┐
│ Master Allocation      │ Determine pod weights
│ Engine                 │
└────────────────────────┘
        │
        ▼
┌────────────────────────┐
│ Pod Agents (4)         │ Each agent optimizes its pod
│ - Alpha (Preservation) │
│ - Beta (Income)        │
│ - Gamma (Growth)       │
│ - Delta (Opportunistic)│
└────────────────────────┘
        │
        ▼
┌────────────────────────┐
│ RL Models              │ Trained on historical data
│ - Q-Learning           │
│ - Policy Gradient      │
│ - DQN                  │
│ - A3C                  │
└────────────────────────┘
        │
        ▼
┌────────────────────────┐
│ ETF Data Product       │ 137 ASX ETFs + metrics
└────────────────────────┘
        │
        ▼
┌────────────────────────┐
│ Optimal Portfolio      │ 4 pods, each with 4-8 ETFs
│ - Preservation: 15%    │
│ - Income: 25%          │
│ - Growth: 50%          │
│ - Opportunistic: 10%   │
└────────────────────────┘
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ ETF Data Product (DONE)
- ✅ Event Sourcing System (DONE)
- ✅ ETFDataProvider (DONE)
- ⏳ Master Portfolio Wrapper
- ⏳ Risk Questionnaire Integration

### Phase 2: Pod Agents (Week 3-4)
- ⏳ Alpha Agent (Preservation)
- ⏳ Beta Agent (Income)
- ⏳ Gamma Agent (Growth)
- ⏳ Delta Agent (Opportunistic)

### Phase 3: RL Models (Week 5-6)
- ⏳ Train Q-Learning (Preservation)
- ⏳ Train Policy Gradient (Income)
- ⏳ Train DQN (Growth)
- ⏳ Train A3C (Opportunistic)

### Phase 4: Integration (Week 7-8)
- ⏳ Event-driven rebalancing
- ⏳ Tax optimization layer
- ⏳ OpenMarkets execution
- ⏳ Anya AI integration

### Phase 5: Testing & Launch (Week 9-10)
- ⏳ Backtesting (5+ years)
- ⏳ Paper trading
- ⏳ Beta testing
- ⏳ Production launch

---

## 7. Key Differentiators

### vs Traditional Robo-Advisors

| Feature | Traditional | UltraWealth |
|---------|-------------|-------------|
| **Optimization** | Static MPT | RL/ML Agents |
| **Rebalancing** | Scheduled | Event-Driven |
| **Goals** | Single portfolio | 4 specialized pods |
| **Learning** | None | Continuous RL |
| **Data** | Centralized | Data Mesh |
| **Audit** | Limited | Full event sourcing |
| **Tax** | Basic | Advanced optimization |

### Competitive Advantages

1. **Agentic AI** - Autonomous agents managing each pod
2. **RL/ML** - Continuous learning and adaptation
3. **Event Sourcing** - Complete audit trail + replay
4. **Data Mesh** - Scalable, decentralized data
5. **Goal-Based** - 4 specialized pods vs single portfolio
6. **Tax Optimization** - Franking credits, CGT harvesting

---

## 8. Example Customer Journey

### Customer: Sarah, 35 years old

**Risk Questionnaire Results:**
- Risk Score: 65/100 (Moderate-Growth)
- Time Horizon: 20 years
- Goals:
  - Car ($50K, 2 years)
  - House ($150K, 5 years)
  - Retirement ($1.5M, 30 years)

**Master Portfolio Allocation:**
```
Total Capital: $100,000

POD 1 (PRESERVATION): $15,000 (15%)
  Goal: Car purchase
  ETFs: BILL 60%, VAF 30%, VAS 10%
  Agent: Alpha (conservative)

POD 2 (INCOME): $25,000 (25%)
  Goal: House deposit
  ETFs: VAF 30%, VHY 25%, VAP 15%, VAS 20%, GOLD 10%
  Agent: Beta (income optimization)

POD 3 (GROWTH): $50,000 (50%)
  Goal: Retirement
  ETFs: VGS 35%, VTS 25%, VAS 15%, NDQ 10%, VAF 10%, GOLD 5%
  Agent: Gamma (Sharpe maximization)

POD 4 (OPPORTUNISTIC): $10,000 (10%)
  Goal: Alpha generation
  ETFs: TECH 25%, ROBO 25%, SEMI 20%, NDQ 15%, ASIA 15%
  Agent: Delta (tactical allocation)
```

**Event Timeline:**

1. **Day 1:** PodCreated events (x4)
2. **Day 1:** PodOptimized events (x4) - Agents optimize
3. **Day 1:** PodActivated events (x4) - Trades executed
4. **Month 1:** ContributionMade ($1000) - Auto-allocated
5. **Month 3:** PodRebalanced (Growth) - Drift >5%
6. **Year 2:** GlidePathTransition (Preservation) - Car goal approaching
7. **Year 2:** GoalAchieved (Car) - Funds withdrawn
8. **Year 5:** GoalAchieved (House) - Funds withdrawn
9. **Year 30:** GoalAchieved (Retirement) - Success!

---

## 9. Next Steps

### Immediate Actions

1. **Review this architecture** with team
2. **Approve pod structure** (4 pods vs alternatives)
3. **Prioritize implementation** (which phase first?)
4. **Allocate resources** (developers, ML engineers)
5. **Set milestones** (sprint planning)

### Questions to Resolve

1. Should we add a 5th pod? (e.g., ESG/Ethical pod?)
2. What's the minimum investment per pod? ($5K? $10K?)
3. How do we handle pod closure? (Goal achieved, reallocate?)
4. Tax optimization priority? (High, Medium, Low?)
5. Anya AI integration scope? (Full automation? Human-in-loop?)

---

**Status:** Awaiting approval to proceed with implementation  
**Next Review:** TBD  
**Owner:** UltraCore Team
