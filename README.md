# BESAZ

**BESAZ is the canonical project name.** The repository preserves historical product and lineage names such as HamidCognition Action Gate where they identify specific artifacts or prior implementations.

The current architecture is being unified under BESAZ as the project-level coordination system.

**Runtime authorization and execution governance for AI agents.**

HamidCognition Action Gate is a deployable control boundary between an AI agent and protected tools:

**Agent → Action Gate → Protected Tool**

It evaluates an action before execution, binds authorization to the relevant tenant/actor/session/action context, records evidence, and allows the protected tool to execute only through the governed path.

## Why it exists

AI agents increasingly have the ability to call APIs, MCP tools, databases, cloud systems and other privileged services. Action Gate addresses one narrow engineering question:

> Can the protected tool independently verify that this exact agent action is authorized, current, correctly bound, and not being replayed?

## Product capabilities

- ALLOW / DENY / ASK / SANDBOX decisions
- tenant, actor, session and action binding
- cryptographically bound decision records
- Gate-issued execution authority
- single-use nonce and replay protection
- HTTP and MCP enforcement
- fail-closed evidence handling
- persistent PostgreSQL operation
- audit and replay evidence
- protected-tool acceptance tests
- self-hosted, managed and enterprise delivery

## Commercial release state

The current published product version is **HamidCognition Action Gate v1.1.1**, sourced from `action_gate/VERSION`.

The latest same-SHA validated and published release is **v1.1.1**, published as GitHub release `action-gate-v1.1.1`.

The mutable main branch is not itself a customer release. v1.1.1 has passed the same-SHA product/security/Clean-Room/production-E2E/release-readiness chain and has a published reproducible artifact. Customer acceptance, licensing, payment and deployment evidence remain separate commercial records.

See PRODUCT/CURRENT_COMMERCIAL_RELEASE.md for the release-control state.

## Commercial entry point

The practical purchase path is a **one-tool proof-of-value pilot**.

Protect one high-impact agent tool or MCP server, run the acceptance suite against the customer's deployment, and deliver reproducible evidence.

See SALES/ONE_PAGER.md, SALES/ICP_AND_POSITIONING.md, SALES/PILOT_OFFER.md, SALES/DEMO_SCRIPT.md, SALES/OUTBOUND_EMAILS.md, and SALES/OBJECTIONS.md.

## Product boundary

Action Gate is a pre-execution authorization and evidence boundary. It does not claim universal AI safety, universal policy correctness, regulatory certification, downstream correctness, or guaranteed business outcomes.

## Delivery models

**SELF_HOSTED** — customer operates the deployment.

**MANAGED** — HamidCognition operates the service boundary.

**ENTERPRISE** — negotiated integration, security review, support, deployment architecture and SLA.

## Research program

The broader repository preserves research and lineage around ClaimLab, P/S/T cognitive-state experiments, LUMEN / behavioral state transfer, KIRGANDE / unknown-space exploration, Farahoosh-Prime experimentation, scale-breaking research, and trading/forecasting experiments.

Those research lines are not automatically commercial product claims. The Action Gate boundary is the product surface.

## Living documentation

The repository includes a Semantic Document Synchronization Layer (SDS). It listens to declared code, release, and evidence signals and keeps deterministic product metadata synchronized. Semantic, commercial, legal, and payment claims are not silently rewritten: they are flagged for revalidation instead.

See PRODUCT/DOCUMENT_SYNCHRONIZATION.md and PRODUCT/DOCUMENT_DEPENDENCY_MAP.yaml.

## Evidence and provenance

Important results are traceable through:

dataset → parameters → code commit → environment → execution → observation → analysis → claim

The repository preserves implementation lineage, evidence records, acceptance procedures and release artifacts.

## Rights

**Copyright © 2026 Hamid Hayati Jozani. All rights reserved.**

Public repository visibility does not by itself grant an open-source license or permission to commercialize the material.

## Citation

For the integrated project, cite **Hamid Hayati Jozani — HamidCognition-Unified** and include the exact release or commit when reproducibility matters.
