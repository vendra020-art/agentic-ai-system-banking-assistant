from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Principal(BaseModel):
    subject: str
    customer_id: str
    scopes: set[str]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    session_id: str = Field(default="demo-session", pattern=r"^[a-zA-Z0-9_-]{3,64}$")


class TraceEvent(BaseModel):
    stage: str
    status: Literal["passed", "called", "blocked", "complete"]
    detail: str
    duration_ms: float = 0


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    answer: str
    redacted_input: str
    agents: list[str]
    tools: list[str]
    trace: list[TraceEvent]
    estimated_cost_usd: float
    mock: bool = True
    data: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool: str
    payload: dict[str, Any]
