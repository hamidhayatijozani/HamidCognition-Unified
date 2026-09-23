# Action Gate 90-Second Demo

This demo runs against the real Action Gate HTTP API. It is intended for screen recording from Termux or any terminal.

## What the recording shows

1. **ALLOW** — ordinary read action.
2. **ASK** — external customer email requiring human approval.
3. **DENY** — destructive action against a production target.

Each decision prints the risk level, policy result, decision signature, decision ID, and replay endpoint.

The demo does **not** invent NED, HAIS, or DRS values. Those metrics are not part of the current Action Gate API response. The recording therefore shows the actual product contract instead of a prettier fiction, which is an unfortunately useful distinction.

## Run

From the repository root:

```bash
cd action_gate
python demo.py
```

Or, if the service is already running elsewhere:

```bash
ACTION_GATE_URL=http://127.0.0.1:8000 python demo.py
```

For an authenticated deployment:

```bash
ACTION_GATE_URL=https://YOUR-GATE-HOST ACTION_GATE_API_TOKEN=YOUR_TOKEN python demo.py
```

## Recording target

Keep the terminal full-screen and record one continuous run. The script is paced for a short product demo and should fit comfortably inside 90 seconds on a normal local deployment.

Suggested narration:

> An AI agent proposes an action. Action Gate evaluates it against a versioned policy, records a signed decision, and exposes replayable evidence.
>
> A normal read is allowed.
>
> An external communication requires human approval.
>
> A destructive production action is denied.
>
> The important part is that the decision is not just printed. It is bound to the action, policy, nonce, tenant, and signature, and it can be replayed.

## Video

**Status:** not recorded yet.

Replace this line after recording:

`VIDEO: <public video URL>`

## Important product-boundary note

The current shipped policy classifies `transfer_funds` as `SANDBOX`, not `DENY`. The demo intentionally uses a real `DENY` scenario so the three-state recording is ALLOW / ASK / DENY without falsifying the current implementation.

No decision is claimed to be objectively correct or safe. The gate records, constrains, and enforces a decision under its configured policy and available evidence.
