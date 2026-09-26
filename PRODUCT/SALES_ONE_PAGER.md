# HamidCognition Action Gate — Enterprise Sales One-Pager

## Executive proposition

**Pre-execution governance and authorization for AI agents.**

HamidCognition Action Gate is a separately deployable control point between an AI agent and protected tools. It evaluates an action before execution, binds the authorization decision to tenant, actor, session, and action identity, records evidence, and permits execution only through the accepted enforcement boundary.

## The product

- Policy-bound action decisions: **ALLOW / DENY / ASK / SANDBOX**
- Tenant, actor, session, and action identity binding
- Cryptographic decision/action binding
- Single-use execution nonce protection with persistent nonce state
- Evidence reservation and recording
- Fail-closed behavior when required evidence cannot be reserved or recorded
- Persistent evidence and replay
- HTTP and MCP enforcement boundaries
- Deployment as a separately operated control point between Agent and Tool

## Customer-visible flow

**Agent → Action Gate → Policy Decision → Evidence Reservation → Execution Authority → Tool → Outcome → Evidence → Replay**

## Offerable release

The current customer-deliverable release is **Action Gate v1.0.5**, published at exact source commit:

f3c77cbb314e76911cce37298d58202ffb451d6e

The release contains a versioned container archive, SHA-256 checksum and release manifest. Customer delivery must use this immutable release rather than the mutable main branch.

The current main branch contains later engineering/research changes and is not commercially release-closed until its same-SHA GitHub validation chain is green. This distinction prevents a development head from being represented as a validated customer artifact.

## Validated boundary

The v1.0.5 release evidence covers the documented Action Gate boundary, including production authentication, tenant/actor/session binding, decision integrity, persistent nonce protection, HTTP and MCP enforcement, fail-closed evidence handling, PostgreSQL persistence, production Compose startup, replay/persistence validation, clean-room validation, security-history scanning, and release-readiness gating.

These are engineering validation claims for the stated release and tested boundary. They are not claims of universal AI safety, universal policy correctness, regulatory certification, downstream tool safety, or guaranteed business outcomes.

## Commercial deployment

**SELF_HOSTED:** customer operates the deployment.

**MANAGED:** HamidCognition operates the service boundary under separately contracted hosting, data residency, monitoring, support, backup, incident-response, and SLA terms.

**ENTERPRISE:** self-hosted or managed deployment with negotiated integration, security review, identity integration, operational controls, support, change management, and SLA scope.

## Pilot offer

**Strategic Proof-of-Value Pilot: 50,000 USDT**

Recommended scope: one protected agent-to-tool execution path, customer-selected policy scenarios, integration support, acceptance testing, evidence/replay demonstration, and a written pilot outcome report.

Pilot duration: **6–8 weeks**, subject to integration scope.

Pilot fee is a commercial proposal, not a claim of market-standard pricing.

## Enterprise conversion

Indicative annual software license target after successful pilot: **150,000–300,000 USDT/year**, with customer-specific integration, managed operations, support, SLA, and special security requirements priced separately.

## Strategic / OEM licensing

For embedding Action Gate capabilities into another vendor's product or platform, use a negotiated technology/OEM license. Initial commercial discussion target: **500,000+ USDT**, with scope, exclusivity, deployment rights, support, and any royalty/minimum-commitment structure negotiated separately.

## Who should evaluate it

- AI platform and agent infrastructure teams
- AI security and governance teams
- Enterprise automation platforms
- MCP/tool orchestration platforms
- Financial and other high-consequence enterprises deploying tool-using agents
- Vendors building agent security or control-plane products

## What the buyer receives

A versioned runtime, deployment materials, integration/API contract, acceptance procedure, operations guidance, security boundary/threat model, and agreed release/provenance evidence, subject to the selected commercial scope and written license.

## Payment

All commercial fees are payable in USDT only. The accepted network and receiving address are stated on the invoice. Settlement is confirmed only from an independently verified transaction hash and the configured confirmation policy.

## Commercial boundary

The product is sold as an enforceable control point. It does not represent that every AI decision is correct, that every downstream tool is safe, or that regulatory compliance exists unless separately evidenced and contracted.

**Primary sales message:** Control the action before the agent executes it, and retain evidence of what was authorized, by whom, under which policy, and what happened afterward.
