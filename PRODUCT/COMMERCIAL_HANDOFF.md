# HamidCognition Action Gate — Commercial Handoff

Version: 1.0.5
Product runtime: Action Gate v1.0.5
Repository governance release: v2.0.0

## 1. What is being sold

The commercial offer is the HamidCognition Action Gate runtime: a deployable authorization and evidence boundary placed between an AI agent and protected tools.

Customer-visible flow:

Agent → Action Gate → Policy Decision → Evidence Reservation → Execution Authority → Tool → Outcome → Evidence → Replay

The product is not sold as a claim that an AI decision is objectively correct. It is sold as an enforceable control point with authenticated identity binding, policy-bound decisions, execution authorization, evidence, and replay.

## 2. Delivery package

A standard self-hosted delivery consists of:

- Action Gate v1.0.5 source/runtime from the exact agreed commit or release baseline.
- Production Docker Compose deployment.
- PostgreSQL persistence.
- Persistent execution-authority nonce storage.
- TLS edge configuration through Caddy.
- Environment/configuration template.
- Integration contract and API contract.
- Customer acceptance procedure and smoke test.
- Operations runbook.
- Security boundary and threat model.
- Release/provenance record.

## 3. Commercial modes

### SELF_HOSTED
The customer operates the deployment. Delivery includes the runtime, deployment materials, integration guidance, acceptance procedure, and agreed release evidence.

### MANAGED
HamidCognition operates the service boundary. Hosting, data residency, monitoring, support, backups, incident response, and SLA terms must be contracted separately.

### ENTERPRISE
Self-hosted or managed deployment with negotiated integration, security review, identity integration, operational controls, support, change management, and SLA scope.

## 4. Customer acceptance

The customer acceptance gate is behavioral, not documentary.

At minimum, acceptance must demonstrate:

1. authenticated protected access;
2. tenant isolation;
3. actor and session binding;
4. decision integrity;
5. action-hash binding;
6. decision expiry;
7. one-time nonce enforcement;
8. ALLOW/DENY/ASK/SANDBOX enforcement;
9. fail-closed behavior when required evidence cannot be reserved or recorded;
10. PostgreSQL persistence;
11. replay after restart;
12. rejection of direct downstream bypass;
13. evidence retrieval and replay match.

The repository's PRODUCT/CUSTOMER_ACCEPTANCE.md defines the detailed procedure.

## 5. Release identity

The commercial runtime baseline is Action Gate v1.0.5. Current release evidence must identify the exact delivered commit, successful same-SHA validation run, artifact digest and release record. Historical v1.0.4 release references are provenance only and must not be substituted for current evidence.

Commercial settlement is USDT only and follows PRODUCT/USDT_PAYMENT_POLICY.md.

## 6. Explicit non-claims

The commercial handoff does not include, unless separately contracted and evidenced:

- regulatory certification;
- universal AI safety;
- correctness of every customer policy;
- correctness or safety of downstream tools;
- HSM/KMS custody;
- external identity-provider federation;
- SIEM integration;
- high availability;
- 24/7 support;
- guaranteed financial or business outcomes.

## 7. Legal and licensing boundary

The repository is private and its license does not grant general rights to reproduce, redistribute, modify, publish, or commercialize the software. Commercial delivery therefore requires a separate written license/permission or another legally valid authorization covering the supplied scope.

## 8. Definition of commercial readiness

For this repository, commercial readiness means that a defined customer can receive a versioned runtime, deploy it using the documented boundary, integrate a protected action path, execute the acceptance procedure, and retain reproducible evidence for the delivered baseline.

It does not mean that market demand, pricing, customer willingness to pay, regulatory approval, or business outcomes have been independently demonstrated.
