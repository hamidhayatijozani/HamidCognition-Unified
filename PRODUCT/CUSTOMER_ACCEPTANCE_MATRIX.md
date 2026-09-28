# Action Gate Customer Acceptance Matrix

## Purpose

This document defines the minimum reproducible acceptance evidence for a customer deployment of HamidCognition Action Gate.

Acceptance is tied to the exact product release, source commit, deployment configuration, and observed test results. A running container or a passing unit-test suite alone is not acceptance evidence.

## Release binding

Record these values before testing:

| Field | Value |
|---|---|
| Product | HamidCognition Action Gate |
| Product version | exact deployed release |
| Git release/tag | exact release tag |
| Source commit | exact source commit |
| Container/image digest | exact deployed digest, when available |
| Policy fingerprint | exact deployed policy fingerprint |
| Acceptance date | UTC timestamp |
| Customer environment | environment identifier |
| Operator | responsible tester |

## Acceptance matrix

| ID | Control | Test | Expected result | Evidence |
|---|---|---|---|---|
| AG-01 | Service health | Query production health endpoint | Healthy service reports the expected persistent storage backend | Response capture |
| AG-02 | Authentication | Call protected endpoint without credentials | Request is rejected | HTTP response |
| AG-03 | Identity binding | Submit action with tenant/actor/session context | Decision is bound to the supplied identity context | Decision record |
| AG-04 | ALLOW | Evaluate an allowed action | Decision is ALLOW | Decision + evidence |
| AG-05 | DENY | Evaluate a prohibited action | Decision is DENY and protected tool is not executed | Decision + execution absence |
| AG-06 | ASK | Evaluate an approval-required action | Decision is ASK until valid approval is supplied | Decision + approval evidence |
| AG-07 | SANDBOX | Evaluate a sandboxed action | Action remains constrained to the sandbox boundary | Decision + execution evidence |
| AG-08 | Decision integrity | Verify decision signature and action/policy binding | Integrity checks pass | Evidence/replay response |
| AG-09 | Tenant isolation | Read evidence using another tenant identifier | Other tenant cannot retrieve the decision | HTTP response |
| AG-10 | Single-use authority | Execute the same authorized action twice | First execution succeeds; replayed execution is rejected | Execution records |
| AG-11 | Expiry | Attempt execution after decision/authority expiry | Expired authority is rejected | HTTP response + evidence |
| AG-12 | Direct bypass | Call the protected tool without Gate-issued authority | Protected tool rejects the request | HTTP response |
| AG-13 | Evidence fail-closed | Trigger an evidence-integrity failure path | Execution is not accepted when required evidence cannot be validated | Failure evidence |
| AG-14 | Persistence | Restart the Action Gate service | Persistent decisions remain available | Before/after evidence |
| AG-15 | Replay | Replay a recorded decision | Replay matches the recorded decision/action/policy state | Replay result |
| AG-16 | HTTP enforcement | Execute through the HTTP enforcement boundary | Execution occurs only with the bound decision | E2E result |
| AG-17 | MCP authentication | Call MCP boundary without valid bearer authentication | Request is rejected | MCP response |
| AG-18 | MCP ALLOW/DENY/EVIDENCE | Run the authenticated MCP E2E harness | ALLOW executes, DENY does not execute, evidence lookup returns the recorded decision | E2E output |
| AG-19 | Restart replay | Replay persisted decisions after service restart | Previously persisted decisions remain reproducible | Replay artifact |
| AG-20 | Configuration integrity | Record deployment secrets/configuration fingerprints without exposing secrets | Deployment can be identified without publishing secret values | Configuration record |

## Acceptance rule

A customer deployment is accepted only when the agreed acceptance cases have recorded:

1. test identifier;
2. exact deployed version;
3. exact source commit or immutable image digest;
4. expected result;
5. actual result;
6. evidence reference;
7. pass/fail outcome.

Any failed mandatory control remains an acceptance blocker until it is corrected and retested.

## Evidence boundary

This matrix establishes evidence for the tested Action Gate authorization, enforcement, persistence, replay, and evidence paths.

It does **not** establish:

- universal AI safety;
- correctness of an upstream agent or policy;
- correctness of downstream business logic;
- regulatory certification;
- infrastructure-wide security;
- customer-specific compliance;
- guaranteed business outcomes.

Decision replay does not replay external world state and does not authorize repeating an external side effect.

## Customer sign-off record

For each deployment, retain the completed matrix together with:

- release/tag;
- source commit;
- image/container digest where applicable;
- policy fingerprint;
- acceptance evidence artifacts;
- known deviations;
- remediation items;
- rollback target;
- customer acceptance decision.

Secrets, private keys, bearer tokens, and customer data must not be placed in this document.
