import pytest
from fastapi import HTTPException

from app.security import InMemoryRateLimiter, authenticate, redact_pii


def test_redacts_card_ssn_and_email():
    text, findings = redact_pii("Use 4111 1111 1111 1111, 123-45-6789, alex@example.test")
    assert text == "Use [CARD REDACTED], [SSN REDACTED], [EMAIL REDACTED]"
    assert findings == ["payment_card", "ssn", "email"]


def test_rate_limiter_blocks_after_capacity():
    limiter = InMemoryRateLimiter(requests=2, window_seconds=60)
    assert limiter.allow("demo") is True
    assert limiter.allow("demo") is True
    assert limiter.allow("demo") is False


def test_authentication_rejects_an_invalid_token():
    with pytest.raises(HTTPException) as error:
        authenticate("Bearer not-the-demo-token")
    assert error.value.status_code == 401
