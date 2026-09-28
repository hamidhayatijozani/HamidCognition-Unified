# BESAZ Awareness Integration

BESAZ is the project name and the awareness layer is the coordination substrate.

## Core invariant

Awareness is distributed. Authority is bounded.

Every component has a contract, parent, observable state, triggers, capabilities, limits, action permissions, escalation target and evidence boundary.

## Integrated architecture

OBSERVE -> DETECT NEED -> AUTHORIZE -> EXECUTE/PROPOSE/ESCALATE -> VERIFY -> RECORD -> LEARN

The awareness tree is not a replacement for Action Gate, Z-FREEZE-LOCK, Evidence Pipeline, Strategic Intelligence or Idea-to-Sale. It is the coordination layer that routes work among them.

| Awareness component | Existing subsystem | Responsibility |
|---|---|---|
| GOVERNANCE | Action Gate + Z-FREEZE-LOCK | authority and safety |
| COGNITION | Strategic Intelligence OS | model coordination |
| SELF-MODEL | Self Model | capability evidence |
| CREATOR-CONTEXT | Creator Model | explicit context |
| MARKET-INTELLIGENCE | Market Intelligence | dated market evidence |
| REASONING | Evidence-bound reasoning | bounded inference |
| EXECUTION | Idea-to-Sale OS | controlled execution |
| PROMPTS | Prompt assets | contracted prompt runs |
| MODULES | Application modules | deterministic execution |
| TOOLS | External adapters | bounded external actions |
| WORKFLOWS | Workflow orchestration | gated sequencing |
| FEEDBACK | Evidence Pipeline | outcome verification |
| VERIFICATION | Release verification | artifact/test proof |
| MEMORY | Provenance records | verified state |
| LEARNING | Learning loop | evidence-backed updates |

## Hard rules

1. A component cannot create its own authority.
2. A child cannot silently rewrite a parent contract.
3. PROPOSE is not EXECUTE.
4. ESCALATE is not ALLOW.
5. An approval-required action cannot execute without explicit approval.
6. Completion without evidence is not verification.
7. Unknowns become discovery tasks, not fabricated facts.
8. Financial, destructive, credential, publication, contractual and irreversible actions remain approval-gated unless separately verified by an external authorization system.
9. Maturity cannot self-upgrade.
10. Every externally meaningful result must have provenance.

## Unknown handling

UNKNOWN -> DECOMPOSE -> RESEARCH/RETRIEVE -> VERIFY -> TEST -> RECORD -> UPDATE

If evidence remains unavailable, BESAZ records a blocker and escalates. It does not convert absence of evidence into certainty.

## Current boundary

The Python layer implements contracts, routing and authorization policy. It does not itself grant operating-system, GitHub, payment, credential or legal authority. Those permissions must remain external and auditable.
