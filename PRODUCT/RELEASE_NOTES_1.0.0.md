# HamidCognition Action Gate v1.0.0

## Production release

Action Gate v1.0.0 establishes the production decision and execution authority boundary for the runtime.

### Included authority controls

- Actor and session identity binding from request through execution.
- Cryptographically bound production approvals.
- Decision signatures with key-rotation and historical-key verification.
- One-time execution nonce protection and replay validation.
- PostgreSQL-backed persistence and audit-chain handling.
- HTTP and MCP enforcement paths.
- Versioned policy snapshots with deterministic policy hashes.
- Dependency-free Python SDK for the core HTTP contract.
- Production self-audit and meta-validation coverage.
- Explicit production requirements for signing and approval secrets.

### Evidence boundary

This release note records the product version and scope. A release is not considered clean-room verified merely because the workflow definition exists. Clean-room execution, its run identity, and its evidence artifact must be observed separately.

### Explicit nonclaims

This release does not claim universal safety, downstream action correctness, HSM/KMS custody, external identity federation, SIEM integration, or HA orchestration as built-in product capabilities. Those remain deployment-specific controls unless separately evidenced.

