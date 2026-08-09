"use client";

import { FormEvent, useMemo, useRef, useState } from "react";

type Message = { role: "assistant" | "user"; text: string };
type Trace = { label: string; detail: string; state: "complete" | "active" | "waiting" };
type DemoResult = { answer: string; agents: string[]; tools: string[]; pii: boolean; requestId?: string };

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

const architectureSteps = [
  { n: 1, title: "Simple demo", layer: "Foundation", note: "React chat → API → one agent → mock LLM." },
  { n: 2, title: "Bank APIs as tools", layer: "Capabilities", note: "Balance, transactions, statements and service requests become typed tools." },
  { n: 3, title: "Domain agents", layer: "Specialization", note: "Accounts, Transactions and Service agents own bounded banking domains." },
  { n: 4, title: "Coordinator", layer: "Orchestration", note: "A deterministic coordinator plans one or several agent calls." },
  { n: 5, title: "MCP service layer", layer: "Integration", note: "Agents call isolated local HTTP services through MCP-style contracts." },
  { n: 6, title: "Authentication", layer: "Trust", note: "Mock bank identity establishes who is making the request." },
  { n: 7, title: "Authorization", layer: "Trust · inferred", note: "Policy checks limit which customer, agent and tool scopes are allowed.", inferred: true },
  { n: 8, title: "Session management", layer: "Memory", note: "Conversation history and inter-agent results share a scoped session." },
  { n: 9, title: "LLM abstraction", layer: "Model · inferred", note: "A provider boundary keeps the default model local and deterministic.", inferred: true },
  { n: 10, title: "PII redaction", layer: "Safety", note: "Sensitive patterns are replaced before any model boundary." },
  { n: 11, title: "Agent evaluation", layer: "Quality · inferred", note: "Routing, safety, tool selection and regression cases become executable evals.", inferred: true },
  { n: 12, title: "Observability", layer: "Operations", note: "Correlation IDs connect prompts, agents, tools, latency and outcomes." },
  { n: 13, title: "Cost tracking", layer: "FinOps", note: "Synthetic token and tool costs are attributed per request." },
  { n: 14, title: "Edge security", layer: "Perimeter", note: "Rate limits, API gateway controls and WAF boundaries complete the design." },
] as const;

const starters = [
  "What is my checking balance?",
  "Show my last 5 transactions",
  "Get my May statement",
  "Order a cheque book",
  "Change my address",
  "Balance and recent transactions",
  "My card is 4111 1111 1111 1111",
];

function classify(input: string): DemoResult {
  const text = input.toLowerCase();
  const pii = /(?:\d[ -]*?){13,19}/.test(input);
  const balance = /balance|checking|savings/.test(text);
  const transactions = /transaction|recent|spent|last 5/.test(text);
  if (pii) return { answer: "I removed the card number before processing your message. No banking tool was called. For card support, use the secure service channel.", agents: ["Safety policy"], tools: [], pii: true };
  if (balance && transactions) return { answer: "Your mock Everyday Checking balance is $8,420.17. Your five most recent synthetic transactions total $214.38, led by Lakeside Market at $86.42.", agents: ["Accounts agent", "Transactions agent"], tools: ["accounts.get_balance", "transactions.list_recent"], pii: false };
  if (balance) return { answer: "Your mock Everyday Checking balance is $8,420.17, with $8,120.17 available. Data timestamp: today at 9:42 AM.", agents: ["Accounts agent"], tools: ["accounts.get_balance"], pii: false };
  if (transactions) return { answer: "Here are your latest synthetic transactions: Lakeside Market −$86.42, Metro Energy −$64.90, Northstar Coffee −$18.60, CloudStream +$12.00, and City Transit −$56.46.", agents: ["Transactions agent"], tools: ["transactions.list_recent"], pii: false };
  if (/statement/.test(text)) return { answer: "Your mock May statement is ready. Reference STM-MAY-2026-1042 was created; no real document or account was accessed.", agents: ["Transactions agent"], tools: ["transactions.request_statement"], pii: false };
  if (/cheque|check book|checkbook/.test(text)) return { answer: "A mock cheque book request was created for the address ending in “Lake Drive.” Reference SR-20481. Nothing will be mailed.", agents: ["Service agent"], tools: ["service.request_cheque_book"], pii: false };
  if (/address|move/.test(text)) return { answer: "Address changes require a second confirmation in this demo. The service agent prepared a mock change request but did not commit it.", agents: ["Service agent"], tools: ["service.prepare_address_change"], pii: false };
  return { answer: "I can help with balances, recent transactions, statements, cheque books and address-change requests using synthetic data only.", agents: ["Coordinator"], tools: [], pii: false };
}

