"""
UltraCore Financial API - Complete Platform
Version 5.0.0 with Accounting Module
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.insert(0, r'C:\Users\mjmil\UltraCore')

from ultracore.api.v1.financial.routes import router as financial_router
from ultracore.api.v1.ultrawealth.routes import router as ultrawealth_router
from ultracore.api.v1.clients.routes import router as clients_router
from ultracore.api.v1.holdings.routes import router as holdings_router
from ultracore.api.v1.transactions.routes import router as transactions_router
from ultracore.api.v1.accounting.routes import router as accounting_router

app = FastAPI(
    title="UltraCore Financial Platform",
    description="Complete wealth management platform with full accounting system",
    version="5.0.0"
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
app.include_router(transactions_router)
app.include_router(accounting_router)

@app.get("/")
async def root():
    return {
        "message": "UltraCore Financial Platform",
        "version": "5.0.0",
        "modules": {
            "financial": "Global financial data (Yahoo Finance)",
            "ultrawealth": "Australian ETFs (100+)",
            "clients": "Client management, KYC, Onboarding",
            "holdings": "Positions, Portfolio, Rebalancing",
            "transactions": "Orders, Trading, Settlement",
            "accounting": "Double-Entry Bookkeeping, Financial Statements (NEW!)"
        },
        "accounting_system": {
            "double_entry_bookkeeping": "Complete audit trail",
            "chart_of_accounts": "30 standard accounts",
            "journal_entries": "Automated from transactions",
            "general_ledger": "Real-time balances",
            "trial_balance": "Always balanced",
            "balance_sheet": "Assets = Liabilities + Equity",
            "income_statement": "Revenue - Expenses = Net Income",
            "cash_flow_statement": "Operating, Investing, Financing",
            "reconciliation": "Automated account reconciliation",
            "integration": "Full transaction & holdings integration"
        },
        "architecture": {
            "event_streaming": "Kafka event-driven",
            "data_mesh": "Data governance & lineage",
            "ai_agents": "Validation & fraud detection",
            "ml_rl": "Optimal execution learning",
            "mcp_tools": "AI assistant integration",
            "double_entry": "GAAP compliant accounting"
        },
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": [
            "financial", "ultrawealth", "clients", 
            "holdings", "transactions", "accounting"
        ],
        "version": "5.0.0",
        "trading_enabled": True,
        "accounting_enabled": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
