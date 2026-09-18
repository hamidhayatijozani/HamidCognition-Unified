# Action Gate Threat Model

## Assets

Authorization decisions, tenant isolation, actor/session identity, policy snapshots and hashes, evidence and replay records, execution nonces, signing material, and downstream tool access.

## Threats and controls

### Decision tampering
Control: decision signature, action hash, policy hash, nonce, expiry, and verification before execution.

### Cross-tenant or cross-actor substitution
Control: tenant/actor/session binding and execution-time identity checks.

### Replay
Control: one-time nonce consumption and expiry.

### Evidence persistence failure
Control: evidence reservation/persistence before protected production execution and fail-closed behavior.

### Direct bypass
Control: deployment architecture must place the enforcement adapter on the production path with no alternate direct route.

### Policy drift
Control: policy version, snapshot, and policy hash are bound to the decision.

### Credential exposure
Control: production secrets remain external to source control and are injected at deployment.

## Residual risk

Action Gate does not prove customer policy correctness, downstream tool safety, or customer infrastructure integrity. Those remain explicit deployment responsibilities.
