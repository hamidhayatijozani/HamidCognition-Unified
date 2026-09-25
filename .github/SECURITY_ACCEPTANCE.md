# Security Acceptance Verification

This document makes the protected-tool acceptance boundary explicit in repository history.

The CI gate covers:
- direct execution without X-Action-Gate-Authority
- authority replay and one-time nonce consumption
- tenant binding tampering
- action binding tampering
- policy binding tampering
- expired authority
- concurrent reuse of the same nonce
- AST coverage of protected FastAPI routes

The reference protected tool is intentionally side-effect-free. Production integrations must place the same enforcement dependency at the actual side-effect boundary and use downstream idempotency or transaction semantics where exactly-once effects are required.
