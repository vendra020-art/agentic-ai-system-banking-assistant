from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI(title="Mock Accounts MCP", version="0.1.0")


class CustomerRequest(BaseModel):
    customer_id: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "accounts", "mock": True}


@app.post("/tools/get-balance")
async def get_balance(payload: CustomerRequest, x_correlation_id: str = Header(default="missing")):
    return {"customer_id": payload.customer_id, "account": "Everyday Checking", "currency": "USD", "ledger_balance": 8420.17, "available_balance": 8120.17, "as_of": "2026-08-08T09:42:00-05:00", "correlation_id": x_correlation_id, "mock": True}
