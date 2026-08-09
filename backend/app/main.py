from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .coordinator import Coordinator
from .mcp_client import HttpMCPClient
from .models import ChatRequest, ChatResponse, Principal
from .security import authenticate, enforce_edge_limit

SERVICE_URLS = {
    "accounts": "http://127.0.0.1:8101",
    "transactions": "http://127.0.0.1:8102",
    "service": "http://127.0.0.1:8103",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.coordinator = Coordinator(HttpMCPClient(client, SERVICE_URLS))
        yield


app = FastAPI(title="Aegis Bank AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["POST", "GET"], allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"])


@app.get("/health")
async def health() -> dict[str, object]:
    return {"status": "ok", "mock": True, "external_connections": False}


@app.post("/v1/chat", response_model=ChatResponse, dependencies=[Depends(enforce_edge_limit)])
async def chat(payload: ChatRequest, request: Request, principal: Principal = Depends(authenticate)) -> ChatResponse:
    return await request.app.state.coordinator.handle(payload.message, payload.session_id, principal)
