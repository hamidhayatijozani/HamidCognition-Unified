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

The latest published technical release is **HamidCognition Action Gate v1.1.1**, tag `action-gate-v1.1.1`. Its source revision and artifact checksum are recorded in `PRODUCT/COMMERCIAL_RELEASE.json` and the published release manifest. The release workflow is [36966012148](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/36966012148).

At the 2026-10-08 audit, main's version file read `1.1.1`, but main's SHA differed from the published release source SHA. Quote and deliver the immutable published release, not the mutable main branch, until a new same-SHA release chain validates a newer source.

## Validated boundary

The published release workflow reports success for its exact tested revision. Prior Risk Lab evidence records a narrow local result for governed authorized execution, direct protected-path rejection and authority replay rejection. These are engineering results for the tested scenarios, not independent proof of every capability listed in the product design or of customer deployment.

These are engineering validation claims for the stated release and tested boundary. They are not claims of universal AI safety, universal policy correctness, regulatory certification, downstream tool safety, or guaranteed business outcomes.

## Commercial deployment

**SELF_HOSTED:** customer operates the deployment.

**MANAGED:** HamidCognition operates the service boundary under separately contracted hosting, data residency, monitoring, support, backup, incident-response, and SLA terms.

**ENTERPRISE:** self-hosted or managed deployment with negotiated integration, security review, identity integration, operational controls, support, change management, and SLA scope.

## Pilot offer

**Standard scoped pilot: USD $2,500 fixed / 30 days.**

Scope: one customer-selected HTTP/MCP tool, one controlled test environment, agreed acceptance cases, deployment assistance and a reproducible evidence package. Any expanded scope or different price requires a separate written quote before work begins.

## After the pilot

SELF_HOSTED, MANAGED and ENTERPRISE are possible next delivery models, but their operational scope and pricing must be negotiated after the customer's acceptance criteria, deployment responsibility and support requirements are known. No annual or OEM price is treated as a validated market price or included in the first-pilot offer.

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
