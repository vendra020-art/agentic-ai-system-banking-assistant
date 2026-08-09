from typing import Any


class FakeToolClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any], str]] = []

    async def call(self, service: str, tool: str, arguments: dict[str, Any], request_id: str) -> dict[str, Any]:
        self.calls.append((service, tool, arguments, request_id))
        payloads = {
            ("accounts", "get-balance"): {"ledger_balance": 8420.17, "available_balance": 8120.17},
            ("transactions", "list-recent"): {"transactions": [{"merchant": "Lakeside Market", "amount": -86.42}]},
            ("transactions", "request-statement"): {"reference": "STM-MAY-2026-1042"},
            ("service", "request-cheque-book"): {"reference": "SR-20481", "will_ship": False},
            ("service", "prepare-address-change"): {"reference": "SR-20482", "committed": False},
        }
        return payloads[(service, tool)]
