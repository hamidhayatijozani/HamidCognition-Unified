# Action Gate Commercial Product Specification

Version: 0.4.2
Product: HamidCognition Action Gate
Originator: Hamid Hayati Jozani

## Product definition
Action Gate is a policy-enforcement runtime that evaluates an action before execution, binds the authorization decision to tenant/actor/session/action identity, records signed evidence, and permits execution only across an accepted enforcement boundary.

Current executable decisions: ALLOW, DENY, ASK, SANDBOX. DEFER is not part of the current executable policy surface.

## Customer value
The product provides a separately deployable control point between an agent and a tool, with evidence and replay rather than a simple allow/deny boolean.

## Validated v0.4.2 boundary
Evidence covers production authentication, tenant isolation, actor/session binding, signed decisions, nonce-based single use, HTTP and MCP enforcement, fail-closed evidence recording, persistent PostgreSQL operation, production Compose startup, end-to-end smoke, 200-event decision replay, restart/persistence replay, and validation evidence packaging.

These are engineering validation claims for the tested boundary, not a guarantee that every customer policy or downstream action is safe.

## Deployment contract
Customer deployment must provide a protected gate endpoint, production authentication, signing secret/keyring configuration, persistent production storage, an enforcement integration that cannot bypass the gate, customer policy configuration, and appropriate monitoring/backups.

## Commercial boundary
The commercial product must distinguish software supplied by HamidCognition, customer policy/data, third-party dependencies, integration work, and support/SLA obligations.

No claim of universal policy correctness, legal compliance, or downstream business safety is made by this specification.
