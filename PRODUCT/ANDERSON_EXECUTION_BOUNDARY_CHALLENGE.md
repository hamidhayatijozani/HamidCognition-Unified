# Anderson Execution Boundary Challenge

## Purpose

A reproducible adversarial test proposal for one real MCP/tool workflow. This is a test definition, not a claim that an external workflow has already passed.

## Attack cases

1. Replay a valid execution authority.
2. Change the action after authorization.
3. Change tenant identity after authorization.
4. Change actor/session context after authorization.
5. Use an expired authority.
6. Race concurrent requests using the same authority/nonce.
7. Change the policy binding/digest.
8. Attempt direct protected-tool access without Gate-issued authority.
9. Cause evidence reservation/persistence failure before execution.
10. Restart the protected service and retry a consumed authority.

## Expected invariant

No consequential tool effect crosses the protected execution boundary unless the exact action, tenant, actor/session context, policy binding, valid execution authority, expiry/nonce state, and required evidence remain valid.

## Evidence required

For every attack: request/input fingerprint, decision identifier, expected result, observed result, tool-side effect indicator, evidence record, replay record, source/release identifier, and execution timestamp.

## Current status

TEST DEFINITION = READY
EXTERNAL MCP WORKFLOW = NOT VERIFIED
CUSTOMER DEPLOYMENT = NOT VERIFIED
DAVID OUTREACH = BLOCKED UNTIL FINAL PRE-OUTREACH GATE
