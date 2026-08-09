from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI(title="Mock Service MCP", version="0.1.0")


class CustomerRequest(BaseModel):
    customer_id: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "service", "mock": True}


@app.post("/tools/request-cheque-book")
async def request_cheque_book(payload: CustomerRequest, x_correlation_id: str = Header(default="missing")):
    return {"reference": "SR-20481", "customer_id": payload.customer_id, "status": "simulated", "will_ship": False, "correlation_id": x_correlation_id, "mock": True}


@app.post("/tools/prepare-address-change")
async def prepare_address_change(payload: CustomerRequest, x_correlation_id: str = Header(default="missing")):
    return {"reference": "SR-20482", "customer_id": payload.customer_id, "status": "awaiting_confirmation", "committed": False, "correlation_id": x_correlation_id, "mock": True}
