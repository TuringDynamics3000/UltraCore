# build-data-mesh.ps1
$ErrorActionPreference = "Continue"

Write-Host "`n=== Building UltraCore Data Mesh ===" -ForegroundColor Cyan

cd src

# Create Data Mesh Structure
Write-Host "`nCreating Data Mesh Domains..." -ForegroundColor Yellow

# Client Domain
New-Item -ItemType Directory -Path "ultracore/domains/client/data_products" -Force | Out-Null
New-Item -ItemType Directory -Path "ultracore/data_mesh/catalog" -Force | Out-Null
New-Item -ItemType Directory -Path "ultracore/data_mesh/governance" -Force | Out-Null
New-Item -ItemType Directory -Path "ultracore/data_mesh/platform" -Force | Out-Null

# Data Mesh API
@"
from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api/v1/data-mesh", tags=["Data Mesh"])

CATALOG = {
    "customer_360": {
        "domain": "client",
        "name": "customer_360",
        "description": "Complete customer view",
        "owner": "client-team@turingdynamics.com.au"
    },
    "loan_portfolio": {
        "domain": "loan", 
        "name": "loan_portfolio",
        "description": "Loan portfolio analytics",
        "owner": "loan-team@turingdynamics.com.au"
    },
    "account_balances": {
        "domain": "account",
        "name": "account_balances", 
        "description": "Real-time balances",
        "owner": "account-team@turingdynamics.com.au"
    }
}

@router.get("/catalog")
async def get_catalog() -> List[Dict]:
    return list(CATALOG.values())

@router.get("/catalog/search")
async def search_catalog(q: str) -> List[Dict]:
    results = []
    for product in CATALOG.values():
        if q.lower() in product["name"].lower() or q.lower() in product["description"].lower():
            results.append(product)
    return results

@router.get("/health")
async def health() -> Dict:
    return {"status": "healthy", "products": len(CATALOG)}
"@ | Out-File -FilePath "ultracore/data_mesh/api.py" -Encoding UTF8

# Update main.py
@"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ultracore.domains.loan.api import router as loan_router
from ultracore.data_mesh.api import router as data_mesh_router

app = FastAPI(
    title="UltraCore with Data Mesh",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loan_router, prefix="/api/v1/loans", tags=["Loans"])
app.include_router(data_mesh_router)

@app.get("/")
async def root():
    return {
        "service": "UltraCore",
        "company": "TuringDynamics",
        "version": "1.0.0",
        "data_mesh": "/api/v1/data-mesh/catalog"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

def main():
    uvicorn.run("ultracore.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
"@ | Out-File -FilePath "ultracore/main.py" -Encoding UTF8

# Create __init__ files
"" | Out-File -FilePath "ultracore/data_mesh/__init__.py" -Encoding UTF8
"" | Out-File -FilePath "ultracore/data_mesh/catalog/__init__.py" -Encoding UTF8

cd ..

Write-Host "`nData Mesh Created!" -ForegroundColor Green
Write-Host "`nRestart server:" -ForegroundColor Yellow
Write-Host '$env:PYTHONPATH = "src"' -ForegroundColor Cyan
Write-Host "python -m ultracore.main" -ForegroundColor Cyan
Write-Host "`nVisit: http://localhost:8000/docs`n" -ForegroundColor Cyan