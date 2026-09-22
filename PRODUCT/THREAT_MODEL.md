# Action Gate Threat Model

## Assets

Authorization decisions, tenant isolation, actor/session identity, policy snapshots and hashes, evidence and replay records, execution nonces, signing material, and downstream tool access.

## Threats and controls

### Decision tampering
Control: Gate-issued execution authority binds decision ID, tenant, action digest, policy digest, nonce, decision and expiry; the downstream tool verifies that authority before accepting a call.

### Cross-tenant or cross-actor substitution
Control: tenant/actor/session binding and execution-time identity checks.

### Replay
Control: one-time nonce consumption and expiry.

### Evidence persistence failure
Control: evidence reservation/persistence before protected production execution and fail-closed behavior.

### Direct bypass
Control: production topology separates edge/backend networks, the tool is not host-published, and the tool rejects calls without Gate-issued execution authority. The production E2E suite includes a direct-tool negative control.

### Policy drift
Control: policy version, snapshot, and policy hash are bound to the decision.

### Credential exposure
Control: production secrets remain external to source control and are injected at deployment.

## Residual risk

Action Gate does not prove customer policy correctness, downstream tool safety, or customer infrastructure integrity. Those remain explicit deployment responsibilities.
