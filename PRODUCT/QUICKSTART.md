# Action Gate 1.0.0 Quickstart

## Product

Action Gate is a deployable policy-enforcement boundary between an agent and protected tools. It evaluates an action, binds the decision to tenant/actor/session/action identity, records evidence, and authorizes execution only through the governed path.

## Production deployment

The production Compose definition is `action_gate/docker-compose.production.yml`.

1. Copy `PRODUCT/.env.example` into deployment-only configuration.
2. Generate unique values for API authentication, decision signing, approval signing, and enforcement secrets.
3. Set a real PostgreSQL password and domain.
4. Keep production execution disabled until the customer acceptance procedure passes.
5. Start the stack and verify Action Gate health.
6. Run the complete customer acceptance procedure.
7. Record version, commit/image digest, policy fingerprint, acceptance evidence, and rollback target.

## Acceptance

A running container is not an accepted security boundary. Acceptance requires evidence for identity binding, decision integrity, nonce single-use, expiry, tenant isolation, ALLOW/DENY/ASK/SANDBOX enforcement, evidence fail-closed behavior, persistence/replay, and absence of a direct downstream bypass.

## Delivery modes

SELF_HOSTED: customer operates the deployment.

MANAGED: HamidCognition operates the service boundary.

ENTERPRISE: negotiated integration, security review, support, and SLA scope.

No mode is a claim of universal safety, legal compliance, or guaranteed business outcome.
