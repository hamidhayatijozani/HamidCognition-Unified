# HamidCognition Financial Controlled Runtime

This module applies the HamidCognition execution-governance model to financial reconciliation and accounting automation.

It is not an accounting-product connector. It provides the controlled runtime between normalized financial evidence and a destination adapter.

Execution model:

Observe -> Normalize -> Match -> Reason -> Decide -> Authorize -> Execute -> Verify -> Evidence

Core separation:

Reasoning != Authorization != Execution != Verification

Decision states:

- ALLOW: exact evidence and policy permit the operation.
- DENY: policy or prior execution blocks the operation.
- ASK: ambiguity requires human review.
- SANDBOX: reserved for non-production simulation or containment.
- DEFER: required evidence is incomplete.

Execution states:

- PLANNED
- AUTHORIZED
- DISPATCHED
- UNKNOWN
- FAILED
- VERIFIED

UNKNOWN is deliberate. A timeout after dispatch does not prove that the destination rejected the operation. The runtime must not blindly retry an operation whose external state is unknown.

Deterministic matching handles exact evidence such as amount, currency and reference. Heuristic or AI matching may rank ambiguous candidates, but a similarity score is never an authorization signal.

Each operation receives a deterministic operation hash before dispatch. The current implementation uses an in-memory vault for testability. Production deployment requires a durable transactional store.

Each execution produces structured evidence containing source events, candidates, decision, execution state, destination and verification result.

Future adapters should implement name, execute(event, candidate), and verify(execution). Adapters for Asan, Sepidar and bank sources must be implemented only after their actual integration surface is verified.

Non-claims: this module does not claim zero error, regulatory compliance, accounting correctness independent of source data, or support for Asan/Sepidar without verified adapters.
