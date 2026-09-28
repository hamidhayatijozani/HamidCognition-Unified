# Product Completion Control

This file is the execution control for turning HamidCognition-Unified into a coherent commercial product while preserving the research program.

## Canonical product

Current product boundary: **HamidCognition Action Gate v1.1.0**.

The executable product version is sourced from `action_gate/VERSION`. The current main branch is the v1.1.0 development/release-candidate line.

**Offerable release and current product version are separate facts:** v1.0.10 is the last independently validated and published commercial release. v1.1.0 must not be presented as an offerable published release until its exact source SHA, CI evidence, artifact digest and release record are validated together.

The commercial product is the executable Action Gate boundary. Research lines remain separate evidence-bearing assets until they have their own implementation, tests, reproducibility record, and explicit product boundary.

## Completion gates

1. **Repository integrity**
   - one canonical main branch;
   - version references agree with `action_gate/VERSION`;
   - obsolete product claims are removed or marked historical;
   - provenance and rights records remain intact.

2. **Executable integrity**
   - Action Gate starts from the production definition;
   - authentication, tenant/actor/session binding, decision integrity, nonce protection and fail-closed behavior are executable;
   - HTTP and MCP enforcement use the same governed authority;
   - direct downstream bypass is rejected;
   - policy binding is independently verified at the protected tool boundary.

3. **Evidence integrity**
   - customer acceptance tests are executable;
   - CI records the exact commit and result;
   - release evidence is tied to the same source revision;
   - failed or unverified claims are not presented as verified.

4. **Commercial readiness**
   - SELF_HOSTED, MANAGED and ENTERPRISE boundaries are explicit;
   - deployment and acceptance instructions are complete;
   - customer-facing scope excludes unsupported guarantees;
   - a reproducible release artifact can be identified.

5. **Research portfolio**
   - every research line is classified as IMPLEMENTED, HYPOTHESIS, UNKNOWN, FALSIFIED or SUPERSEDED;
   - only evidence-backed candidates move toward productization;
   - opportunities outside the repository are evaluated separately for challenge, bounty, grant or prize eligibility.

## Portfolio rule

Do not merge research into the commercial runtime merely because it is interesting. Promote a research line only when it provides a concrete capability, an executable test, reproducible evidence, and a defensible user problem.

## Opportunity pipeline

**Discover → verify eligibility → estimate effort → build minimum winning artifact → validate → submit → preserve evidence.**

No prize or market claim is considered real until its external rules and the submission evidence are verified.

## Current product state

**Current development product: Action Gate v1.1.0.**

**Last validated published commercial release: Action Gate v1.0.10.**

Current release evidence is valid only when the exact source SHA, workflow run, artifact digest and release record agree.

Commercial payment is USDT only. Payment settlement is deliberately outside the Action Gate authorization path and is governed by PRODUCT/USDT_PAYMENT_POLICY.md.

The product is not considered commercially verified merely because the repository contains release documents. A current offerable release requires same-SHA product/security/clean-room validation and a reproducible release artifact, followed by customer-specific acceptance for production execution.
