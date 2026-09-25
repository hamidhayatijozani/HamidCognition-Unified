# Action Gate v1.0.4 Operations Runbook

## Start

1. Set DOMAIN and unique production secrets through the deployment environment or secret manager.
2. Back up the existing evidence database before first upgrade.
3. Start with docker compose using action_gate/docker-compose.production.yml.
4. Verify /health reports version 1.0.4 and PostgreSQL storage.
5. Verify the tool authority nonce database is located on the persistent production volume.
6. Keep production execution disabled until customer acceptance passes.

## Acceptance

Run PRODUCT/CUSTOMER_ACCEPTANCE.md against the exact deployed commit/image. Record the result, policy hash, image digest, and rollback target.

## Monitoring

Monitor health, request latency, HTTP 4xx/5xx rates, denials and approvals, evidence reservation/finalization failures, PostgreSQL health/storage capacity, tool nonce-store availability, and certificate renewal.

## Incident response

If evidence persistence, authorization, nonce validation, or integrity verification fails, treat the execution path as fail-closed. Preserve logs and evidence before changing the deployment. Do not bypass Action Gate to restore functionality.

## Key rotation

Add the new key to ACTION_GATE_SIGNING_KEYS, select it with ACTION_GATE_KEY_ID, deploy, then retain the previous key until all decisions signed with it have passed their retention period. Never place keys in source control.

## Upgrade

1. Export/backup evidence.
2. Record current version and image digest.
3. Deploy the candidate in a non-production environment.
4. Run the complete acceptance suite.
5. Verify replay compatibility.
6. Verify nonce persistence across a tool-service restart.
7. Roll out reversibly.
8. Record the new version, commit, image digest, policy fingerprint and acceptance result.

## Rollback

Stop the candidate, restore the previously recorded image/release baseline, verify database compatibility, then rerun health and relevant acceptance checks. Do not delete evidence to make a rollback appear clean.

## Recovery boundary

PostgreSQL evidence is part of the security record. Backup and restore procedures must preserve integrity and access controls. The tool nonce database is a separate persistent execution-control state and must also be backed up or recreated only according to the release's documented recovery procedure. HA, external secret managers, SIEM, HSM/KMS and identity federation are deployment-specific and require separate validation.
