# Action Gate Commercial Readiness

Evidence snapshot: 2026-11-07 (UTC)

## Current source identity

Current `main` head observed from GitHub:
- SHA: `deafc1d233cb955768e01d85af5ce3398484c235`
- Latest observed commit: `BESAZ: record innovation sandbox report`

The published Action Gate v1.1.1 artifact remains a historical release and is not asserted to contain current-main changes.

## Current pilot-hardening work

### PR #258 — open
`fix(pilot): isolate Render secrets and durable Action Gate plans`

- Base: `main` at `e9f95774759e338a1f6de6acfc0c1658b7080374`
- Head: `b3d70799efe264acc62725960a92b3c94f85d73d`
- Status: OPEN, MERGEABLE, NOT MERGED
- Scope: isolate Render secret groups, use paid starter compute for the five Action Gate services, use paid basic_256mb Action Gate PostgreSQL, and add regression tests.
- GitHub Actions observed on the exact PR head: 16 completed workflow runs, all with conclusion `success`.
- The observed Product Gates run includes real HTTP enforcement, real MCP enforcement, PostgreSQL audit checks, 200-event replay, restart-and-replay, customer console E2E, and production-stack checks.
- No Render service, database, public endpoint, customer environment, customer acceptance, payment, or revenue is established by this PR.

### PR #257 — open
`security: make autonomous repair contents read-only`

- Status: OPEN but currently `mergeable=false`.
- Change: reduce GitHub Actions repository contents permission from write to read for the autonomous repair workflow.
- This remains an independent security hardening change and has not been merged.

### PR #256 — open
Superseded in practical scope by the current-main-based PR #258. Its historical CI evidence is not transferred to the newer head.

## Acceptance evidence

The current repository contains a limited-pilot runbook at
`docs/ACTION_GATE_PILOT_OPERATIONS_RUNBOOK.md`.

The runbook requires, on the actual pilot host:

1. PostgreSQL health and Action Gate health;
2. ALLOW and DENY enforcement;
3. missing/expired/wrong-tenant/wrong-action/stale-world/reused-nonce rejection;
4. HTTP/MCP parity;
5. PostgreSQL persistence after restart and audit UPDATE/DELETE rejection;
6. fail-closed access control;
7. rollback and credential revocation;
8. a retained redacted evidence bundle.

The runbook explicitly states that green CI is not a substitute for target-host evidence.

## Known deployment boundary

The repository's production Compose path has automated CI evidence for the controlled container stack, including PostgreSQL persistence/replay and enforcement checks. A real externally reachable deployment, TLS/DNS endpoint, and customer-host acceptance run remain unverified.

The protected tool currently uses a separate SQLite nonce registry on persistent `tool_data`. The runbook therefore limits the pilot to one protected-tool instance and prohibits claims of multi-replica nonce consistency.

## Commercial boundary

Proposed limited pilot:
- price: 2,500 USDT fixed for 30 days;
- scope: one customer-selected HTTP or MCP tool;
- environment: controlled, isolated, reversible test actions.

This is a proposed offer, not evidence of a customer, contract, payment, or revenue.

## Current Go / No-Go

**NO-GO for production customer execution.**

**Eligible:** restricted technical evaluation after the deployment contract is reviewed, the paid Render resources are explicitly approved, an immutable release artifact is produced from the accepted source SHA, and the full acceptance matrix is executed on the actual pilot host.

**Not claimed:** public production deployment, customer acceptance, revenue, certification, universal AI safety, multi-replica nonce coordination, or external-world replay.

## Delivery package still required

1. immutable release tag + artifact + checksum;
2. secret-free deployment/policy templates;
3. integration/API contract;
4. security boundary + limitations;
5. pilot operations/rollback runbook;
6. customer acceptance matrix + raw evidence;
7. written pilot licence/scope;
8. delivery/entitlement record.
