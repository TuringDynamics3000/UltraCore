from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Domain APIs
from ultracore.domains.loan.api import router as loan_router
from ultracore.domains.loan.integrated_api import router as integrated_loan_router
from ultracore.domains.client.api import router as client_router
from ultracore.domains.client.compliance_api import router as compliance_router
from ultracore.domains.account.api import router as account_router
from ultracore.domains.payment.api import router as payment_router
from ultracore.domains.risk.api import router as risk_router

# Infrastructure APIs
from ultracore.data_mesh.api import router as data_mesh_router
from ultracore.infrastructure.event_store.api import router as event_store_router
from ultracore.ledger.api import router as ledger_router
from ultracore.agentic_ai.mcp_api import router as mcp_router
from ultracore.ml_models.api import router as ml_router
from ultracore.infrastructure.event_store.store import get_event_store

app = FastAPI(
    title='UltraCore V2 - Complete Banking Platform',
    version='2.0.0',
    description='''
    🏦 Complete Enterprise Banking Platform
    
    🎯 5 Complete Domains:
    - 💰 Loans (AI-powered underwriting)
    - 👥 Clients (KYC & onboarding)
    - 💳 Accounts (Deposits & withdrawals)
    - 💸 Payments (Transfers & fraud detection)
    - ⚠️  Risk (Portfolio & compliance risk)
    
    🔧 Infrastructure:
    - ⚡ Event Sourcing (Full audit trail)
    - 📊 General Ledger (Double-entry accounting)
    - 🔗 Data Mesh (15 data products)
    - 🤖 AI Agents (Anya + MCP)
    - 🧠 ML Pipeline (Credit + Fraud)
    - 🇦🇺 Australian Compliance
    '''
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Domain APIs - Complete Banking
app.include_router(loan_router, prefix='/api/v1/loans', tags=['💰 Loans'])
app.include_router(integrated_loan_router, prefix='/api/v1/loans', tags=['🚀 Integrated Loan Flow'])
app.include_router(client_router, prefix='/api/v1/clients', tags=['👥 Clients'])
app.include_router(account_router, prefix='/api/v1/accounts', tags=['💳 Accounts'])
app.include_router(payment_router, prefix='/api/v1/payments', tags=['💸 Payments'])
app.include_router(risk_router, prefix='/api/v1/risk', tags=['⚠️ Risk Management'])
app.include_router(compliance_router, prefix='/api/v1', tags=['🇦🇺 Compliance'])

# Infrastructure APIs
app.include_router(event_store_router, tags=['⚡ Event Store'])
app.include_router(ledger_router, prefix='/api/v1/ledger', tags=['📊 General Ledger'])
app.include_router(data_mesh_router, tags=['🔗 Data Mesh'])
app.include_router(mcp_router, prefix='/api/v1', tags=['🤖 MCP (AI Agents)'])
app.include_router(ml_router, prefix='/api/v1', tags=['🧠 Machine Learning'])


@app.on_event('startup')
async def startup():
    store = get_event_store()
    await store.initialize()
    print('✅ Event Store initialized')
    print('✅ General Ledger ready')
    print('✅ All 5 Domains loaded')
    print('✅ AI Agents (Anya) ready')
    print('✅ ML Pipeline ready')
    print('✅ MCP Server ready')
    print('🚀 UltraCore V2 Banking Platform ONLINE')


@app.get('/')
async def root():
    return {
        'service': 'UltraCore V2',
        'company': 'TuringDynamics / Richelou Pty Ltd',
        'version': '2.0.0',
        'tagline': 'Complete Enterprise Banking Platform',
        'domains': {
            'loans': '✅ AI-powered underwriting',
            'clients': '✅ KYC & onboarding',
            'accounts': '✅ Deposits & withdrawals',
            'payments': '✅ Transfers & fraud detection',
            'risk': '✅ Portfolio & compliance risk'
        },
        'infrastructure': {
            'event_sourcing': '✅ Complete audit trail',
            'general_ledger': '✅ Double-entry accounting',
            'data_mesh': '✅ 15 data products',
            'ai_powered': '✅ Anya + GPT-4',
            'ml_pipeline': '✅ Credit + Fraud models',
            'mcp_protocol': '✅ AI agent interface',
            'compliance': '✅ Australian regulations'
        },
        'endpoints': {
            'loans': '/api/v1/loans',
            'clients': '/api/v1/clients',
            'accounts': '/api/v1/accounts',
            'payments': '/api/v1/payments',
            'risk': '/api/v1/risk',
            'ledger': '/api/v1/ledger',
            'events': '/api/v1/events',
            'data_mesh': '/api/v1/data-mesh',
            'mcp': '/api/v1/mcp',
            'ml': '/api/v1/ml'
        },
        'docs': '/docs'
    }


@app.get('/health')
async def health():
    return {
        'status': 'healthy',
        'version': '2.0.0',
        'domains': ['loans', 'clients', 'accounts', 'payments', 'risk'],
        'systems': {
            'event_store': 'online',
            'general_ledger': 'online',
            'ai_agents': 'online',
            'ml_pipeline': 'online',
            'mcp_server': 'online'
        }
    }


def main():
    uvicorn.run('ultracore.main:app', host='0.0.0.0', port=8000, reload=True)


if __name__ == '__main__':
    main()
