# Runtime Capsule

Runtime Capsule is the portable deployment boundary for Action Gate. It packages Action Gate, Enforcement, the protected tool, PostgreSQL, Dashboard, MCP, and the HTTPS edge into one reproducible Compose runtime.

## Design rule

The capsule is portable across any host capable of running Docker Compose. It does not assume a particular cloud vendor.

## Required host

- Linux or equivalent Docker host
- Docker Engine
- Docker Compose plugin
- persistent storage
- a public DNS name for public HTTPS operation

The capsule does not bypass provider verification, payment controls, sanctions, or identity requirements. It removes dependence on a specific hosting vendor.

## Bootstrap

Set a real DNS name:

```bash
export DOMAIN=diag.example.com
bash tools/runtime_capsule_bootstrap.sh
```

The script generates deployment-local secrets when `.env` does not already exist. The file is intentionally not committed.

## State Oracle

Production execution requires an initialized authoritative committed snapshot. The state oracle is separate from agent-supplied evidence.

Lifecycle:

1. An authorized state provider signs a snapshot containing `world_version` and observed state.
2. Action Gate commits that snapshot.
3. New decisions bind to the current `world_version`.
4. Execution requires the same version.
5. If the committed world changes, the old execution authority becomes unusable.

This is an execution-integrity boundary, not a claim that Action Gate magically knows physical reality. Reality still needs an authenticated state provider.

## Runtime identity

Every deployment should publish:

- runtime_id
- git_sha
- image digest
- policy_hash
- state world_version
- database schema version
- started_at
- capabilities

## Public boundary

Only the Caddy edge is published. Action Gate and the protected tool remain on the internal network. Ports 8000 and 9000 must not be exposed directly.

## Evidence

A deployment is accepted only after the customer acceptance procedure passes and the resulting evidence is retained with the release identity and runtime metadata.
