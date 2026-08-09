# Local API contract

## Coordinator

`POST http://127.0.0.1:8000/v1/chat`

```http
Authorization: Bearer mock-demo-token
Content-Type: application/json

{"message":"Balance and recent transactions","session_id":"demo-session"}
```

The response contains the redacted input, selected agents, called tools, per-stage trace, synthetic estimated cost and `mock: true`.

## MCP-style service endpoints

| Port | Service | Tools |
|---:|---|---|
| 8101 | Accounts | `get-balance` |
| 8102 | Transactions | `list-recent`, `request-statement` |
| 8103 | Service | `request-cheque-book`, `prepare-address-change` |

The coordinator uses real HTTP calls through `httpx`, supplies `X-Correlation-ID` and `X-Mock-Mode`, enforces a three-second timeout, and maps non-success HTTP responses to failures. The services never forward requests to another system.

Interactive OpenAPI documentation is available at `/docs` on every local FastAPI service.
