import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("renders the Aegis banking assistant experience", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /Aegis Bank AI/);
  assert.match(html, /See a secure banking assistant/);
  assert.match(html, /Execution trace/);
  assert.match(html, /Architecture evolution/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton/);
});

test("publishes mock-first and safety disclosures", async () => {
  const response = await render();
  const html = await response.text();
  assert.match(html, /Synthetic data/);
  assert.match(html, /No external LLM/);
  assert.match(html, /PII redaction test/);
  assert.match(html, /Demo only/);
  assert.equal(response.headers.get("x-content-type-options"), "nosniff");
  assert.equal(response.headers.get("x-frame-options"), "DENY");
  assert.match(response.headers.get("content-security-policy") ?? "", /frame-ancestors 'none'/);
});
