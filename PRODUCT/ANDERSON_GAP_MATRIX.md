# Anderson Gap Matrix — Pre-Outreach Positioning

**Audit date:** 2026-10-08  
**Purpose:** technically honest positioning, not a claim of equivalence or existing integration.

## Source boundary

Public references associated with David Anderson:
- [LinkedIn profile](https://www.linkedin.com/in/davidandersonorlando)
- [Public article/post reference](https://www.linkedin.com/pulse/deception-resistant-mcp-governance-securing-ai-agents-david-anderson-yeaye)

The article title references “Deception-Resistant MCP Governance”. Its complete text and detailed technical claims were not independently captured in this audit. The matrix below treats Anderson-oriented themes as hypotheses to verify in conversation, not as a definitive attribution of a complete architecture.

| Theme | Action Gate evidence today | Honest status | Gap / joint-test question |
|---|---|---|---|
| Behavioral deception/anomaly detection | No verified behavior/deception classifier in the inspected Risk Lab path | GAP | What signal is emitted, with what false-positive/false-negative profile? |
| MCP governance | MCP integration and E2E tooling are documented; live parity was not rerun here | PARTIAL | Can one customer-selected MCP server enforce the same authority as the HTTP path? |
| Telemetry over narrative | Action Gate records authorization/execution evidence; no full behavioral telemetry plane demonstrated | COMPLEMENTARY, NOT EQUIVALENT | Can the detector's signal be retained with protocol-level request/response evidence? |
| Policy enforcement at the side-effect boundary | Recorded G01 success, G02 direct protected-path rejection (403), G03 authority replay rejection (403) in prior Risk Lab evidence | NARROW RECORDED EVIDENCE | Does the customer's actual protected tool independently validate the authority on every route? |
| Signal-to-action binding | Action/policy/context binding exists in the product design; detector-to-Gate integration not evidenced | INTEGRATION GAP | Can the detection signal be bound to the exact tenant/actor/session/action hash and policy snapshot? |
| Tripwires / honeytokens | No dedicated implementation found in reviewed materials | GAP | Are they needed for the selected workflow, or out of scope? |
| Continuous anomaly detection | No demonstrated commercial detection plane in reviewed evidence | GAP | Is detection supplied by the customer's existing control, an external detector, or not part of this test? |
| Containment / kill switch | ALLOW/DENY/ASK/SANDBOX decisions exist; independent kill-switch control plane not established | PARTIAL | What is the emergency stop and rollback path in the target environment? |
| MCP server trust / supply chain | Insufficient evidence for comprehensive governance | UNKNOWN/GAP | Which server identity, version and trust boundary are in scope? |
| Business impact / ROI | No customer outcome or ROI evidence | UNKNOWN | What measurable consequence and acceptance threshold does the buyer care about? |

## Complementary architecture hypothesis

```text
Behavioral observation/detection
          ↓ signal with provenance
Action Gate binds signal to exact action/context/policy
          ↓ valid execution authority
Protected HTTP/MCP tool
          ↓
Evidence + replayable acceptance result
```

The detector can flag suspicious behavior; the Gate's proposed role is to enforce the resulting policy at the execution boundary. This is a complementary hypothesis, not an existing integrated feature.

## Suggested adversarial experiment

1. Select one real, consequential but safely isolated MCP workflow.
2. Define a normal action and a small set of suspicious/policy-violating variants.
3. Record detector output separately from the Gate decision.
4. Bind signal, decision and action to the same tenant/actor/session/action hash and policy snapshot.
5. Test direct bypass, action/parameter mutation, tenant substitution, expired authority, replay, concurrent reuse, restart and alternate MCP routes.
6. Capture raw protocol messages, detector output, Gate decision, actual tool side effect, timestamps, exact source/release SHA and artifact digest.
7. Report pass/fail and false positives/negatives per scenario. Do not collapse the result into “secure” or “deception-proof”.

## Safe positioning

> Behavioral detection and execution enforcement address different parts of the control problem. A detector can flag an action; an execution boundary can require valid authority before the tool performs the side effect. The useful question is whether a detector's signal can be bound to the exact MCP action and whether the protected tool enforces the resulting decision under adversarial conditions.

Do not claim that Action Gate detects deception, implements or replaces Anderson's approach, is already integrated with his work, or proves universal MCP security.

**Positioning readiness:** READY FOR A SHORT TECHNICAL QUESTION.  
**Integration readiness:** NOT ESTABLISHED.  
**Outreach status:** NOT SENT.  
**CONTACTED status:** NOT VERIFIED until an actual message is sent through a verified channel.
