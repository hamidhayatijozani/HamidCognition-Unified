# Action Gate 12-Minute Demo

## 0:00–2:00 — Show the architecture

Agent → Action Gate → Protected Tool.

Explain that the product governs the transition from an agent decision to a real side effect.

## 2:00–4:00 — Normal authorization

Submit a representative action.

Show:
- tenant;
- actor/session;
- policy;
- decision;
- execution authority.

Execute the protected tool successfully.

## 4:00–6:00 — Direct bypass

Call the protected endpoint without execution authority.

Expected result: **403**.

Key sentence:

"Authentication of the caller is not the authorization boundary. The tool itself requires Gate-issued execution authority."

## 6:00–8:00 — Tampering

Change tenant, action or policy after authorization.

Expected result: **403**.

Show that the authorization is bound to the execution context.

## 8:00–10:00 — Replay

Submit the same authority twice.

First request: accepted.

Second request: rejected as nonce reuse.

## 10:00–12:00 — Evidence

Show the decision/evidence record and acceptance test.

Close with:

"We are not asking you to trust a claim. We are asking you to run the acceptance test against the tool you actually care about."
