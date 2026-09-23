# Action Gate 90-Second Demo

This demo runs against the real Action Gate HTTP API and prints the actual verdict, reason, signature, approval state, evidence-chain hashes, and replay reference.

## Scenarios

1. **ALLOW** — ordinary read action.
2. **ASK** — external communication. The API requires human approval. The current `evaluate` response does not contain a separate `approval_request` object, so the demo prints the real approval endpoint and the stored `approval: null` state instead of inventing an object.
3. **DENY** — destructive action against a production target, with the stored evidence chain.

The demo deliberately does not display NED, HAIS, or DRS values because the current API does not expose those metrics.

## Run

```bash
cd action_gate
python demo.py
```

Or:

```bash
ACTION_GATE_URL=http://127.0.0.1:8000 python demo.py
```

For the local authenticated production-style service:

```bash
ACTION_GATE_URL=http://127.0.0.1:8000 ACTION_GATE_API_TOKEN=ci-action-gate-token python demo.py
```

## Recording

Keep the terminal full-screen and record one continuous run. The script is paced for a short product demo.

Suggested narration:

> An AI agent proposes an action. Action Gate evaluates it against a versioned policy, creates a signed decision record, and exposes replayable evidence.
>
> A normal read is allowed.
>
> An external communication pauses for human approval.
>
> A destructive production action is denied.
>
> The important part is that the decision is bound to the action and policy, signed, persisted, and replayable.

## Video

**Status:** not recorded yet.

Replace with:

`VIDEO: <public video URL>`

## Product boundary

The shipped builtin policy classifies `transfer_funds` and `transfer_money` as `SANDBOX`, not `DENY`. The demo therefore uses a real `DENY` case instead of falsifying the financial-transfer behavior.

No decision is presented as objectively safe. The gate enforces the configured policy and records the evidence available at decision time.
