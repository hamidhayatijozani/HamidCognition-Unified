# Anderson Gap Matrix — Pre-Outreach Positioning

**Audit date:** 2026-10-08  
**Purpose:** technically honest positioning, not a claim of equivalence or existing integration.

## Source boundary

The public article [“Deception-Resistant MCP Governance: Securing AI Agents in an Era of Strategic Misdirection”](https://www.linkedin.com/pulse/deception-resistant-mcp-governance-securing-ai-agents-david-anderson-yeaye) is attributed to David Anderson and dated August 29, 2025. Its stated principles include: shifting oversight from narrative to telemetry, an independent evidence plane, policy enforcement over intent, tripwires/honeytokens, continuous anomaly detection, and containment/kill switches. These are Anderson's published themes; they are not proof that he personally operates a specific implementation or that he has expressed interest in Action Gate.

## Gap and complementarity matrix

| Published theme | Action Gate evidence today | Honest status | Gap / joint-test question |
|---|---|---|---|
| Telemetry over narrative | Action Gate records authorization/execution evidence; a full behavioral MCP flight-recorder plane is not demonstrated in reviewed evidence | COMPLEMENTARY, NOT EQUIVALENT | Can every request/response, target, result and identity be captured independently of the agent's narrative? |
| Independent evidence plane | Evidence/replay records exist around the execution boundary; immutability/tamper-resistance of a complete MCP telemetry plane not established here | PARTIAL | Can the record be independently reproduced and checked for tampering? |
| Policy enforcement over intent | Prior Risk Lab evidence records G01 authorized execution, G02 direct protected-path rejection (403), G03 authority replay rejection (403) | NARROW RECORDED EVIDENCE | Does the customer's actual protected tool validate authority on every path? |
| Tripwires / honeytokens | No dedicated implementation verified in the reviewed materials | GAP | Does the target workflow need decoy tools/data, and can their activation be safely measured? |
| Continuous anomaly detection | No demonstrated commercial behavior/anomaly detection plane in the reviewed evidence | GAP | Which detector supplies signals, and what are its false-positive/false-negative rates? |
| Containment / kill switches | ALLOW/DENY/ASK/SANDBOX decisions exist; independent kill-switch control plane not established | PARTIAL | What is the emergency stop, authority revocation and rollback path? |
| MCP governance / server trust | MCP integration and E2E tooling are documented; live HTTP/MCP parity and comprehensive server supply-chain governance were not verified in this audit | PARTIAL / UNKNOWN | Can one selected MCP server enforce the same authority and preserve server identity/version provenance? |
| Signal-to-action binding | Context/action/policy binding is part of the Action Gate design; integration from an external behavioral detector to Gate is not evidenced | INTEGRATION GAP | Can the detector's signal be bound to the exact tenant/actor/session/action hash and policy snapshot? |
| Business impact | No customer outcome, ROI or avoided-loss evidence verified | UNKNOWN | Which concrete consequence and acceptance threshold matter to the buyer? |

## Complementary architecture hypothesis

```text
Behavioral observation / anomaly detection
          ↓ signal + provenance
Action Gate binds signal to exact action / context / policy
          ↓ valid execution authority
Protected HTTP / MCP tool
          ↓
Evidence + replayable acceptance result
```

The detector may identify suspicious behavior; the Gate's proposed role is to enforce authorization at the execution boundary. This is a complementarity hypothesis, not an existing integrated feature.

## Suggested adversarial experiment

1. Select one real, consequential but safely isolated MCP workflow.
2. Define a normal action and a small set of suspicious or policy-violating variants.
3. Record detector output separately from the Gate decision.
4. Bind signal, decision and action to the same tenant/actor/session/action hash and policy snapshot.
5. Test direct bypass, action/parameter mutation, tenant substitution, expired authority, replay, concurrent reuse, restart and alternate MCP routes.
6. Capture raw protocol messages, detector output, Gate decision, actual tool side effect, timestamps, exact source/release SHA and artifact digest.
7. Report each result and false positive/negative separately. Do not collapse the outcome into “secure” or “deception-proof”.

## Safe positioning

> Your article separates behavioral observability from enforcement. Action Gate is focused on the latter: the boundary where a tool call becomes a side effect. The useful question is whether a detector's signal can be bound to the exact MCP action and whether the protected tool enforces the resulting decision under adversarial conditions.

Do not claim Action Gate detects deception, implements or replaces Anderson's approach, is already integrated with any detector, guarantees all MCP security, or has customer validation/revenue.

**Positioning readiness:** READY FOR A SHORT TECHNICAL QUESTION.  
**Integration readiness:** NOT ESTABLISHED.  
**Outreach status:** NOT SENT.  
**CONTACTED status:** NOT VERIFIED until an actual message is sent through a verified channel.
