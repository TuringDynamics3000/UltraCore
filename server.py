"""
UltraCore Financial API - Complete Platform
Version 3.0.0 with Holdings/Positions Module (Kafka-First)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.insert(0, r'C:\Users\mjmil\UltraCore')

from ultracore.api.v1.financial.routes import router as financial_router
from ultracore.api.v1.ultrawealth.routes import router as ultrawealth_router
from ultracore.api.v1.clients.routes import router as clients_router
from ultracore.api.v1.holdings.routes import router as holdings_router

app = FastAPI(
    title="UltraCore Financial Platform",
    description="Complete wealth management platform with Kafka, Data Mesh, AI, ML/RL",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(financial_router)
app.include_router(ultrawealth_router)
app.include_router(clients_router)
app.include_router(holdings_router)

@app.get("/")
async def root():
    return {
        "message": "UltraCore Financial Platform",
        "version": "3.0.0",
        "modules": {
            "financial": "Global financial data (Yahoo Finance)",
            "ultrawealth": "Australian ETFs (100+)",
            "clients": "Client management, KYC, Onboarding",
            "holdings": "Positions, Portfolio, Rebalancing (Kafka-First)"
        },
        "architecture": {
            "event_streaming": "Kafka event-driven",
            "data_mesh": "Data governance & lineage",
            "ai_agents": "Autonomous monitoring & decisions",
            "ml_rl": "Reinforcement learning optimization",
            "mcp_tools": "AI assistant integration"
        },
        "features": {
            "event_sourcing": "Complete audit trail",
            "real_time_valuation": "Live mark-to-market",
            "cost_basis_tracking": "Multi-method tax optimization",
            "performance_analytics": "Comprehensive metrics",
            "auto_rebalancing": "AI-powered rebalancing",
            "tax_optimization": "Loss harvesting identification"
        },
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": ["financial", "ultrawealth", "clients", "holdings"],
        "version": "3.0.0",
        "architecture": "Kafka-First Event-Driven"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
