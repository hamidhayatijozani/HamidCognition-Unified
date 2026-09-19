# Customer Acceptance Smoke Test

`PRODUCT/customer_acceptance_smoke.py` is a dependency-free, non-destructive smoke test for a deployed Action Gate instance.

It verifies one complete governed path using the inert `example.read_only_check` action:
1. health and product version are readable;
2. an authenticated action is evaluated;
3. the decision contains identity, nonce, action hash, and policy fingerprint;
4. the inert action is ALLOWed;
5. execution reservation succeeds;
6. execution is recorded;
7. evidence is retrievable;
8. replay returns `match=true`.

This does not replace the complete procedure in `PRODUCT/CUSTOMER_ACCEPTANCE.md`. It is the fast first-pass deployment smoke test.

Run against an acceptance deployment:

```bash
 ACTION_GATE_URL=http://localhost:8080 ACTION_GATE_API_TOKEN='...' python3 PRODUCT/customer_acceptance_smoke.py
```

The JSON result can be retained with version, commit/image digest, policy hash, evidence hash, and timestamp. The script does not intentionally invoke an external side effect.
