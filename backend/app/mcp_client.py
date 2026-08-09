from __future__ import annotations

from typing import Any, Protocol

import httpx


class ToolClient(Protocol):
    async def call(self, service: str, tool: str, arguments: dict[str, Any], request_id: str) -> dict[str, Any]: ...


class HttpMCPClient:
    """Real HTTP transport around intentionally local, synthetic services."""

    def __init__(self, client: httpx.AsyncClient, service_urls: dict[str, str]) -> None:
        self.client = client
        self.service_urls = service_urls

    async def call(self, service: str, tool: str, arguments: dict[str, Any], request_id: str) -> dict[str, Any]:
        response = await self.client.post(
            f"{self.service_urls[service]}/tools/{tool}",
            json=arguments,
            headers={"X-Correlation-ID": request_id, "X-Mock-Mode": "true"},
            timeout=3.0,
        )
        response.raise_for_status()
        return response.json()
