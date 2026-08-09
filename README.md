# Aegis Bank AI

> A secure, mock-first multi-agent banking assistant reference implementation.

[![Aegis Bank AI demo: chat, execution trace, architecture and trust model](docs/media/aegis-demo.gif)](docs/media/aegis-demo.mp4)

**[Watch the 12-second MP4 demo](docs/media/aegis-demo.mp4)** · [Open the live demo](https://aegis-bank-ai.vendra020.chatgpt.site/#demo)

The animated preview shows a safe multi-agent request, its execution trace, the fourteen-step architecture explorer and the mock-first trust model. Select it to open the full video file.

[Architecture evolution](docs/ARCHITECTURE_EVOLUTION.md) · [Security model](docs/SECURITY.md) · [API contract](docs/API.md) · [5-minute demo](docs/DEMO.md)

## Why this project exists

Most chatbot demos hide the interesting engineering. Aegis makes it visible. A request passes through an edge limit, mock identity, authorization policy, PII redaction, deterministic coordination, one or more domain agents, and isolated MCP-style HTTP services. The UI shows that trace beside every answer.

The boundaries and connection code are real. The customers, accounts, transactions, identity, tools, model responses and cost figures are synthetic. Nothing connects to a bank or external model by default.

## System at a glance

```mermaid
flowchart LR
  UI[React chat + trace] --> EDGE[Edge rate limit]
  EDGE --> AUTH[Mock authentication]
  AUTH --> PII[PII redaction]
  PII --> C[Coordinator]
  C --> AA[Accounts agent]
  C --> TA[Transactions agent]
  C --> SA[Service agent]
  AA -->|HTTP| AMCP[Accounts MCP-style service]
  TA -->|HTTP| TMCP[Transactions MCP-style service]
  SA -->|HTTP| SMCP[Service MCP-style service]
  C --> SESS[Session store]
  C --> OBS[Trace + synthetic cost]
  C --> LLM[Deterministic mock LLM]
```

## Architecture evolution: step-by-step flows

Each step adds one boundary or control in response to a limitation in the previous design. Select a heading to open the corresponding design note.

### 01 — [Simple demo](architecture/step-01.md)

One client, endpoint and agent prove the interaction before responsibilities are distributed.

```mermaid
flowchart LR
  USER[User] --> UI[React chat]
  UI --> API[Assistant API]
  API --> AGENT[Single agent]
  AGENT --> MODEL[Deterministic model adapter]
  MODEL --> UI
```

### 02 — [Bank APIs as tools](architecture/step-02.md)

Typed operations ground answers in explicit capabilities instead of generated claims.

```mermaid
flowchart LR
  AGENT[Agent] --> CATALOG[Typed tool catalog]
  CATALOG --> BAL[Get balance]
  CATALOG --> TXN[List transactions]
  CATALOG --> STMT[Get statement]
  CATALOG --> SVC[Service request]
  BAL & TXN & STMT & SVC --> DATA[Synthetic bank data]
```

### 03 — [Domain agents](architecture/step-03.md)

The growing tool catalog is divided into bounded domains with smaller policy surfaces.

```mermaid
flowchart LR
  REQUEST[User request] --> ROUTER[Intent router]
  ROUTER --> AA[Accounts agent]
  ROUTER --> TA[Transactions agent]
  ROUTER --> SA[Service agent]
  AA --> AT[Account tools]
  TA --> TT[Transaction tools]
  SA --> ST[Service tools]
```

### 04 — [Coordinator](architecture/step-04.md)

A deterministic planner handles cross-domain requests and runs independent reads concurrently.

```mermaid
flowchart LR
  REQUEST[User request] --> PLAN[Coordinator plan]
  PLAN -->|parallel| AA[Accounts agent]
  PLAN -->|parallel| TA[Transactions agent]
  PLAN -->|when needed| SA[Service agent]
  AA & TA & SA --> JOIN[Aggregate results]
  JOIN --> RESPONSE[Policy-filtered response]
```

### 05 — [MCP service layer](architecture/step-05.md)

Each domain moves behind an isolated, typed HTTP boundary with explicit timeouts and errors.

```mermaid
flowchart LR
  AGENTS[Domain agents] --> CLIENTS[Typed HTTP clients]
  CLIENTS -->|correlation ID| AMCP[Accounts MCP service]
  CLIENTS -->|correlation ID| TMCP[Transactions MCP service]
  CLIENTS -->|correlation ID| SMCP[Service MCP service]
  AMCP & TMCP & SMCP --> STORE[Synthetic stores]
```

### 06 — [Authentication](architecture/step-06.md)

Every request must establish a synthetic identity before orchestration begins.

```mermaid
flowchart LR
  REQUEST[API request] --> HEADER[Bearer token]
  HEADER --> AUTH[Authentication dependency]
  AUTH -->|valid| PRINCIPAL[Synthetic principal]
  AUTH -->|missing or invalid| REJECT[401 response]
  PRINCIPAL --> COORD[Coordinator]
```

### 07 — [Authorization](architecture/step-07.md)

Identity scopes are checked immediately before each capability is invoked.

```mermaid
flowchart LR
  PRINCIPAL[Principal scopes] --> POLICY[Policy check]
  INTENT[Planned capability] --> POLICY
  POLICY -->|allowed| AGENT[Domain agent]
  POLICY -->|denied| STOP[403 without tool call]
  AGENT --> TOOL[Authorized tool]
```

### 08 — [Session management](architecture/step-08.md)

Bounded, per-session memory enables follow-up turns without mixing customer context.

```mermaid
flowchart LR
  TURN[New turn + session ID] --> LOAD[Load bounded history]
  LOAD --> CONTEXT[Isolated context]
  CONTEXT --> COORD[Coordinator]
  COORD --> RESULT[Agent results]
  RESULT --> APPEND[Append sanitized turn]
  APPEND --> SESSION[In-memory session store]
```

### 09 — [LLM abstraction](architecture/step-09.md)

A provider interface keeps model choice out of agents and preserves a network-free default.

```mermaid
flowchart LR
  COORD[Coordinator and agents] --> PORT[LLM provider interface]
  PORT --> MOCK[Deterministic mock provider]
  PORT -. production extension .-> REAL[External provider adapter]
  MOCK --> RESPONSE[Generated response]
  REAL -. disabled by default .-> RESPONSE
```

### 10 — [PII redaction](architecture/step-10.md)

Sensitive patterns are replaced before planning, tracing or model use.

```mermaid
flowchart LR
  INPUT[Raw user input] --> SCAN[PII pattern scan]
  SCAN -->|card, SSN or email| REDACT[Replace sensitive values]
  SCAN -->|no match| CLEAN[Approved text]
  REDACT --> CLEAN
  CLEAN --> PLAN[Planner and model boundary]
  CLEAN --> TRACE[Sanitized trace]
```

### 11 — [Agent evaluation](architecture/step-11.md)

Executable cases make routing, tool selection and safety behavior reviewable.

```mermaid
flowchart LR
  CASE[Evaluation case] --> SYSTEM[Coordinator + agents]
  SYSTEM --> OBSERVED[Observed plan, tools and answer]
  EXPECTED[Expected behavior] --> COMPARE[Assertions]
  OBSERVED --> COMPARE
  COMPARE -->|match| PASS[Pass]
  COMPARE -->|regression| FAIL[Fail CI]
```

### 12 — [Observability](architecture/step-12.md)

Sanitized stages explain what happened without exposing raw customer input.

```mermaid
flowchart LR
  REQUEST[Correlated request] --> STAGES[Edge → auth → PII → plan → tools]
  STAGES --> EVENTS[Stage, outcome, detail and duration]
  EVENTS --> TRACE[Sanitized execution trace]
  TRACE --> RESPONSE[Client response]
  TRACE --> OPS[Operational diagnosis]
```

### 13 — [Cost tracking](architecture/step-13.md)

Synthetic attribution makes economic tradeoffs visible before a paid provider is introduced.

```mermaid
flowchart LR
  PLAN[Execution plan] --> USAGE[Agent and tool usage]
  USAGE --> ESTIMATE[Synthetic cost estimate]
  ESTIMATE --> TRACE[Request trace]
  ESTIMATE --> BUDGET[Budget policy input]
  TRACE --> RESPONSE[Response metadata]
```

### 14 — [Edge security](architecture/step-14.md)

The final layer rejects abuse before expensive or sensitive processing begins.

```mermaid
flowchart LR
  INTERNET[Client traffic] --> EDGE[Gateway / WAF boundary]
  EDGE --> RATE[Rate limit]
  RATE -->|allowed| API[Assistant API]
  RATE -->|exceeded| REJECT[429 response]
  API --> AUTH[Authentication]
  AUTH --> PII[PII guard]
  PII --> COORD[Coordinator]
```

## What is real and what is mocked

| Concern | Implemented for real | Intentionally mocked |
|---|---|---|
| Web experience | Responsive React UI, keyboard-accessible chat and architecture viewer | Customer identity and displayed values |
| Orchestration | Typed plans, concurrent multi-agent execution, policies and error boundaries | Natural-language generation |
| Integration | `httpx` calls, service URLs, timeouts, headers, typed request/response bodies | The three local data providers |
| Security | Auth dependency, scopes, redaction, rate-limit boundary | Identity provider, WAF and production secrets |
| Operations | Correlation IDs, per-stage traces and calculated mock cost | Telemetry backend and billing |

## Repository layout

```text
app/                 Interactive React/TypeScript portfolio experience
backend/app/         FastAPI gateway, coordinator, agents and guardrails
backend/services/    Three isolated MCP-style synthetic banking services
backend/tests/       Unit and orchestration tests
architecture/        One concise design note for every step from 01–14
docs/                Architecture, security, API and interview demo guides
evals/               Seven routing, tool-use and safety evaluation cases
scripts/             Local multi-service launcher
.github/workflows/   Frontend, backend and evaluation CI
```

## Run locally

Prerequisites: Node.js 22+, Python 3.11+.

```powershell
npm install
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
./scripts/run-local.ps1
```

Open `http://localhost:3000`. The launcher starts the coordinator on port `8000` and the mock services on ports `8101`–`8103`.

Run verification separately:

```powershell
npm run build
python -m pytest backend/tests
python evals/evaluate.py
```

## Safe demo prompts

- `What is my checking balance?`
- `Show my last 5 transactions`
- `Get my May statement`
- `Order a cheque book`
- `Change my address`
- `Balance and recent transactions`
- `My card is 4111 1111 1111 1111`

That card number is a standard non-production test value. The project redacts it before routing and calls no banking tool.

## Safety contract

- Mock mode is explicit in responses and service headers.
- The only accepted identity token is `Bearer mock-demo-token`.
- External model access is disabled and unnecessary.
- Write-like actions are simulations; cheque books are not mailed and address changes are not committed.
- The project contains no real customer data, bank endpoint or production credential.

## Interview story

Start with the UI, run the multi-agent prompt, then run the PII test. Explain that the architecture did not begin with fourteen boxes: each step addresses a concrete limitation in the previous design. Finish with the evaluation suite and the “real boundaries / mock data” table. See [the five-minute script](docs/DEMO.md).

## Disclaimer

For education and portfolio demonstration only. Aegis Bank AI is not a bank, does not provide financial advice, and must not be connected to production financial systems without a full security, privacy, compliance and operational review.
