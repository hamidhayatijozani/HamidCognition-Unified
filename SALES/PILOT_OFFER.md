# Action Gate 30-Day Pilot Offer

## Objective

Deploy Action Gate around one customer-selected high-impact agent tool or MCP server and produce reproducible evidence that the execution boundary cannot be bypassed through the tested paths.

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

### Week 3 — Operationalization
- production-like deployment;
- persistent database;
- secret separation;
- audit/evidence review;
- operational runbook;
- rollback procedure.

### Week 4 — Customer acceptance
Deliver:
- deployed integration;
- test report;
- acceptance evidence;
- configuration/policy snapshot;
- release/commit identifiers;
- known limitations;
- production recommendation.

## Customer responsibilities

The customer supplies:
- one target tool or MCP service;
- test environment;
- required identities and access;
- representative policy cases;
- technical owner;
- acceptance criteria for the protected workflow.

## Success criteria

The pilot is successful when the agreed acceptance suite passes in the customer's deployment and the customer receives reproducible evidence of the tested controls.

The pilot does not certify the customer's overall AI system, legal compliance, or downstream business correctness.

## Commercial conversion

After acceptance, the customer may continue as:
- SELF_HOSTED software/support;
- MANAGED service;
- ENTERPRISE integration and support.

Pricing is negotiated according to deployment responsibility, integration complexity, support scope and contractual risk.
