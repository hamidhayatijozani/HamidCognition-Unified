# Action Gate Validation Boundary

Status: PROPOSED / ENFORCEMENT-READY
Scope: HamidCognition Action Gate MVP

## 1. Purpose

The Validation Boundary defines the exact claim surface that Action Gate may make from executable evidence. It separates what is validated at the action boundary from claims about model correctness, policy correctness, downstream systems, or production security.

Core invariant:

> No consequential tool effect is considered governed unless the exact action, tenant, actor, policy state, decision, execution authority, and outcome can be joined and verified at the enforcement boundary.

The boundary is intentionally narrower than "AI safety" or "production security". A green CI run is evidence that specified checks executed successfully; it is not evidence that every deployment or every policy is safe.

## 2. Boundary model

`Agent proposal -> Canonical Action -> Identity/Context -> Policy Snapshot -> Decision -> Execution Authority -> Enforcement Point -> Tool Effect -> Outcome -> Evidence -> Replay`

The protected transition is:

`Decision + exact action + valid authority -> permitted execution`

Anything outside this transition is not automatically validated by Action Gate.

## 3. In-boundary claims

Action Gate may claim an item is VALIDATED only when executable evidence demonstrates all applicable predicates:

### VB-01 Canonical action binding

The action identity covers at minimum tenant, actor, action/tool, target, normalized parameters, policy version, and one-time execution nonce. Any material change invalidates the authority.

### VB-02 Decision integrity

The execution path accepts only a Gate-issued decision whose state permits the requested execution. Caller-supplied Decision IDs are references, never authority by themselves.

### VB-03 Complete mediation

The protected tool path cannot execute through an alternate unauthenticated route. Direct tool access without the required enforcement authority must fail closed.

### VB-04 Tenant isolation

Evidence, decisions, approvals, and execution authority are tenant-bound. A principal from tenant B cannot retrieve or redeem tenant A authority merely by changing a tenant identifier.

### VB-05 Actor binding

The actor/workload identity used for evaluation is bound to the decision and execution request. An execution request cannot substitute a different actor without invalidating the authority.

### VB-06 One-time execution

A consumed, expired, revoked, or otherwise non-redeemable authority cannot produce a second side effect.

### VB-07 Attestation integrity

Execution attestation is derived from the exact decision/action/nonce context and is verified at the protected execution boundary. Forged or tampered attestation is rejected.

### VB-08 Fail-closed behavior

When authorization state, evidence binding, identity, attestation, or required Gate communication is unavailable or invalid, the protected path must not execute the consequential action.

### VB-09 Evidence continuity

A decision, execution, and outcome can be correlated into a durable evidence record with sufficient identifiers and hashes to reconstruct the governed transaction.

### VB-10 Replayability

A recorded governed transaction can be replay-checked against its recorded decision inputs and execution state without treating replay as permission to repeat the side effect.

### VB-11 Policy immutability for a decision

A decision is evaluated against a concrete policy snapshot/version and cannot silently inherit a different policy between evaluation and redemption.

### VB-12 Persistence integrity

For production-oriented validation, the durable backend must preserve decision/evidence/audit state across process restart and support the required transaction boundary. PostgreSQL is the target production persistence path; SQLite remains an MVP/development backend.

## 4. Out-of-boundary claims

The following are explicitly NOT established by Action Gate validation:

- that an AI model is truthful, aligned, or generally safe;
- that the policy itself is correct or complete;
- that a human approval is substantively wise;
- that external evidence supplied to a policy is true merely because it is recorded;
- that a permitted action is beneficial or free of downstream harm;
- that all network paths in an arbitrary deployment are mediated;
- that cryptographic key management, IAM, secrets management, TLS, or infrastructure isolation are production-secure unless separately tested;
- that MCP, HTTP, Docker, PostgreSQL, or any other integration is protocol-certified merely because an integration test passes;
- that the MVP is enterprise production-ready;
- that passing CI proves absence of undiscovered vulnerabilities.

## 5. Validation classes

| Class | Required evidence | Status semantics |
|---|---|---|
| V0 Structural | schema/code/test existence | IMPLEMENTED |
| V1 Deterministic | repeated same-input checks | VERIFIED only after execution |
| V2 Adversarial | forged/tampered/bypass/replay tests | VERIFIED only after execution |
| V3 Integration | real HTTP/MCP/tool path | VERIFIED only after execution |
| V4 Persistence | PostgreSQL restart/concurrency/transaction tests | VERIFIED only after execution |
| V5 Deployment | real Compose stack and protected route | VERIFIED only for tested topology |
| V6 Independent reproduction | separate environment/snapshot/run | REQUIRED before broad production claim |

## 6. Acceptance matrix

The minimum Action Gate validation suite is:

1. ALLOW + exact action executes once.
2. DENY never reaches the tool.
3. ASK/approval cannot be bypassed by changing the decision reference.
4. SANDBOX does not imply production execution authority.
5. Altered target is rejected.
6. Altered parameters are rejected.
7. Altered tenant is rejected.
8. Altered actor is rejected.
9. Forged Decision ID is rejected.
10. Forged/tampered attestation is rejected.
11. Replayed nonce/permit is rejected.
12. Expired authority is rejected.
13. Direct tool route without Gate authority is rejected.
14. Gate unavailability fails closed.
15. Evidence is tenant-scoped.
16. Decision/evidence survives persistence restart.
17. Audit chain detects mutation.
18. Replay reconstructs the transaction without replaying the side effect.
19. Production Compose uses PostgreSQL and protected execution path.
20. Evidence pack records commit, workflow run, configuration/input fingerprint, and observed result.

## 7. Proof levels

`PASS` means the specified test execution completed and its expected predicate held.

`VERIFIED` means PASS plus reproducible evidence is retained and the scope is explicit.

`PRODUCTION-READY` is not a synonym for VERIFIED. It requires a separate operational/security review, deployment controls, key management, identity integration, observability, resilience, incident response, and independent testing.

`FAIL` means the predicate was falsified by execution.

`BLOCKED` means the required evidence could not be obtained. BLOCKED must never be converted to PASS by inference.

## 8. Claim boundary statement

> HamidCognition Action Gate is validated only as far as the tested enforcement path demonstrates that a specifically identified action can cross from decision to execution under the required identity, policy, authority, integrity, replay, and evidence conditions. It makes no broader claim about the correctness of the agent, policy, evidence, infrastructure, or resulting real-world outcome.

## 9. Evidence record minimum

Every validation run should retain:

- repository and branch;
- commit SHA;
- workflow/run ID;
- test suite/version;
- environment/topology;
- policy snapshot/version/hash;
- canonical action hash;
- tenant/actor test identity;
- nonce/permit lifecycle result;
- expected predicate;
- observed result;
- artifact/result hash;
- timestamp;
- interpretation and scope limitations.

This document is a validation contract, not a security certification.