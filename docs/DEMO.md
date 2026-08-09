# Five-minute interview demo

## 0:00–0:45 — Frame the problem

Open the landing page. State the contract: real application boundaries and HTTP integration, but synthetic banking data, mock identity, mock tools and a network-free model by default.

## 0:45–1:45 — Show a single-agent request

Choose **What is my checking balance?** Point out the edge, identity, PII, coordinator, Accounts agent, tool and response stages. The output is typed, traceable and explicitly mocked.

## 1:45–2:45 — Show coordination

Enter **Balance and recent transactions**. The coordinator creates two independent read actions and executes Accounts and Transactions concurrently. Note the two agents, two tool calls and shared correlation ID.

## 2:45–3:30 — Show the safety stop

Select **Run the PII redaction test**. The test card number is replaced before routing; no banking tool is called.

## 3:30–4:30 — Tell the evolution story

Open the architecture viewer and move from Step 1 to Step 14. Emphasize the three inferred bridge steps rather than claiming missing source images existed.

## 4:30–5:00 — Prove quality

Show the seven backend tests, seven evaluation cases and CI workflow. End with the distinction: the code demonstrates where production controls belong, not that a portfolio demo is production-compliant.
