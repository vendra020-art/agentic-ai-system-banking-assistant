from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    async def summarize(self, prompt: str, context: dict) -> str: ...


class MockLLMProvider:
    """Deterministic provider. It never opens a network connection."""

    async def summarize(self, prompt: str, context: dict) -> str:
        kind = context.get("kind")
        if kind == "balance_and_transactions":
            return "Your mock checking balance is $8,420.17. Your five latest synthetic transactions total $214.38."
        if kind == "balance":
            return "Your mock Everyday Checking balance is $8,420.17, with $8,120.17 available."
        if kind == "transactions":
            return "I found five recent synthetic transactions. The largest is Lakeside Market at $86.42."
        if kind == "statement":
            return f"Your mock statement request is ready: {context['reference']}."
        if kind == "cheque":
            return f"Your mock cheque book request was created: {context['reference']}. Nothing will be mailed."
        if kind == "address":
            return "I prepared a mock address change. A second confirmation is required before this demo can commit it."
        return "I can help with balances, recent transactions, statements, cheque books and address changes using synthetic data only."
