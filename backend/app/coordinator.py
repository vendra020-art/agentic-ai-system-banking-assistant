from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from uuid import uuid4

from .agents import AccountsAgent, ServiceAgent, TransactionsAgent
from .llm import LLMProvider, MockLLMProvider
from .mcp_client import ToolClient
from .models import ChatResponse, Principal, ToolResult, TraceEvent
from .security import redact_pii
from .session import SessionStore, sessions


@dataclass(frozen=True)
class Plan:
    intent: str
    actions: tuple[str, ...]


def plan_request(message: str) -> Plan:
    text = message.lower()
    if "[card redacted]" in text or "[ssn redacted]" in text:
        return Plan("sensitive_input", ())
    balance = any(word in text for word in ("balance", "checking", "savings"))
    transactions = any(word in text for word in ("transaction", "recent", "last 5", "spent"))
    if balance and transactions:
        return Plan("balance_and_transactions", ("balance", "recent"))
    if balance:
        return Plan("balance", ("balance",))
    if transactions:
        return Plan("transactions", ("recent",))
    if "statement" in text:
        return Plan("statement", ("statement",))
    if any(term in text for term in ("cheque", "checkbook", "check book")):
        return Plan("cheque", ("cheque",))
    if "address" in text or "move" in text:
        return Plan("address", ("address",))
    return Plan("help", ())


class Coordinator:
    def __init__(self, tools: ToolClient, llm: LLMProvider | None = None, store: SessionStore | None = None) -> None:
        self.accounts = AccountsAgent(tools)
        self.transactions = TransactionsAgent(tools)
        self.service = ServiceAgent(tools)
        self.llm = llm or MockLLMProvider()
        self.sessions = store or sessions

    async def handle(self, message: str, session_id: str, principal: Principal) -> ChatResponse:
        started = time.perf_counter()
        request_id = f"req-{uuid4().hex[:10]}"
        redacted, findings = redact_pii(message)
        plan = plan_request(redacted)
        trace = [
            TraceEvent(stage="edge", status="passed", detail="rate limit passed"),
            TraceEvent(stage="identity", status="passed", detail=f"{principal.subject} authenticated"),
            TraceEvent(stage="pii", status="passed", detail=f"redacted: {', '.join(findings)}" if findings else "no sensitive patterns"),
            TraceEvent(stage="coordinator", status="complete", detail=f"intent={plan.intent}; actions={','.join(plan.actions) or 'none'}"),
        ]
        self.sessions.append(session_id, "user", redacted)

        results = await asyncio.gather(*(self._run(action, principal, request_id) for action in plan.actions))
        for result in results:
            trace.append(TraceEvent(stage="tool", status="called", detail=result.tool))

        context = self._context(plan, results)
        answer = (
            "I removed sensitive data before orchestration. No banking tool was called."
            if plan.intent == "sensitive_input"
            else await self.llm.summarize(redacted, context)
        )
        self.sessions.append(session_id, "assistant", answer)
        trace.append(TraceEvent(stage="response", status="complete", detail="mock response delivered", duration_ms=round((time.perf_counter() - started) * 1000, 2)))
        return ChatResponse(
            request_id=request_id,
            session_id=session_id,
            answer=answer,
            redacted_input=redacted,
            agents=self._agents(plan),
            tools=[result.tool for result in results],
            trace=trace,
            estimated_cost_usd=round(0.0003 + 0.00045 * len(results), 6),
            data=context,
        )

    async def _run(self, action: str, principal: Principal, request_id: str) -> ToolResult:
        actions = {
            "balance": self.accounts.balance,
            "recent": self.transactions.recent,
            "statement": self.transactions.statement,
            "cheque": self.service.cheque_book,
            "address": self.service.address_change,
        }
        return await actions[action](principal, request_id)

    @staticmethod
    def _context(plan: Plan, results: list[ToolResult]) -> dict:
        context = {"kind": plan.intent, "results": [result.payload for result in results]}
        for result in results:
            if "reference" in result.payload:
                context["reference"] = result.payload["reference"]
        return context

    @staticmethod
    def _agents(plan: Plan) -> list[str]:
        mapping = {"balance": "accounts-agent", "recent": "transactions-agent", "statement": "transactions-agent", "cheque": "service-agent", "address": "service-agent"}
        return list(dict.fromkeys(mapping[action] for action in plan.actions)) or ["coordinator"]
