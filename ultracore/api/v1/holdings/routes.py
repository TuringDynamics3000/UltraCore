"""
Holdings Management API Routes
Complete RESTful API for position tracking and portfolio management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from ultracore.modules.holdings.holdings_service import holdings_service
from ultracore.modules.holdings.position_tracker import position_tracker, CostBasisMethod
from ultracore.modules.holdings.performance_analytics import performance_analytics
from ultracore.modules.holdings.rebalancing_engine import rebalancing_engine, RebalancingStrategy

router = APIRouter(prefix="/api/v1/holdings", tags=["holdings"])

# ============================================================================
# POSITION MANAGEMENT
# ============================================================================

@router.post("/positions/open")
async def open_position(
    client_id: str,
    ticker: str,
    quantity: float,
    purchase_price: float,
    purchase_date: Optional[str] = None,
    transaction_id: Optional[str] = None
):
    """Open new position"""
    try:
        date = datetime.fromisoformat(purchase_date) if purchase_date else None
        
        result = await holdings_service.open_position(
            client_id=client_id,
            ticker=ticker,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=date,
            transaction_id=transaction_id
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/positions/{position_id}/close")
async def close_position(
    position_id: str,
    sale_price: float,
    sale_date: Optional[str] = None,
    transaction_id: Optional[str] = None
):
    """Close position"""
    try:
        date = datetime.fromisoformat(sale_date) if sale_date else None
        
        result = await holdings_service.close_position(
            position_id=position_id,
            sale_price=sale_price,
            sale_date=date,
            transaction_id=transaction_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions/{position_id}")
async def get_position(
    position_id: str,
    include_lineage: bool = False
):
    """Get position details"""
    position = await holdings_service.get_position(position_id, include_lineage)
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    return position

@router.put("/positions/{position_id}/value")
async def update_position_value(
    position_id: str,
    current_price: float
):
    """Update position with current market price"""
    try:
        result = await holdings_service.update_position_value(
            position_id=position_id,
            current_price=current_price
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions/{position_id}/reconstruct")
async def reconstruct_position(position_id: str):
    """Reconstruct position from event stream"""
    try:
        state = await holdings_service.reconstruct_position_from_events(position_id)
        return {
            "position_id": position_id,
            "reconstructed_state": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PORTFOLIO MANAGEMENT
# ============================================================================

@router.get("/portfolio/{client_id}/positions")
async def get_client_positions(
    client_id: str,
    status: Optional[str] = None
):
    """Get all positions for client"""
    positions = await holdings_service.get_client_positions(client_id, status)
    return {"client_id": client_id, "positions": positions}

@router.get("/portfolio/{client_id}/value")
async def get_portfolio_value(
    client_id: str,
    real_time: bool = True
):
    """Get portfolio valuation"""
    valuation = await holdings_service.get_portfolio_value(client_id, real_time)
    return valuation

@router.get("/portfolio/{client_id}/monitor")
async def monitor_portfolio(client_id: str):
    """Run AI monitoring on portfolio"""
    monitoring = await holdings_service.monitor_portfolio_with_ai(client_id)
    return monitoring

# ============================================================================
# COST BASIS & TAX
# ============================================================================

@router.get("/cost-basis/{ticker}/summary")
async def get_cost_basis_summary(ticker: str):
    """Get cost basis summary for ticker"""
    summary = position_tracker.get_position_summary(ticker)
    return summary

@router.post("/cost-basis/{ticker}/sell")
async def calculate_sale_basis(
    ticker: str,
    quantity: float,
    sale_price: float,
    sale_date: str,
    method: CostBasisMethod = CostBasisMethod.FIFO
):
    """Calculate cost basis for sale"""
    try:
        date = datetime.fromisoformat(sale_date)
        
        result = position_tracker.sell_position(
            ticker=ticker,
            quantity=quantity,
            sale_price=sale_price,
            sale_date=date,
            method=method
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cost-basis/{ticker}/tax-loss-harvest")
async def get_tax_loss_opportunities(
    ticker: str,
    current_price: float,
    min_loss: float = 1000
):
    """Get tax loss harvesting opportunities"""
    opportunities = position_tracker.tax_loss_harvest_opportunities(
        ticker=ticker,
        current_price=current_price,
        min_loss=min_loss
    )
    
    return {
        "ticker": ticker,
        "opportunities": opportunities,
        "total_potential_loss": sum(o["potential_loss"] for o in opportunities),
        "total_tax_benefit": sum(o["tax_benefit"] for o in opportunities)
    }

@router.get("/cost-basis/{ticker}/unrealized-gl")
async def get_unrealized_gl(
    ticker: str,
    current_price: float
):
    """Calculate unrealized gains/losses"""
    result = position_tracker.calculate_unrealized_gl(ticker, current_price)
    return result

# ============================================================================
# PERFORMANCE ANALYTICS
# ============================================================================

@router.post("/analytics/performance")
async def calculate_performance(
    portfolio_history: List[dict],
    benchmark_returns: Optional[List[float]] = None
):
    """Calculate comprehensive performance metrics"""
    try:
        metrics = performance_analytics.calculate_comprehensive_metrics(
            portfolio_history,
            benchmark_returns
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/sharpe")
async def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: Optional[float] = None
):
    """Calculate Sharpe ratio"""
    sharpe = performance_analytics.calculate_sharpe_ratio(returns, risk_free_rate)
    return {"sharpe_ratio": sharpe}

@router.post("/analytics/max-drawdown")
async def calculate_max_drawdown(values: List[float]):
    """Calculate maximum drawdown"""
    result = performance_analytics.calculate_max_drawdown(values)
    return result

@router.post("/analytics/alpha-beta")
async def calculate_alpha_beta(
    portfolio_returns: List[float],
    benchmark_returns: List[float]
):
    """Calculate alpha and beta"""
    result = performance_analytics.calculate_alpha_beta(
        portfolio_returns,
        benchmark_returns
    )
    return result

# ============================================================================
# REBALANCING
# ============================================================================

@router.post("/rebalancing/{client_id}/evaluate")
async def evaluate_rebalancing(
    client_id: str,
    target_allocation: dict,
    strategy: RebalancingStrategy = RebalancingStrategy.THRESHOLD
):
    """Evaluate if portfolio needs rebalancing"""
    try:
        portfolio = await holdings_service.get_portfolio_value(client_id)
        positions = portfolio.get("positions", [])
        
        # Calculate current allocation
        total_value = portfolio.get("total_value", 0)
        current_allocation = {}
        
        for position in positions:
            ticker = position["ticker"]
            value = position["market_value"]
            current_allocation[ticker] = value / total_value if total_value > 0 else 0
        
        evaluation = await rebalancing_engine.evaluate_rebalancing_need(
            current_allocation=current_allocation,
            target_allocation=target_allocation,
            strategy=strategy
        )
        
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebalancing/{client_id}/plan")
async def generate_rebalancing_plan(
    client_id: str,
    target_allocation: dict,
    min_trade_size: float = 100
):
    """Generate rebalancing trades"""
    try:
        portfolio = await holdings_service.get_portfolio_value(client_id)
        positions = portfolio.get("positions", [])
        total_value = portfolio.get("total_value", 0)
        
        plan = await rebalancing_engine.generate_rebalancing_trades(
            current_positions=positions,
            target_allocation=target_allocation,
            total_value=total_value,
            min_trade_size=min_trade_size
        )
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebalancing/{client_id}/execute")
async def execute_rebalancing(
    client_id: str,
    rebalancing_plan: dict,
    dry_run: bool = True
):
    """Execute rebalancing"""
    try:
        result = await rebalancing_engine.execute_rebalancing(
            client_id=client_id,
            rebalancing_plan=rebalancing_plan,
            dry_run=dry_run
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebalancing/{client_id}/schedule")
async def schedule_rebalancing(
    client_id: str,
    target_allocation: dict,
    schedule: str = "quarterly"
):
    """Schedule automatic rebalancing"""
    try:
        result = rebalancing_engine.schedule_rebalancing(
            client_id=client_id,
            target_allocation=target_allocation,
            schedule=schedule
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AI RECOMMENDATIONS
# ============================================================================

@router.get("/recommendations/{client_id}/rebalancing")
async def get_ai_rebalancing_recommendations(
    client_id: str,
    target_allocation: dict
):
    """Get AI-powered rebalancing recommendations"""
    recommendations = await holdings_service.get_rebalancing_recommendations(
        client_id=client_id,
        target_allocation=target_allocation
    )
    
    return recommendations

@router.get("/recommendations/{client_id}/optimize")
async def optimize_portfolio(
    client_id: str,
    risk_profile: str,
    constraints: Optional[dict] = None
):
    """Get portfolio optimization recommendations"""
    from ultracore.agents.holdings_agent import holdings_agent
    
    portfolio = await holdings_service.get_portfolio_value(client_id)
    
    optimization = await holdings_agent.optimize_portfolio(
        portfolio=portfolio,
        risk_profile=risk_profile,
        constraints=constraints
    )
    
    return optimization

@router.get("/recommendations/{client_id}/anomalies")
async def detect_anomalies(client_id: str):
    """Detect portfolio anomalies"""
    from ultracore.agents.holdings_agent import holdings_agent
    
    positions = await holdings_service.get_client_positions(client_id, status="open")
    
    anomalies = await holdings_agent.detect_anomalies(
        client_id=client_id,
        positions=positions
    )
    
    return anomalies
