from app.security import InMemoryRateLimiter, redact_pii


def test_redacts_card_ssn_and_email():
    text, findings = redact_pii("Use 4111 1111 1111 1111, 123-45-6789, alex@example.test")
    assert text == "Use [CARD REDACTED], [SSN REDACTED], [EMAIL REDACTED]"
    assert findings == ["payment_card", "ssn", "email"]


def test_rate_limiter_blocks_after_capacity():
    limiter = InMemoryRateLimiter(requests=2, window_seconds=60)
    assert limiter.allow("demo") is True
    assert limiter.allow("demo") is True
    assert limiter.allow("demo") is False
