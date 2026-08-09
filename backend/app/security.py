from __future__ import annotations

import re
from collections import defaultdict, deque
from time import monotonic

from fastapi import Header, HTTPException, Request

from .models import Principal

CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)")
SSN_PATTERN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


def redact_pii(text: str) -> tuple[str, list[str]]:
    findings: list[str] = []
    rules = ((CARD_PATTERN, "[CARD REDACTED]", "payment_card"), (SSN_PATTERN, "[SSN REDACTED]", "ssn"), (EMAIL_PATTERN, "[EMAIL REDACTED]", "email"))
    redacted = text
    for pattern, replacement, label in rules:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            findings.extend([label] * count)
    return redacted, findings


def authenticate(authorization: str = Header(default="Bearer mock-demo-token")) -> Principal:
    if authorization != "Bearer mock-demo-token":
        raise HTTPException(status_code=401, detail="Invalid mock identity token")
    return Principal(subject="demo-user", customer_id="CUST-1042", scopes={"accounts:read", "transactions:read", "service:write"})


def require_scope(principal: Principal, scope: str) -> None:
    if scope not in principal.scopes:
        raise HTTPException(status_code=403, detail=f"Missing required scope: {scope}")


class InMemoryRateLimiter:
    def __init__(self, requests: int = 30, window_seconds: int = 60) -> None:
        self.requests = requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = monotonic()
        bucket = self._buckets[key]
        while bucket and bucket[0] <= now - self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.requests:
            return False
        bucket.append(now)
        return True


rate_limiter = InMemoryRateLimiter()


async def enforce_edge_limit(request: Request) -> None:
    key = request.client.host if request.client else "local"
    if not rate_limiter.allow(key):
        raise HTTPException(status_code=429, detail="Mock edge rate limit exceeded")
