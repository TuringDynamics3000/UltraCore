"""
PROPRIETARY AND CONFIDENTIAL
Copyright (c) 2025 Richelou Pty Ltd. All Rights Reserved.
TuringDynamics Division
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ultracore.domains.loan.api import router as loan_router

app = FastAPI(
    title="UltraCore™ by TuringDynamics",
    description="Event-Sourced Core Banking Platform",
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

@app.get("/")
async def root():
    return {
        "service": "UltraCore",
        "company": "TuringDynamics / Richelou Pty Ltd",
        "version": "1.0.0",
        "status": "operational",
        "copyright": "© 2025 Richelou Pty Ltd"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

def main():
    uvicorn.run("ultracore.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