async function resolvePrompt(input: string): Promise<DemoResult> {
  if (!API_BASE_URL) return classify(input);
  try {
    const response = await fetch(`${API_BASE_URL}/v1/chat`, {
      method: "POST",
      headers: { "Authorization": "Bearer mock-demo-token", "Content-Type": "application/json" },
      body: JSON.stringify({ message: input, session_id: "portfolio-demo" }),
    });
    if (!response.ok) throw new Error(`Coordinator returned ${response.status}`);
    const payload = await response.json() as { answer: string; agents: string[]; tools: string[]; redacted_input: string; request_id: string };
    return { answer: payload.answer, agents: payload.agents, tools: payload.tools, pii: payload.redacted_input !== input, requestId: payload.request_id.toUpperCase() };
  } catch {
    return classify(input);
  }
}

export default function BankingConsole() {
  const initial: Message[] = [{ role: "assistant", text: "Good morning, Alex. I’m Nova, your secure mock banking assistant. What would you like to explore?" }];
  const [messages, setMessages] = useState<Message[]>(initial);
  const [input, setInput] = useState("");
  const [selectedStep, setSelectedStep] = useState(14);
  const [traces, setTraces] = useState<Trace[]>([
    { label: "Identity", detail: "demo-user · verified", state: "complete" },
    { label: "Policy", detail: "retail:read · allowed", state: "complete" },
    { label: "Coordinator", detail: "waiting for a request", state: "waiting" },
  ]);
  const [requestId, setRequestId] = useState("REQ—READY");
  const localRequestSequence = useRef(0);
  const step = architectureSteps[selectedStep - 1];
  const toolCount = useMemo(() => traces.filter((trace) => trace.label === "Tool call").length, [traces]);

  async function submit(value?: string) {
    const prompt = (value ?? input).trim();
    if (!prompt) return;
    const result = await resolvePrompt(prompt);
    localRequestSequence.current += 1;
    setRequestId(result.requestId ?? `REQ—LOCAL${String(localRequestSequence.current).padStart(3, "0")}`);
    setMessages((current) => [...current, { role: "user", text: result.pii ? prompt.replace(/(?:\d[ -]*?){13,19}/g, "[CARD REDACTED]") : prompt }, { role: "assistant", text: result.answer }]);
    setTraces([
      { label: "Edge", detail: "rate limit · passed", state: "complete" },
      { label: "Identity", detail: "demo-user · verified", state: "complete" },
      { label: "PII guard", detail: result.pii ? "card pattern · redacted" : "no sensitive pattern", state: "complete" },
      { label: "Coordinator", detail: result.agents.join(" + "), state: "complete" },
      ...result.tools.map((tool) => ({ label: "Tool call", detail: `${tool} · 200`, state: "complete" as const })),
      { label: "Response", detail: "policy filtered · delivered", state: "active" },
    ]);
    setInput("");
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void submit();
  }

  return (
    <main>
      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="Aegis Bank AI home"><span className="brand-mark" aria-hidden="true">A</span><span>Aegis <b>Bank AI</b></span></a>
        <div className="nav-links"><a href="#demo">Live demo</a><a href="#evolution">Architecture</a><a href="#trust">Trust model</a><a className="github-link" href="https://github.com/vendra020-art/secure-multi-agent-banking-assistant" target="_blank" rel="noreferrer">View repository ↗</a></div>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> Enterprise AI reference architecture</p>
          <h1>See a secure banking assistant <em>think.</em></h1>
          <p className="hero-lede">A working, mock-first multi-agent system that makes routing, tool use and guardrails visible—without touching a real bank, customer or model.</p>
          <div className="hero-actions"><a className="primary-button" href="#demo">Try the safe demo <span>↓</span></a><a className="text-link" href="#evolution">Explore all 14 layers →</a></div>
          <div className="trust-row" aria-label="Project guarantees"><span><i>✓</i> Synthetic data</span><span><i>✓</i> Local services</span><span><i>✓</i> No external LLM</span></div>
        </div>
        <div className="hero-visual" aria-label="Architecture summary">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          <div className="core-card"><span className="core-kicker">Coordinator</span><strong>One request.<br />The right agents.</strong><span className="pulse"><i /> Policy checked</span></div>
          <div className="satellite sat-one"><span>01</span> Accounts</div><div className="satellite sat-two"><span>02</span> Transactions</div><div className="satellite sat-three"><span>03</span> Service</div>
          <div className="edge-label">EDGE · AUTH · PII · TRACE</div>
        </div>
      </section>

      <section className="demo-section" id="demo">
        <div className="section-heading"><div><p className="eyebrow dark"><span /> Interactive system</p><h2>Ask the bank. Watch the system respond.</h2></div><p>Every answer includes a transparent execution trace. The experience is real; the identity, accounts, tools and costs are deliberately mocked.</p></div>
        <div className="console">
          <section className="chat-panel" aria-label="Banking assistant chat">
            <header className="panel-header"><div className="assistant-avatar">N</div><div><strong>Nova</strong><span><i /> Secure mock assistant</span></div><button className="icon-button" aria-label="Start a new conversation" onClick={() => setMessages(initial)}>↻</button></header>
            <div className="messages" aria-live="polite">{messages.map((message, index) => <div className={`message ${message.role}`} key={`${message.role}-${index}`}>{message.role === "assistant" && <span className="mini-avatar">N</span>}<p>{message.text}</p></div>)}</div>
            <div className="suggestions" aria-label="Example requests">{starters.slice(0, 4).map((starter) => <button key={starter} onClick={() => void submit(starter)}>{starter}</button>)}</div>
            <form className="composer" onSubmit={onSubmit}><label className="sr-only" htmlFor="chat-input">Ask Nova a banking question</label><input id="chat-input" value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about your mock accounts…" autoComplete="off" /><button type="submit" aria-label="Send message">↑</button></form>
            <p className="mock-disclaimer">Demo only · No real banking data or external model calls</p>
          </section>
          <aside className="trace-panel" aria-label="Execution trace">
            <header className="trace-header"><div><span className="live-dot" /> Execution trace</div><code>{requestId}</code></header>
            <div className="trace-flow">{traces.map((trace, index) => <div className="trace-item" key={`${trace.label}-${index}`}><span className={`trace-node ${trace.state}`}>{trace.state === "complete" ? "✓" : trace.state === "active" ? "•" : "○"}</span><div><strong>{trace.label}</strong><span>{trace.detail}</span></div>{index < traces.length - 1 && <i className="trace-line" />}</div>)}</div>
            <div className="trace-metrics"><div><span>Agents</span><strong>{traces.some((t) => t.label === "Coordinator" && t.state === "complete") ? Math.max(1, traces.find((t) => t.label === "Coordinator")?.detail.split("+").length ?? 1) : 0}</strong></div><div><span>Tools</span><strong>{toolCount}</strong></div><div><span>Est. cost</span><strong>${toolCount ? "0.0012" : "0.0000"}</strong></div></div>
            <button className="pii-test" onClick={() => void submit(starters[6])}>Run the PII redaction test <span>→</span></button>
          </aside>
        </div>
      </section>

      <section className="evolution" id="evolution">
        <div className="section-heading light"><div><p className="eyebrow"><span /> Architecture evolution</p><h2>Fourteen deliberate layers.<br />One defensible system.</h2></div><p>The design grows from a demo into an enterprise-ready reference architecture. Select a step to see why each layer exists.</p></div>
        <div className="evolution-grid">
          <div className="step-list" role="list" aria-label="Architecture steps">{architectureSteps.map((item) => <button className={selectedStep === item.n ? "selected" : ""} key={item.n} onClick={() => setSelectedStep(item.n)} aria-pressed={selectedStep === item.n}><span>{String(item.n).padStart(2, "0")}</span><b>{item.title}</b>{item.inferred && <em>Bridge</em>}</button>)}</div>
          <article className="step-detail">
            <div className="step-meta"><span>Step {String(step.n).padStart(2, "0")} / 14</span><span>{step.layer}</span></div><h3>{step.title}</h3><p>{step.note}</p>
            <div className="architecture-map" aria-label={`Conceptual diagram for ${step.title}`}><div className="map-edge">Secure edge</div><div className="map-row"><span className="map-client">React client</span><i>→</i><span className="map-coordinator">Coordinator</span></div><div className="map-agents"><span>Accounts agent</span><span>Transactions agent</span><span>Service agent</span></div><div className="map-tools"><span>Mock Accounts MCP</span><span>Mock Transactions MCP</span><span>Mock Service MCP</span></div><div className="map-rails"><span>Identity</span><span>Policy</span><span>Session</span><span>PII</span><span>Trace</span><span>Cost</span></div></div>
            <div className="step-footer"><span>{step.inferred ? "Inferred bridge step" : "Source architecture step"}</span><code>architecture/step-{String(step.n).padStart(2, "0")}.md</code></div>
          </article>
        </div>
      </section>

      <section className="trust-section" id="trust">
        <div className="trust-intro"><p className="eyebrow dark"><span /> Built to explain</p><h2>Real boundaries.<br /><em>Zero real banking.</em></h2><p>The project is credible because its integration contracts, failure modes and controls are implemented—while every risky external dependency is replaced by a deterministic local adapter.</p></div>
        <div className="trust-cards"><article><span>01</span><h3>Real connection code</h3><p>Typed HTTP clients, timeouts, correlation IDs and error mapping connect the coordinator to three isolated services.</p><b>FastAPI · HTTPX · Pydantic</b></article><article><span>02</span><h3>Mock-first by design</h3><p>Customers, balances, identity, transactions and model responses are synthetic, local and resettable.</p><b>No credentials · No vendors</b></article><article><span>03</span><h3>Observable and testable</h3><p>Routing, authorization, redaction, tools and multi-agent plans ship with unit and evaluation cases.</p><b>Pytest · Eval fixtures · CI</b></article></div>
      </section>
      <footer><div className="brand"><span className="brand-mark">A</span><span>Aegis <b>Bank AI</b></span></div><p>Secure multi-agent banking assistant · Portfolio reference project</p><span>Mock data only · 2026</span></footer>
    </main>
  );
}
