# Action Gate Portable Runtime

This directory provides a repeatable bootstrap around the existing production Docker Compose deployment.

## Truth boundary

The runtime capsule records observations. It does not treat self-reported host properties as trusted facts. Verified host identity requires cryptographic attestation.

## Start

From the repository root:

```bash
bash runtime/bootstrap.sh
```

The bootstrapper requires Docker Compose v2, creates a local `.runtime.env` with fresh secrets when needed, builds the existing production services, starts them, and writes `evidence/runtime/runtime-capsule.json`.

## Health

```bash
bash runtime/healthcheck.sh
```

## Public access

The existing Caddy edge is controlled by `DOMAIN`. A public deployment needs a real DNS name pointing to the host. Do not expose Action Gate or the protected tool directly.

## Distributed-host roadmap

`registration -> attestation -> capability probe -> policy eligibility -> execution authority -> revalidation -> execution -> evidence`

This layer does not create compute from nothing. It makes the existing application portable across hosts that already provide compute.
