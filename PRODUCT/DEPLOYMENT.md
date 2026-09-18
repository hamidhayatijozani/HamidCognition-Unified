# Action Gate Deployment Contract

Version: 1.0.0 baseline

The current deployment contract targets Action Gate 1.0.0. Historical 0.4.x records remain historical evidence and are not relabeled as 1.0.0 execution evidence.

This document defines the minimum deployment boundary for a customer installation. It is an operational contract, not a compliance certification.

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

PostgreSQL is the production persistence target for this deployment contract. The exact release evidence must be retained with the candidate being deployed. SQLite may be useful for local development but must not silently become the production persistence layer.

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
