# David Anderson — Technical Evidence Packet

**Status:** PREPARED / NOT SENT  
**Purpose:** technical discussion and scoped adversarial test. This is not a customer acceptance report.

## Product boundary

BESAZ / HamidCognition Action Gate is positioned as an execution authorization boundary between an agent and a protected HTTP/MCP tool. It is not presented as a behavioral-deception detector.

## Published artifact

- Release: [action-gate-v1.1.1](https://github.com/hamidhayatijozani/HamidCognition-Unified/releases/tag/action-gate-v1.1.1)
- Release source SHA: `e9ea7565f4ddea91f5c45104237bd20564c80894`
- Release workflow: [36966012148](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/36966012148), GitHub reports success
- Artifact: `action-gate-1.1.1.tar`
- Artifact SHA-256: `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`
- Important: main currently reads version 1.1.1 but has a different SHA. Do not treat mutable main as identical to this release.

## Recorded Risk Lab evidence

- Source: [Risk Lab demo script](../tools/run_risk_lab_demo.py)
- Recorded workflow: [36429274558](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/36429274558)
- Recorded artifact SHA-256: `19141b22b0a17488dce982c2593ee66e6e2575dbe2a05f901df22d3a56929684`

| ID | Scenario | Recorded outcome | Interpretation |
|---|---|---|---|
| B01 | Separate unprotected local reference endpoint | HTTP 200 / observed | Deliberate baseline; not a protected-tool bypass result |
| G01 | Gate-authorized call to protected tool | HTTP 200 / pass | Authorized path succeeded in the recorded run |
| G02 | Direct call to protected tool without authority | HTTP 403 / pass | The tested direct request was rejected |
| G03 | Reuse the same execution authority | HTTP 403 / pass | The tested replay was rejected |

These are narrow results from a recorded local engineering test. They are not a universal security guarantee or evidence of a customer deployment.

## Gaps to keep explicit

Not established by the cited G01–G03 run:
- expired-authority rejection;
- action or policy tampering;
- tenant/session substitution;
- concurrent nonce race behavior;
- restart/persistence behavior;
- HTTP/MCP parity on one exact SHA;
- behavior-detector-to-Gate integration;
- customer acceptance, revenue, compliance certification or ROI.

## Proposed adversarial challenge

Use one customer-selected real MCP workflow in an isolated test environment. Agree on one consequential tool action and a safe way to observe side effects.

1. Valid authorized execution.
2. Direct tool call without Gate-issued authority.
3. Change action/parameters after decision.
4. Change tenant, actor or session context.
5. Submit expired authority.
6. Replay the same authority.
7. Submit concurrent requests using the same authority/nonce.
8. Restart the relevant service and retry.
9. Attempt the same action over alternate HTTP/MCP routes.
10. If a behavior detector is available, pass its signal into policy and verify that the signal is bound to the exact action/context rather than merely logged.

For each case preserve exact release/source SHA, environment, request and response, detector output if applicable, Gate decision, actual tool-side effect, timestamps and evidence digest. Report failures and untested cases without reclassifying them.

## Proposed outcome

The experiment should answer one narrow question:

**Can the selected protected tool perform the consequential action only when the exact, current, Gate-issued authority is valid, and can the team reproduce evidence for both allowed and rejected attempts?**

## Claims prohibited by this packet

Do not claim Action Gate detects deception, implements Anderson's approach, is already integrated with any detector, guarantees all MCP security, is customer-validated, or has generated revenue.
