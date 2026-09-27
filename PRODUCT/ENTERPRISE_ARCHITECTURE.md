# HamidCognition Action Gate: Enterprise Architecture

## Purpose

The enterprise architecture separates authorization context, execution enforcement, evidence, policy relationships, execution profiles, plugin integration, and post-execution analysis into explicit contracts.

The first implementation keeps these contracts in one deployable runtime. This is deliberate. The boundaries are independently testable and can later become network services without changing the authorization contract.

## Runtime

Agent -> Decision Context Service -> Enforcement Engine -> Tool or MCP Plugin -> Execution

Evidence Ledger records the lifecycle and Post-Execution Forensics consumes the append-only trail.

Policy Graph and Execution Profile are inputs to Enforcement, not side channels that can override it.

## Decision Context Service

Creates a signed immutable DecisionContext containing tenant, actor, session, agent, action, protected tool, target, parameter digest, policy identity/version/digest, risk level, execution profile, creation time, and expiry.

It does not execute a tool and does not grant execution authority.

## Enforcement Engine

The Enforcement Engine is the protected decision point. It is stateless except for a delegated one-time nonce claim in shared storage.

Every execution checks:

1. context signature and freshness
2. tenant binding
3. agent binding
4. policy identity and policy digest
5. tool binding
6. Policy Graph path
7. Execution Profile requirements
8. one-time nonce

Any failed check returns a denial. There is no permissive fallback.

## Policy Graph

The minimum authorization graph is:

Tenant -> Policy -> Tool
Agent -> Policy
Policy -> Authority

A missing edge is an authorization failure. A graph mutation is not executable merely because the graph contains the edge. The control plane must provide the corresponding evidence and versioned policy state.

## Execution Profiles

Profiles convert binary authorization into graded enforcement:

| Profile | Evidence | Replay | Human review |
| --- | --- | --- | --- |
| LOW | Minimal | Optional | No |
| HIGH | Full | Required | No |
| CRITICAL | Full | Required | Required |

The profile is bound into the signed context. A caller cannot silently downgrade a critical action to a low-risk execution path.

## Plugin Boundary

ToolPlugin and MCPPlugin define the integration contract:

- verify authority before execution
- report execution evidence after execution
- fail closed when the enforcement dependency is unavailable

The contract is protocol-oriented so HTTP tools, MCP servers, and future connectors can implement the same authorization boundary.

## Evidence Ledger

The reference ledger is append-only and hash-chained. The intended lifecycle is:

request -> policy -> decision -> authority -> evidence -> execution -> post-execution digest

Production persistence should use PostgreSQL and/or an immutable retention layer according to customer requirements. The existing Action Gate audit chain remains the runtime evidence source while this module establishes the explicit ledger contract.

## Post-Execution Forensics

The first analyzer is deterministic and intentionally narrow. It emits signals for repeated execution patterns, authority churn within a trace, and unusually high policy usage.

These are risk signals, not claims of compromise or fraud. A downstream security or operations workflow decides what action to take.

## Enterprise boundary

This architecture does not claim regulatory certification, universal AI safety, downstream tool correctness, HSM/KMS custody, identity-provider federation, HA, 24/7 managed operations, or guaranteed business outcomes.

## Acceptance target

The architecture is accepted only when graph cuts fail closed, policy-digest tampering fails closed, profile downgrades fail closed, nonce reuse fails closed, evidence remains append-only, forensic output is deterministic, and the existing HTTP/MCP protected-tool tests remain green.
