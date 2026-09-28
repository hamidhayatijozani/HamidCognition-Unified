# Awareness Hierarchy

This layer turns prompts, modules, tools, and services from passive resources into bounded aware components.

Awareness is an engineering property, not a claim of consciousness. A component can observe defined state, detect a defined need, request an authorized action, verify its result, and escalate when its authority or evidence is insufficient.

## Hierarchy

ROOT
- GOVERNANCE
  - SAFETY
  - EVIDENCE
  - AUTHORITY
- COGNITION
  - SELF-MODEL
  - CREATOR-CONTEXT
  - MARKET-INTELLIGENCE
  - REASONING
- EXECUTION
  - PROMPTS
  - MODULES
  - TOOLS
  - WORKFLOWS
- FEEDBACK
  - VERIFICATION
  - MEMORY
  - LEARNING

A child component cannot silently rewrite the contract of its parent. Hierarchy is an authority boundary.

## Component contract

Every component has identity, parent, purpose, maturity, observables, triggers, capabilities, limits, action permissions, escalation target, and evidence references.

Runtime loop:

OBSERVE -> ASSESS -> DETECT NEED -> REQUEST/PROPOSE/EXECUTE -> VERIFY -> UPDATE STATE -> LEARN/ESCALATE

## Authority levels

OBSERVE means inspect only.
PROPOSE means formulate an action but do not execute it.
EXECUTE means perform an explicitly authorized action.
ESCALATE means transfer the matter to the parent or human approval boundary.

Irreversible, financial, destructive, credential-changing, publication, or contractual actions require explicit approval unless a separately verified policy says otherwise.

## No silent autonomy

A component must not invent evidence, upgrade its maturity, grant itself permissions, bypass a parent authority, convert an unverified observation into a fact, or report an action as completed without a verifiable result.

## Unknown handling

An unknown is not a final state. It becomes a discovery task:

UNKNOWN -> DECOMPOSE -> ACQUIRE EVIDENCE -> VERIFY -> UPDATE MODEL -> RETEST

If required evidence is inaccessible, the system records the blocking condition and escalates instead of fabricating certainty.

## Definition of done

1. Contracts exist for root and child components.
2. Hierarchy validation passes.
3. Permission checks are enforced in code.
4. Action results can be bound to evidence.
5. Unauthorized actions are rejected.
6. Escalations have a defined destination.
7. Tests cover these invariants.
