from fastapi import FastAPI, Header
from pydantic import BaseModel, Field

app = FastAPI(title="Mock Transactions MCP", version="0.1.0")

TRANSACTIONS = [
    {"merchant": "Lakeside Market", "amount": -86.42, "date": "2026-08-07"},
    {"merchant": "Metro Energy", "amount": -64.90, "date": "2026-08-06"},
    {"merchant": "Northstar Coffee", "amount": -18.60, "date": "2026-08-06"},
    {"merchant": "CloudStream", "amount": 12.00, "date": "2026-08-05"},
    {"merchant": "City Transit", "amount": -56.46, "date": "2026-08-04"},
]


class RecentRequest(BaseModel):
    customer_id: str
    limit: int = Field(default=5, ge=1, le=20)


class StatementRequest(BaseModel):
    customer_id: str
    month: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "transactions", "mock": True}


@app.post("/tools/list-recent")
async def list_recent(payload: RecentRequest, x_correlation_id: str = Header(default="missing")):
    return {"customer_id": payload.customer_id, "transactions": TRANSACTIONS[: payload.limit], "correlation_id": x_correlation_id, "mock": True}


@app.post("/tools/request-statement")
async def request_statement(payload: StatementRequest, x_correlation_id: str = Header(default="missing")):
    return {"reference": "STM-MAY-2026-1042", "month": payload.month, "status": "generated", "download_url": None, "correlation_id": x_correlation_id, "mock": True}
