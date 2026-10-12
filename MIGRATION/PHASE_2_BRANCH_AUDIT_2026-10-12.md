# Phase 2 — Non-Default Branch and Unmerged Work Audit (2026-10-12)

**Status:** GitHub branch/compare inspection. No branch was deleted, force-pushed, or merged by this audit.
**Why this matters:** Archiving a repository does not delete its branches, but it makes the repository read-only. Unique work on non-default branches must be reviewed and its destination decided before declaring the repository consolidated.

## Findings

### `HamidCognitionEngine`

- Default branch `master`: `3241cdb3ae9ea152d805234c57ebabaf5efe8204`.
- Branch `hardening/pst-canonical-contract`: `7debd089f23cd89fe22360a552c07ddefe3036ea`, **2 commits ahead** of master.
- It adds `.github/workflows/pst-canonical.yml` and expands `integrated/ps_t/test_canonical_engine.py` from a small contract check to regression vectors, deterministic trajectory, invalid-input rejection, state bounds and instance-isolation tests.
- The workflow is configured for Python 3.12 and runs pytest against the canonical contract file.
- A PR was opened to preserve and evaluate this work: [PR #2](https://github.com/hamidhayatijozani/HamidCognitionEngine/pull/2).
- At inspection time, no workflow run or commit status was returned for the exact PR head SHA. **Tests are UNKNOWN; PR must not be merged on an assumed green result.**
- Branch `fix/pst-canonical-weights` is behind master by one commit, with no ahead-only commits reported.

### `hamidcognition-v0-max`

The default branch is `7da846315ea56a6d1b187546b47f68ffe291c004`. Four non-default branches were found:

| Branch | Compare to `main` | Observed change signal | Disposition |
|---|---|---|---|
| `consolidation/unified-governance-system` | diverged; 1 ahead / 9 behind | Adds Deploy, Lint and Tests workflow files relative to the merge base | Review before archive; do not cherry-pick workflows blindly |
| `feat/rfc-0003-governance-integration` | diverged; 21 ahead / 6 behind | Governance RFC/engine, API/server, Docker/compose, requirements and tests | High-value lineage candidate; review every diff before migration |
| `feature/RFC-0003-HHJ-CSG-implementation` | behind by 9; no ahead-only commits | No ahead-only diff reported | Stale branch candidate |
| `hamidhayatijozani-patch-1` | behind by 10; no ahead-only commits | No ahead-only diff reported | Stale branch candidate |

The RFC-0003 branch's API test changes remove dedicated DENY and SANDBOX assertions and replace them with a replay-lineage test. That is not automatically an improvement: the missing decision-boundary assertions must be retained or replaced by equivalent coverage before any port is accepted.

### Other legacy candidates

- `HamidCognition`: `add-readme-license` is behind `master` by five commits; no ahead-only commits reported.
- `hamidcognition-realtime`: `fix/pst-canonical-weights` is behind `main` by one commit; no ahead-only commits reported.
- `hamidcognition-complete`: `fix/pst-canonical-weights` is behind `main` by one commit; no ahead-only commits reported.
- `hamidcognition-web`, `epistemic-filterr`, and `EURUSD-5M-ForecastHamid` had only their default branch in the branch-list response.
- No open PRs were returned for these legacy candidates during the initial check. PR #2 was subsequently opened on `HamidCognitionEngine` for the hardening branch.

## Archive gate update

The original “archive ten repositories” proposal is not ready. In particular:
1. `HamidCognitionEngine` has a two-commit hardening branch and an open evaluation PR.
2. `hamidcognition-v0-max` has a 21-commit governance branch and other CI-related branches that need disposition.
3. A branch being behind is not itself a problem; an ahead/diverged branch may contain unique work and must be inspected.
4. Branch existence and a successful-looking commit message are not proof of CI execution.

Before any archive action, every ahead/diverged branch must be labeled **MERGE**, **PORT**, **RETAIN_AS_HISTORICAL**, or **DISCARD_WITH_EVIDENCE**. Nothing should be discarded solely because the default branch advanced.
