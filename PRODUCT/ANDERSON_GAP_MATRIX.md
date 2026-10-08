# Anderson Alignment and Gap Matrix

Date: 2026-10-08
Purpose: pre-outreach technical positioning, not a claim of equivalence.

| Anderson-oriented concern | Action Gate position | Conclusion |
|---|---|---|
| Telemetry over narrative | Authorization/evidence records are tied to execution | COMPLEMENTARY, not equivalent to a full telemetry plane |
| Independent evidence plane | Evidence Ledger/replay exists around the execution boundary | PARTIAL |
| Policy enforcement over intent | Exact action/context/authority/policy binding at enforcement point | STRONG ALIGNMENT |
| Tripwires / honeytokens | No dedicated implementation found | GAP |
| Continuous anomaly detection | Forensic signals are referenced, but no demonstrated continuous detection plane | PARTIAL/GAP |
| Containment / kill switch | DENY/SANDBOX/ASK provide execution controls | PARTIAL; independent kill switch not established |
| MCP telemetry | MCP enforcement and E2E tooling exist | PARTIAL |
| MCP server trust / supply chain | No sufficient evidence for full governance | GAP |
| Behavioral baseline | Research references exist, but no demonstrated commercial behavioral-detection layer | GAP |
| Business Impact Intelligence | No established implementation found | GAP |

## Defensible integration hypothesis

Agent -> behavioral observation/detection -> Action Gate -> exact context/policy/authority binding -> protected MCP/tool -> evidence -> containment/response

The key distinction is simple: monitoring can establish that something happened; enforcement determines whether the protected action can happen.

## Adversarial challenge

Use one real MCP/tool workflow and attempt to:

1. replay a valid authority;
2. alter the action after decision;
3. alter tenant/session context;
4. use expired authority;
5. race concurrent execution;
6. mutate policy binding;
7. bypass the gate directly.

Expected invariant: no consequential tool effect crosses the protected boundary unless the exact governed authority and required evidence remain valid.

## Non-claims

This matrix does not establish that Action Gate implements Anderson's complete governance model, nor does it establish live production behavior against an external MCP server.
