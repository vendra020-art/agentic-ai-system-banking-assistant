from __future__ import annotations

from .mcp_client import ToolClient
from .models import Principal, ToolResult
from .security import require_scope


class AccountsAgent:
    name = "accounts-agent"

    def __init__(self, tools: ToolClient) -> None:
        self.tools = tools

    async def balance(self, principal: Principal, request_id: str) -> ToolResult:
        require_scope(principal, "accounts:read")
        payload = await self.tools.call("accounts", "get-balance", {"customer_id": principal.customer_id}, request_id)
        return ToolResult(tool="accounts.get_balance", payload=payload)


class TransactionsAgent:
    name = "transactions-agent"

    def __init__(self, tools: ToolClient) -> None:
        self.tools = tools

    async def recent(self, principal: Principal, request_id: str) -> ToolResult:
        require_scope(principal, "transactions:read")
        payload = await self.tools.call("transactions", "list-recent", {"customer_id": principal.customer_id, "limit": 5}, request_id)
        return ToolResult(tool="transactions.list_recent", payload=payload)

    async def statement(self, principal: Principal, request_id: str) -> ToolResult:
        require_scope(principal, "transactions:read")
        payload = await self.tools.call("transactions", "request-statement", {"customer_id": principal.customer_id, "month": "2026-05"}, request_id)
        return ToolResult(tool="transactions.request_statement", payload=payload)


class ServiceAgent:
    name = "service-agent"

    def __init__(self, tools: ToolClient) -> None:
        self.tools = tools

    async def cheque_book(self, principal: Principal, request_id: str) -> ToolResult:
        require_scope(principal, "service:write")
        payload = await self.tools.call("service", "request-cheque-book", {"customer_id": principal.customer_id}, request_id)
        return ToolResult(tool="service.request_cheque_book", payload=payload)

    async def address_change(self, principal: Principal, request_id: str) -> ToolResult:
        require_scope(principal, "service:write")
        payload = await self.tools.call("service", "prepare-address-change", {"customer_id": principal.customer_id}, request_id)
        return ToolResult(tool="service.prepare_address_change", payload=payload)
