# HamidCognition Action Gate Commercial Product Specification

Version: 1.0.0  
Product: HamidCognition Action Gate  
Originator: Hamid Hayati Jozani

## Product definition

Action Gate is a policy-enforcement runtime that evaluates an action before execution, binds the authorization decision to tenant, actor, session, and action identity, records evidence, and permits execution only across an accepted enforcement boundary.

Current executable decisions: ALLOW, DENY, ASK, SANDBOX. DEFER is not part of the current executable policy surface.

## Customer value

The product provides a separately deployable control point between an agent and a tool. It adds explicit authorization state, evidence, replay, identity binding, and enforcement rather than reducing governance to an untraceable allow/deny boolean.

## Validated v1.0.0 boundary

The current release evidence covers:

- production authentication;
- tenant isolation;
- actor/session binding;
- decision integrity and cryptographic binding;
- single-use execution nonce protection;
- HTTP enforcement;
- MCP enforcement;
- fail-closed evidence handling;
- persistent PostgreSQL operation;
- production Compose startup;
- end-to-end smoke validation;
- 200-event decision replay;
- restart/persistence replay;
- clean-room validation on the direct main branch;
- release-candidate container artifact generation.

Evidence references are recorded in the release and workflow artifacts for the exact release baseline.

These are engineering validation claims for the tested boundary. They do not guarantee that every customer policy, downstream tool, deployment, or business process is safe or correct.

## Deployment contract

A customer deployment must provide a protected gate endpoint, production authentication, signing secret/keyring configuration, persistent production storage, an enforcement integration that cannot bypass the gate, customer policy configuration, and appropriate monitoring and backups.

## Commercial boundary

The commercial product must distinguish:

1. software supplied by HamidCognition;
2. customer policy and data;
3. third-party dependencies;
4. customer-specific integration work;
5. support and SLA obligations.

No claim of universal policy correctness, legal compliance, HSM/KMS custody, external identity federation, SIEM integration, high-availability orchestration, or downstream business safety is made unless separately evidenced and explicitly included in scope.
