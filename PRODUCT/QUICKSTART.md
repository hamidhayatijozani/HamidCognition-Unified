# Action Gate 1.1.0 Quickstart

## Product

Action Gate is a deployable policy-enforcement boundary between an agent and protected tools. It evaluates an action, binds the decision to tenant/actor/session/action identity, records evidence, and authorizes execution only through the governed path.

The current development product version is **v1.1.0**, sourced from `action_gate/VERSION`.

The last validated published commercial release is **v1.0.10**. Do not treat the mutable main branch or the v1.1.0 development line as a published commercial release until release-candidate validation and publication are complete.

## Production deployment

The production Compose definition is `action_gate/docker-compose.production.yml`.

1. Copy `PRODUCT/.env.example` into deployment-only configuration.
2. Generate unique values for API authentication, decision signing, approval signing, and enforcement secrets.
3. Set a real PostgreSQL password and domain.
4. Keep production execution disabled until the customer acceptance procedure passes.
5. Start the stack and verify Action Gate health.
6. Run the customer acceptance procedure from inside the Action Gate service:
   `docker compose -f action_gate/docker-compose.production.yml exec action-gate python /app/customer_acceptance_smoke.py`
7. Record version, commit/image digest, policy fingerprint, acceptance evidence, and rollback target.
8. Verify the tool authority nonce database is on the persistent production volume configured by the Compose file.

The smoke test is deliberately executed against the internal Action Gate API. The production edge does not publish the Action Gate API directly, which preserves the protected boundary.

## Acceptance

A running container is not an accepted security boundary. Acceptance requires evidence for identity binding, decision integrity, nonce single-use, expiry, tenant isolation, ALLOW/DENY/ASK/SANDBOX enforcement, evidence fail-closed behavior, persistence/replay, and absence of a direct downstream bypass.

The smoke test is non-destructive and uses the inert `example.read_only_check` action. It verifies health, ALLOW evaluation, execution reservation, execution recording, evidence hash, and replay consistency. The complete acceptance procedure remains mandatory because the smoke test does not replace protected-tool bypass and tampering tests.

## Delivery modes

SELF_HOSTED: customer operates the deployment.

MANAGED: HamidCognition operates the service boundary.

ENTERPRISE: negotiated integration, security review, support, and SLA scope.

No mode is a claim of universal safety, legal compliance, or guaranteed business outcome.
