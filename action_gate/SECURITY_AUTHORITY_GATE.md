# Security & Authority Gate

This gate establishes executable authority binding before Action Gate execution.

## Acceptance invariants

- **Decision binding:** an authority is bound to one canonical action digest and policy digest.
- **Forgery resistance:** invalid signatures are denied.
- **Expiration:** authorities outside their validity interval are denied.
- **Tenant isolation:** an authority issued for tenant A cannot authorize tenant B.
- **Replay resistance:** a nonce cannot be consumed twice by the same verifier state.
- **Authorization matrix:** only `ALLOW` and `SANDBOX` can become executable authority.
- **Canonical digest:** JSON serialization is deterministic (`sort_keys`, fixed separators, UTF-8).

## Explicit boundary

This gate proves authority-token integrity and binding. It does **not** prove world-state replay, distributed nonce persistence, cryptographic key rotation, or production-grade identity management. Those remain separate acceptance gates.

## Next production hardening

1. Replace process-local nonce state with durable transactional storage.
2. Introduce asymmetric signing and key rotation for multi-service deployment.
3. Bind authority to authenticated principal/session and deployment environment.
4. Add race/concurrency tests for nonce consumption.
5. Integrate the verifier directly into every HTTP and MCP execution path and add a negative bypass test.
