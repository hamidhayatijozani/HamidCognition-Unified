# Action Gate v0.4.2

## Release status
Engineering-validated commercial baseline.

## Security and reliability changes
- canonical runtime version is loaded from VERSION;
- actor identity is bound to the decision and execution;
- production execution is restricted to ALLOW;
- SANDBOX is prevented from crossing the production execution boundary;
- evidence reservation precedes downstream execution;
- evidence recording failures fail closed;
- PostgreSQL audit-chain append is serialized;
- SQLite audit-chain writes use an immediate transaction;
- production Docker image includes the canonical VERSION file.

## Validation
Product Gates run 35365796829 passed all configured product-gate stages, including production PostgreSQL/E2E smoke and 200-event restart/persistence replay.

Action Gate MVP, Security Authority Gate, and Research Evidence Gates also passed in the same validation cycle.

## Provenance
Product release baseline commit:
6a8aa17a28ba50c73de1ba714f25bfc04e3268c9

Provenance seal:
PROVENANCE_SEAL_ACTION_GATE_0.4.2.md

This release is an engineering/software product baseline. It is not a claim of universal scientific validation or legal certification.
