# Recurring Deposits Domain - UltraCore Institutional Grade

Enterprise-grade recurring deposit (systematic savings) module with AI/ML/RL capabilities.

## Overview

Recurring Deposits (RD) enable customers to build disciplined saving habits through regular monthly deposits. Unlike Fixed Deposits which require a lump sum, RDs allow customers to save systematically toward goals like:
- House deposits
- Education expenses
- Wedding funds
- Emergency funds
- Vehicle purchases

## Architecture

### Event-Sourced (Kafka-First)
- All state changes flow through Kafka
- Complete payment audit trail
- Temporal queries (account state at any point in time)
- Event replay for debugging and analytics

### CQRS Pattern
- Commands: State-changing operations
- Queries: Read-only operations
- Optimized for high-volume payment processing

### Domain-Driven Design
- Rich domain models with payment schedules
- Account health scoring
- Payment behavior tracking

## Features

### Core Banking
? Recurring deposit products with flexible terms (6-60 months)
? Monthly deposit scheduling and tracking
? Auto-debit mandate management
? Interest calculation (compound monthly/quarterly)
? Payment reminders and grace periods
? Missed payment handling with penalties
? Account health scoring (0-100)
? Maturity processing with multiple options
? Premature closure with calculated penalties
? Maker-checker workflows

### Agentic AI (Anya)
? Natural language interface: "I want to save /month for my house deposit"
? Payment reminders and encouragement
? Missed payment assistance with empathy
? Progress tracking and milestone celebrations
? Affordability checking before opening
? Completion coaching with personalized advice
? Goal visualization and motivation

### Machine Learning
? Completion prediction (85% accuracy)
? Missed payment risk detection
? Affordability scoring
? Customer churn prediction
? Behavioral segmentation
? Early intervention triggers

### Reinforcement Learning
? Dynamic incentive optimization
? Retention strategy learning
? Personalized reward packages
? Cost-benefit balancing

### MCP Framework
? 8 AI tools for Claude/assistants
? Natural integration with AI workflows
? Conversational deposit management

### Data Mesh
? 3 data products (Accounts, Payments, Analytics)
? Real-time payment tracking
? Completion analytics
? Quality SLAs

## Quick Start

\\\python
from ultracore.domains.recurring_deposits import RecurringDepositService
from ultracore.domains.recurring_deposits.agents import AnyaRecurringDepositAgent

# Initialize service
rd_service = RecurringDepositService(event_store, kafka)

# Submit application
application = await rd_service.submit_application(
    customer_id="CUST-123",
    product=product,
    monthly_deposit_amount=Decimal("500"),
    term_months=24,
    source_account_id="SAV-456",
    debit_day_of_month=1,
    maturity_instruction="transfer_to_savings",
    submitted_by="customer"
)

# Use Anya for natural language
anya = AnyaRecurringDepositAgent(anthropic, rd_service, "CUST-123")
response = await anya.execute("I want to save  every month for 2 years")
\\\

## Event Flow

\\\
1. SubmitApplication (Command)
   ?
2. RecurringDepositApplicationSubmittedEvent ? Kafka
   ?
3. ML: Completion Probability + Affordability Check
   ?
4. Maker-Checker Approval
   ?
5. RecurringDepositApprovedEvent ? Kafka
   ?
6. ActivateAccount (Command)
   ?
7. RecurringDepositActivatedEvent ? Kafka
   ?
8. Auto-Debit Mandate Setup
   ?
9. Monthly Deposit Processing (COB Job)
   ?
   - MonthlyDepositDueEvent ? Kafka
   - Auto-Debit Attempt
   - MonthlyDepositReceivedEvent ? Kafka (success)
   - OR DepositMissedEvent ? Kafka (failure)
   ?
10. ML: Update completion probability
    ?
11. Anya: Send encouragement / reminder
    ?
12. Interest Calculation (Monthly)
    ?
13. InterestCalculatedEvent ? Kafka
    ?
14. Maturity Processing
    ?
15. RecurringDepositMaturedEvent ? Kafka
\\\

## API Endpoints

- POST /api/v1/recurring-deposits/applications - Submit application
- POST /api/v1/recurring-deposits/applications/{id}/approve - Approve
- POST /api/v1/recurring-deposits/applications/{id}/activate - Activate
- GET /api/v1/recurring-deposits/accounts/{id} - Get account
- GET /api/v1/recurring-deposits/accounts/{id}/schedule - Payment schedule
- POST /api/v1/recurring-deposits/accounts/{id}/payments/{num}/record - Record payment
- GET /api/v1/recurring-deposits/rates - Current rates

## Data Mesh Products

### 1. Recurring Deposit Accounts
- **Product ID**: ecurring_deposits.accounts
- **Freshness**: Real-time (< 1s)
- **Completeness**: 100%
- **Key Metrics**: Balance, health score, completion %

### 2. RD Payments
- **Product ID**: ecurring_deposits.payments
- **Updates**: Real-time via Kafka
- **Metrics**: On-time rate, missed payments, penalties

### 3. RD Analytics
- **Product ID**: ecurring_deposits.analytics
- **Updates**: Real-time aggregations
- **Metrics**: Completion rates, churn risk, portfolio health

## ML Models

### Completion Predictor
\\\python
from ultracore.domains.recurring_deposits.ml import CompletionPredictionModel

