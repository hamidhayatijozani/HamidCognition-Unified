# Action Gate Deployment Contract

Version: 1.0.10

This document defines the minimum deployment boundary for a customer installation of Action Gate v1.0.10. It is an operational contract, not a compliance certification.

## Required components

- Action Gate runtime.
- Persistent storage for decision/evidence records.
- Production authentication.
- Signing secret or keyring managed outside source control.
- A non-bypassable integration point between protected actions and Action Gate.
- Customer policy configuration.
- Monitoring for health, latency, denials, evidence failures, and storage failures.
- Backup and restore procedures for persistent evidence.

## Security boundary

Production execution must never call the downstream tool directly when that tool is governed by Action Gate. The integration path is:

request -> authenticated gate -> policy decision -> evidence reservation/recording -> execution authorization -> downstream action.

A failure while reserving or recording required evidence is fail-closed.

## Secrets

Never commit production secrets, signing keys, database passwords, bearer tokens, or customer credentials. Inject them through the deployment environment or an external secret manager.

## Storage

PostgreSQL is the production persistence target for this deployment contract. The exact release evidence must be retained with the candidate being deployed. SQLite is used for persistent execution-authority nonce state in the tool boundary and must remain on the configured persistent production volume. It must not silently replace PostgreSQL as the production evidence store.

## Upgrade rule

Before upgrading a production installation:

1. Export/backup evidence.
2. Record current version and image digest.
3. Run customer acceptance against the candidate.
4. Verify replay compatibility.
5. Roll out reversibly.
6. Record version, commit, image digest, and acceptance result.

## Explicit non-claims

Deployment does not by itself prove that a customer's policy is correct, a downstream tool is safe, or an external regulatory obligation is satisfied.
