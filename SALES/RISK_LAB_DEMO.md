# Agent Action Risk Lab — Buyer Demo

## The five-minute proof

The demo asks one question:

**Can the protected tool itself reject an action that does not carry valid execution authority?**

### Step 1 — Baseline

Run a harmless representative tool action without Action Gate.

Record exactly what happens.

### Step 2 — Governed execution

Send the same action through Action Gate.

Show:

- decision;
- tenant;
- actor/session;
- policy binding;
- execution authority;
- protected-tool response.

### Step 3 — Break the authority

Change one element after authorization:

- action;
- tenant;
- policy;
- expiry;
- nonce.

Expected governed result: rejection.

### Step 4 — Replay

Submit the same authority twice.

Expected:

- first execution: accepted when policy permits;
- second execution: rejected as replay.

### Step 5 — Bypass

Call the protected endpoint directly without Gate-issued authority.

Expected: rejection when the enforcement contract is active.

## The customer takeaway

Do not ask the buyer to trust a security claim.

Show the exact request, the exact protected endpoint, the exact response, and the reproducible evidence.

The paid pilot begins only when the customer chooses a real tool to protect.
