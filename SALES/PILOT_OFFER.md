# Action Gate 30-Day Pilot Offer

## Offer

**Standard scoped pilot: USD $2,500 fixed for 30 days.**

This price applies to the narrow scope below: one customer-selected HTTP/MCP tool, one controlled test environment, agreed acceptance cases, deployment assistance and a reproducible evidence package. Any scope or price variation requires a separate written quote before work begins.

## Objective

Deploy Action Gate around one customer-selected consequential agent tool or MCP server and produce reproducible evidence for the agreed execution-boundary tests.

## Scope

### Week 1 — Integration
- identify one protected tool;
- map tenant / actor / session / action identity;
- connect the tool to the Action Gate enforcement boundary;
- define ALLOW / DENY / ASK / SANDBOX policy cases.

### Week 2 — Security acceptance
- direct-access rejection;
- expired authority rejection;
- replay rejection;
- tenant tampering rejection;
- action/policy tampering rejection;
- concurrent nonce race testing;
- restart/persistence validation.

These are proposed acceptance cases. A case is not a verified result until it has actually run and its raw outcome is retained.

### Week 3 — Operationalization
- production-like deployment within the agreed test scope;
- persistent database;
- secret separation;
- audit/evidence review;
- operational runbook;
- rollback procedure.

### Week 4 — Customer acceptance
Deliver:
- deployed integration within agreed scope;
- per-case test report, including failures and untested cases;
- acceptance evidence;
- configuration/policy snapshot;
- exact release/commit identifiers;
- known limitations;
- production recommendation.

## Customer responsibilities

The customer supplies:
- one target tool or MCP service;
- controlled test environment;
- required identities and access;
- representative policy cases;
- technical owner;
- acceptance criteria for the protected workflow.

## Success criteria

The pilot is successful when the agreed acceptance suite passes in the customer's deployment and the customer receives reproducible evidence of the tested controls. A failed test is reported as a failure, not hidden or reclassified as a pass.

## Exclusions

No organization-wide deployment, compliance certification, universal attack-prevention guarantee, downstream business-correctness guarantee, unrestricted custom development or production SLA is included.

## Commercial conversion

After acceptance, the customer may continue as:
- SELF_HOSTED software/support;
- MANAGED service;
- ENTERPRISE integration and support.

## Payment and release truth

The quote must identify the exact release/tag and checksum. Payment route, settlement evidence, license and entitlement must be recorded separately. Technical release evidence does not establish a customer transaction or revenue.
