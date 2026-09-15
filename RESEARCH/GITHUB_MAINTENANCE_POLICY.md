# GitHub Maintenance & Governance Policy

**Repository:** `hamidhayatijozani/HamidCognition-Unified`
**Effective date:** 2026-09-15
**Authority:** Repository owner delegated autonomous engineering-maintenance authority to the connected GitHub agent.

## Purpose

Keep the HamidCognition repository family coherent, traceable, reproducible, and usable as a public research and engineering record.

## Operating rules

1. **Inspect before mutating.** Repository state, branches, files, commits, and existing documentation are evidence. Do not infer missing state.
2. **Preserve provenance.** Every migrated or canonicalized artifact should retain its source repository, source commit when available, original path, destination path, and migration rationale.
3. **Do not silently destroy history.** Existing repositories are treated as historical records until their contents and lineage have been inventoried.
4. **Canonicalization is evidence-based.** A newer, larger, or cleaner implementation is not automatically canonical. Canonical status requires an explicit decision record and, where relevant, validation evidence.
5. **Separate implemented, experimental, historical, and hypothetical material.** Repository presence is not evidence of scientific validity.
6. **Prefer additive, reversible maintenance.** New registries, manifests, documentation, tests, and migration records may be added autonomously. Destructive changes require stronger evidence and should preserve a recovery path.
7. **No invented execution claims.** A test, benchmark, deployment, migration, or validation is reported as completed only when an execution record or GitHub evidence exists.
8. **Protect research integrity.** Failed experiments, contradictions, unknowns, and superseded implementations are retained when they carry provenance or scientific value.
9. **Security boundary.** Never commit secrets, credentials, private keys, tokens, or other sensitive material. Flag suspected secrets rather than reproducing them.
10. **Public-reference quality.** README, citation metadata, lineage records, and status documents must distinguish current canonical state from historical artifacts.

## Autonomous maintenance scope

The delegated agent may, when supported by the connected GitHub permissions:

- inspect repositories, branches, commits, files, issues, pull requests, and CI state;
- create or update documentation, registries, manifests, tests, and migration records;
- reorganize non-destructive repository structure when provenance is preserved;
- create issues describing blockers and required validation;
- review changes and identify contradictions, duplicates, stale claims, and missing evidence;
- maintain the Unified repository as the primary research/provenance index.

## Protected operations

The following are not performed merely for cleanliness:

- deleting a repository;
- destroying or rewriting historical commit history;
- deleting experimental evidence solely because it failed;
- replacing a canonical implementation without a recorded migration decision;
- asserting scientific validation without executable evidence;
- exposing or committing credentials or secrets.

When a protected operation becomes necessary, the safest reversible alternative should be preferred first.

## Repository roles

`HamidCognition-Unified` is the canonical research/provenance index.

Historical repositories remain evidence sources until their inventory and lineage are captured. They may later be classified as `ACTIVE`, `FROZEN`, `ARCHIVED`, `DEPRECATED`, `MERGED`, or `ABANDONED` based on evidence rather than assumption.

## Maintenance loop

```text
OBSERVE
  -> INVENTORY
  -> CLASSIFY
  -> TRACE PROVENANCE
  -> IDENTIFY CONFLICTS
  -> CHANGE REVERSIBLY
  -> VALIDATE
  -> RECORD
  -> REASSESS
```

The maintenance system must never confuse repository cleanliness with research validity.
