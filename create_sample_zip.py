import os
import zipfile

def create_sample_project():
    zip_path = "Demo_FinTech_Portal.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # README.md
        z.writestr("README.md", """# FinTech Customer Portal
A secure banking and payments customer portal web application.

## Overview
This repository contains the backend and frontend for the customer portal.

## Setup & Running
```bash
pip install -r requirements.txt
python -m src.server
```
""")

        # SECURITY.md
        z.writestr("SECURITY.md", """# Security Policy

## Reporting a Vulnerability
Please report security vulnerabilities to security@fintechportal.example.com.
We respond to critical reports within 24 hours.

## Supported Versions
| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |
""")

        # requirements.txt
        z.writestr("requirements.txt", """fastapi==0.110.0
uvicorn==0.28.0
pydantic==2.6.4
sqlalchemy==2.0.28
cryptography==42.0.5
python-jose==3.3.0
pytest==8.1.1
httpx==0.27.0
""")

        # docs/architecture.md
        z.writestr("docs/architecture.md", """# System Architecture & Design

## Architecture Overview
The system follows a three-tier architecture:
- Presentation Tier: React SPA
- Application Tier: FastAPI REST Services
- Data Tier: PostgreSQL database with encrypted volume storage

## Data Flow & Trust Boundaries
1. External Client -> Cloudflare WAF -> Ingress Gateway (TLS 1.3 termination)
2. Ingress Gateway -> API Service (Internal VPC)
3. API Service -> PostgreSQL Database (mTLS with IAM authentication)

## Encryption & Secrets Management
- All sensitive customer data (PII, account numbers) are encrypted at rest using AES-256.
- Application secrets are provisioned via environment variables from Vault.
""")

        # src/app.py
        z.writestr("src/app.py", """import os
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel

app = FastAPI(title="FinTech Portal API", version="2.1.0")

class TransferRequest(BaseModel):
    recipient_account: str
    amount: float
    currency: str = "USD"

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fintech-portal-api"}

@app.post("/api/v1/transfers")
def initiate_transfer(req: TransferRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")
    if req.amount > 50000:
        raise HTTPException(status_code=403, detail="Amounts over $50,000 require multi-factor authorization")
    return {"status": "processed", "transfer_id": "tx_992147", "amount": req.amount}
""")

        # tests/test_app.py
        z.writestr("tests/test_app.py", """import pytest
from src.app import app

def test_health_check():
    # Basic sanity test for service health
    assert app.title == "FinTech Portal API"

def test_transfer_validation():
    # Verify input validation boundary
    assert True
""")

        # .github/workflows/ci.yml
        z.writestr(".github/workflows/ci.yml", """name: CI / Security Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run Test Suite
        run: |
          pytest tests/
""")

    print(f"Created {zip_path} successfully. Size: {os.path.getsize(zip_path)} bytes.")

if __name__ == "__main__":
    create_sample_project()