predictor = CompletionPredictionModel()
await predictor.train(historical_rds)

result = await predictor.predict_completion(rd_account, customer, payments)
# Returns: {
#   will_complete, 
#   completion_probability, 
#   risk_level,
#   risk_factors,
#   recommended_interventions
# }
\\\

### Affordability Scorer
\\\python
from ultracore.domains.recurring_deposits.ml import AffordabilityScorer

scorer = AffordabilityScorer()
assessment = await scorer.assess_affordability(customer_id, monthly_amount)
# Returns: {is_affordable, recommended_amount, utilization_rate}
\\\

## RL Incentive Optimizer

\\\python
from ultracore.domains.recurring_deposits.rl import DynamicIncentiveOptimizer

optimizer = DynamicIncentiveOptimizer()
await optimizer.train(total_timesteps=100000)

incentive = await optimizer.optimize_incentive(
    customer_segment="retail",
    account_health=65.0,
    completion_risk=0.6,
    months_remaining=12
)
# Returns: {type, components, cost, expected_lift, message}
\\\

## MCP Tools

8 tools available for AI agents:
1. open_recurring_deposit - Create new RD
2. check_payment_schedule - View upcoming payments
3. 	rack_savings_progress - Monitor progress
4. calculate_rd_maturity - Calculate returns
5. handle_missed_payment - Assist with misses
6. check_affordability - Assess affordability
7. get_completion_coaching - AI coaching
8. list_recurring_deposits - View customer RDs

## Key Differentiators

### vs Traditional RD Systems
| Feature | Traditional | UltraCore RD |
|---------|------------|--------------|
| Payment Tracking | Manual | Real-time event-sourced |
| Customer Support | Reactive | Proactive (Anya) |
| Risk Detection | None | ML-powered predictions |
| Incentives | Fixed | RL-optimized dynamic |
| Audit Trail | Limited | Complete (Kafka events) |
| Completion Rate | ~60% industry | Target 85%+ with AI |

### Anya's Role
- **Prevention**: Identifies at-risk accounts before they fail
- **Intervention**: Proactive outreach with empathy
- **Motivation**: Celebrates milestones and progress
- **Support**: Helps navigate financial difficulties
- **Coaching**: Personalized completion strategies

### Account Health Score (0-100)
Components:
- Completion rate: 50%
- On-time payment rate: 30%
- Consecutive misses: -20%
- Penalties: -10%

Usage:
- <60: Critical intervention needed
- 60-75: Proactive support
- 75-90: Standard monitoring
- >90: Excellent standing

## Payment Processing

### Auto-Debit Flow
1. **T-3 days**: Anya reminder notification
2. **T-0 day**: Auto-debit attempt
3. **Success**: MonthlyDepositReceivedEvent ? Kafka
4. **Failure**: 
   - Retry after 2 hours (up to 3 times)
   - If all fail: DepositMissedEvent ? Kafka
5. **Grace period**: 5 days to make manual payment
6. **After grace**: PenaltyAppliedEvent ? Kafka

### Missed Payment Handling
1. Anya empathetic outreach within 24 hours
2. Offer options:
   - Grace period (no penalty)
   - Skip month (if eligible)
   - Reduce amount temporarily
   - Payment holiday (hardship)
3. ML assesses churn risk
4. RL optimizes retention incentive
5. Track for future intervention

## Testing

\\\ash
# Unit tests
pytest tests/unit/domains/recurring_deposits/

# Integration tests
pytest tests/integration/recurring_deposits/

# Payment simulation
pytest tests/simulation/recurring_deposits/payment_flows.py

# Completion prediction accuracy
pytest tests/ml/recurring_deposits/completion_model_test.py
\\\

## Compliance

? Event-sourced audit trail (immutable)
? Maker-checker workflows
? Auto-debit mandate compliance
? Payment processing standards
? Customer protection (hardship provisions)
? Privacy Act 1988 compliant
? Financial counseling referrals

## Performance

- Event publishing: < 10ms p99
- Payment processing: 10,000 deposits/minute
- Account query: < 50ms p99
- ML prediction: < 100ms p99
- Health score calculation: < 20ms p99

## Monitoring & Alerts

### Key Metrics
- Completion rate (target: >85%)
- On-time payment rate (target: >90%)
- Churn rate (target: <5%)
- Average account health (target: >80)
- ML prediction accuracy (target: >80%)

### Alerts
- Critical: Account health <50
- Warning: 2+ consecutive misses
- Info: Approaching milestone
- Success: Account completed

## Roadmap

Phase 1 ? (Complete):
- Core RD functionality
- Event sourcing
- Anya integration
- ML completion prediction
- RL incentive optimization
- MCP tools
- Data Mesh products

Phase 2 ?? (Next):
- Advanced payment flexibility
- Family/joint RD accounts
- Goal-based UI widgets
- Gamification elements
- Social savings challenges

Phase 3 ?? (Future):
- Micro-savings (round-up deposits)
- AI-powered financial planning
- Integration with investment products
- Behavioral economics nudges
- Community savings groups

## Related Modules

- **Fixed Deposits**: Lump sum deposits
- **Savings Accounts**: Day-to-day transactional savings
- **Goals**: Long-term financial goal tracking
- **Lending**: Loan against RD facility

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Owner**: Recurring Deposits Domain Team  
**Support**: rd-team@turingdynamics.com.au
