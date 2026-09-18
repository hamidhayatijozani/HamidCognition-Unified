# Action Gate Integration Contract

## Caller contract

Every protected action request should carry stable identity context:

- tenant_id
- actor_id
- session_id
- action/tool identity
- request nonce
- policy-relevant arguments
- correlation/trace identifier

The caller must treat the returned decision as authoritative only for the exact request identity and nonce for which it was issued.

## Decision handling

Current executable policy surface:

- ALLOW: may proceed through the validated execution boundary.
- DENY: must not execute.
- ASK: must not execute until the required authorization path completes.
- SANDBOX: may execute only inside an explicitly non-production sandbox boundary.

DEFER is not part of the current executable policy surface.

## Non-bypass rule

The integration must not contain an alternate direct path to the downstream production tool. A gate that can be bypassed is a decorative traffic cone, and software has enough decorative objects already.

## Failure handling

If Action Gate cannot authenticate, evaluate, reserve evidence, or persist a required decision record, the protected production action must fail closed.

## Replay

Customer acceptance should retain:

- Action Gate version/commit
- request identity
- decision
- nonce
- evidence identifier
- execution outcome
- timestamps
- policy/configuration fingerprint

## Example request

tenant_id=tenant-demo
actor_id=actor-demo
session_id=session-demo
action=example.protected_action
nonce=single-use-request-id
trace_id=trace-demo

This example contains no credentials and is not a production policy.
