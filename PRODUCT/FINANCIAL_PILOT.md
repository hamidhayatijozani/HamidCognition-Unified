# Financial Automation Pilot

## Objective

Prove a controlled end-to-end path for one real financial workflow:

Bank data -> canonical financial events -> reconciliation -> governed decision -> destination execution -> verification -> evidence.

## Pilot boundary

The first pilot should support one verified bank input format and one verified destination integration. A second accounting destination is added only after the first execution path is stable.

The pilot must demonstrate:

1. deterministic matching for exact evidence;
2. ambiguous matching routed to ASK rather than automatic posting;
3. idempotency across retries;
4. UNKNOWN state after an uncertain external outcome;
5. post-execution verification;
6. reconstructable evidence for each operation.

## Required customer inputs

- actual Asan integration method and version;
- actual Sepidar integration method and version;
- bank statement export format or API access;
- representative non-production data;
- accounting rules that define which transactions may be automated;
- a safe test environment or an agreed controlled window.

## Explicit boundary

No production connector is claimed until the customer's actual integration surface is inspected and a connector acceptance test passes.
