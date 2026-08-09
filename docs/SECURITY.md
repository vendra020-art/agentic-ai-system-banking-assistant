# Security and trust model

This repository demonstrates control placement; it does not claim production banking compliance.

## Trust boundaries

- **Edge:** in-memory demo rate limiter; a production WAF/API gateway belongs here.
- **Identity:** one explicit mock bearer token creates a synthetic principal.
- **Policy:** each agent checks a named scope immediately before a tool call.
- **Model:** redaction occurs before routing or model processing; the default adapter never uses the network.
- **Services:** MCP-style services accept only typed input and always return `mock: true`.
- **State:** session histories are memory-only and keyed by a validated session identifier.
- **Telemetry:** trace details intentionally avoid raw PII and full prompts.

## Threats demonstrated

| Threat | Demo control | Production extension |
|---|---|---|
| Credential abuse | Fixed mock token and 401 handling | OIDC, short-lived tokens, MFA and device risk |
| Excessive privilege | Per-agent scopes | Central policy engine, relationship checks and audit |
| Sensitive prompt leakage | Card, SSN and email redaction | Data classification, DLP and regional controls |
| Tool abuse | Bounded typed tools | Confirmation, transaction limits and human approval |
| Resource exhaustion | Sliding-window request limit | Distributed quotas, WAF and adaptive throttling |
| Cross-request confusion | Correlation and session IDs | Signed context, TTLs and distributed session store |
| Supply-chain risk | Pinned dependencies and CI | SBOM, provenance, scanning and change control |

## Explicit non-goals

No encryption-key management, fraud decisioning, payment initiation, real KYC, production audit archive or regulatory assertion is implemented. “MCP-style” describes service contracts and boundaries; it is not a claim of protocol certification.
