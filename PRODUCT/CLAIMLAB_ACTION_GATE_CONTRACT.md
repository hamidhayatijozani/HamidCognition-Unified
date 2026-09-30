# ClaimLab ↔ Action Gate Contract

Status: normative integration boundary

## Scope

ClaimLab is the evidence and epistemic-assessment layer. Action Gate is the execution-authorization layer. ClaimLab verdicts MUST NOT directly authorize execution.

## Verdict semantics

- VALID: evidence record satisfies ClaimLab's current assessment rules. Informational only.
- WEAK: support exists but does not satisfy the current validation threshold. Informational only.
- INVALID: current evidence contradicts the claim under ClaimLab rules. Informational only.
- UNKNOWN: evidence is insufficient or absent. MUST NOT be converted to an automatic policy or permission.
- OVERCLAIM: the claim strength exceeds the recorded evidence. MUST NOT be converted to an automatic permission.

## Action Gate boundary

If a future integration consumes ClaimLab output, it MUST pass through an explicit adapter that maps an evidence assessment into Action Gate input fields. The adapter MUST preserve:

1. claim_id and assessment fingerprint;
2. evidence coverage and evidence-quality components;
3. epistemic state and unknown_reason;
4. evidence identifiers and source provenance;
5. assessment timestamp/version;
6. the exact Action Gate decision context used for authorization.

The adapter MUST NOT map VALID to ALLOW by itself. Action Gate remains authoritative for execution authorization and applies its own policy, authority, state, nonce, and execution-integrity checks.

UNKNOWN, UNRESOLVED, OVERCLAIMED, and missing provenance are fail-closed inputs for any future high-impact integration.

## Producer integration status

The current repository contains the structured SignalSnapshot model and a tested HTTP/PostgreSQL ingestion path. The CI payload is synthetic test data. No canonical production P/S/T producer endpoint has been verified in this repository, so ClaimLab MUST NOT claim direct production-engine ingestion yet.

The next producer adapter should consume the canonical producer's structured SignalSnapshot object rather than scrape free-form text. It should include producer identity, producer version/commit, timestamp, and a stable source event ID so replay and provenance remain deterministic.

## Security

POST /evidence requires X-ClaimLab-API-Key. The secret is supplied through CLAIMLAB_API_KEY and MUST NOT be committed to source control. Render declares this variable as a secret placeholder.
