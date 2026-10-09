# HamidCognition Action Gate v1.1.1 Delivery Manifest

## Customer deliverable

The canonical commercial runtime is `action_gate/` at version **1.1.1** for the published `action-gate-v1.1.1` delivery baseline.

The published release identity is established by the immutable GitHub release `action-gate-v1.1.1` and its exact source commit `e9ea7565f4ddea91f5c45104237bd20564c80894`. The release workflow validates that exact revision; it does not establish customer acceptance or validate later `main` commits.

The release artifact and checksum must be taken from the v1.1.1 release assets and verified before delivery. Do not substitute the mutable `main` branch for the immutable release baseline.

A delivery must additionally identify:
- image digest when container images are supplied;
- policy version and policy hash;
- deployment configuration baseline;
- acceptance result;
- rollback target;
- customer evidence artifact reference.

## Included

- Action Gate runtime
- production Docker Compose deployment
- PostgreSQL persistence
- persistent execution-authority nonce storage
- Caddy TLS edge
- production configuration template
- deployment contract
- customer acceptance procedure
- operations runbook
- commercial handoff and offer boundary
- CI/release provenance

## Not included by default

- regulatory certification
- guaranteed AI correctness
- downstream tool safety
- HSM/KMS custody
- external identity federation
- SIEM integration
- HA orchestration
- 24/7 support
- guaranteed business or financial outcomes

## Acceptance rule

A customer delivery is accepted only after the exact delivered baseline passes the required behavioral acceptance tests and the evidence is retained.

## Licensing

This repository is not generally licensed for commercialization. A commercial customer must receive a separate written license/permission covering the delivered scope.
