# Action Gate Pilot Console

A browser-first evaluation console for the bounded BESAZ / Action Gate pilot.

## Scope and safety

- Static frontend at `webapp/pilot/index.html`; no build toolchain required.
- Optional calls to `/health`, `/v1/action/evaluate`, `/v1/evidence/{decision_id}`, and `/v1/replay/{decision_id}`.
- Local JSON/JSONL evidence import is for inspection only. It does not validate signatures or hash chains.
- The UI does not implement enforcement, authentication, nonce storage, policy decisions, or tamper-proof evidence. Those must be enforced by the server.
- API token stays in page memory and is not persisted by this UI. Use only over HTTPS, with an isolated pilot tenant and reversible test actions.
- The frontend uses `credentials: omit`, `cache: no-store`, and `redirect: error`. Configure server-side CORS and authentication. Never expose internal database/tool ports.
- Do not enter production credentials or connect irreversible actions.

## Open locally

Open `index.html` in a modern browser. For browser API calls, serve it from a trusted HTTPS origin (or localhost) and configure the API's CORS allowlist. Some browsers restrict fetch behavior from `file://`.

## Pilot acceptance

This UI is not proof of a deployed endpoint. Before a pilot, follow [the operations runbook](../../docs/ACTION_GATE_PILOT_OPERATIONS_RUNBOOK.md): verify real-host health with PostgreSQL backend, HTTP/MCP parity, denied-action no-side-effect, stale/replayed authority rejection, evidence integrity, restart persistence, rollback, and credential revocation. Capture redacted raw evidence tied to the exact commit and host.

## Validation boundary

This change adds static frontend files only. It does not claim a production deployment, browser automation pass, customer acceptance, or revenue. Exact-head CI and manual API integration checks must be observed separately.
