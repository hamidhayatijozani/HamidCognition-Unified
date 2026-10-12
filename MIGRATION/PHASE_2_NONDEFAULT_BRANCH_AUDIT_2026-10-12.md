# Phase 2 — Non-Default Branch and Unmerged Work Audit (2026-10-12)

**Status:** Read-only branch comparison and workflow review. No branches were deleted, merged, or force-pushed by this audit.
**Decision impact:** A repository must not be archived while unique branch-only code is unresolved. Repository archival makes the repository read-only; it is not a safe substitute for reviewing unmerged work.

## Findings

### hamidcognition-v0-max — BLOCK ARCHIVE

Two branches contain work not present on main:

1. **feat/rfc-0003-governance-integration**
   - Compare result: **21 commits ahead, 6 behind** the current default branch.
   - Unique file set includes governance/governance_engine.py, governance/RFC-0003-INTEGRATION.md, tests/test_governance_engine.py, plus API server changes, Docker/deployment files, requirements, and workflow definitions.
   - This is a substantive pre-response governance layer: it evaluates an ObservableDecisionArtifact and returns ALLOW / ASK / SANDBOX / DENY. Its own RFC explicitly states it does **not** replace cryptographic Action Gate execution authorization.
   - Latest returned RFC-0003 workflow success is on branch HEAD 794076bdc1addebc2f20094c357f3468bdb091fb: [governance tests](https://github.com/hamidhayatijozani/hamidcognition-v0-max/actions/runs/35547475333) and [CI/CD](https://github.com/hamidhayatijozani/hamidcognition-v0-max/actions/runs/35547475382), both from 2026-09-21.
   - **Disposition:** do not archive the repository until this branch is reviewed for merge/port/history-only status. Decide whether the pre-response governance behavior belongs in Unified, belongs as an independent product capability, or remains a preserved experiment. If ported, add behavior-preservation tests and make clear it is not the Action Gate's execution authority.

2. **consolidation/unified-governance-system**
   - Compare result: **1 commit ahead, 9 behind**.
   - Its one unique commit adds three workflows: deploy, lint, and tests.
   - The visible workflow evidence on branch HEAD 50e87647550ed8a2ca7b4be398d1655d4bd90d31 shows **Lint & Format failure** and **Tests cancelled**: [lint run](https://github.com/hamidhayatijozani/hamidcognition-v0-max/actions/runs/31248794916), [test run](https://github.com/hamidhayatijozani/hamidcognition-v0-max/actions/runs/31248794857).
   - **Disposition:** preserve the branch until workflow intent is reviewed; do not copy failing workflows blindly. Either repair and port, or record why they are intentionally excluded.

Other hamidcognition-v0-max branches:
- feature/RFC-0003-HHJ-CSG-implementation: no ahead-only commits vs current main (behind by 9).
- hamidhayatijozani-patch-1: no ahead-only commits vs current main (behind by 10).
These two branches do not currently block archive on unique commits according to compare metadata, but repository-level dependency/deployment checks still apply.

### Other historical repositories

| Repository | Non-default branch | Compare result | Disposition |
|---|---|---|---|
| HamidCognition | add-readme-license | 0 ahead, 5 behind | No unique branch-only commits reported; still review repository files before archive. |
| HamidCognitionEngine | fix/pst-canonical-weights | 0 ahead, 4 behind | No unique branch-only commits reported. |
| HamidCognitionEngine | hardening/pst-canonical-contract | 0 ahead, 1 behind | Hardening work is now merged to master at 9da718d1ba8964a4e4ae3f0f5e3455c6c26cdecb; exact-SHA workflow passed. |
| hamidcognition-realtime | fix/pst-canonical-weights | 0 ahead, 1 behind | No unique branch-only commits reported. |
| hamidcognition-complete | fix/pst-canonical-weights | 0 ahead, 1 behind | No unique branch-only commits reported. |
| hamidcognition-web | No non-default branch returned | N/A | No extra branch surfaced by the branch-list query. |

## Updated archive decision

**Do not archive hamidcognition-v0-max yet.** Its RFC-0003 branch contains 21 commits of unique implementation and tests, with successful CI evidence on that branch's head. Its separate workflow-consolidation branch contains a failing lint run and cancelled tests. These findings contradict a blanket low-risk archive recommendation until the unique work is dispositioned.

Before archive, require:
1. A decision record for each unique branch.
2. A path/blob mapping for every unique file and behavior test for every deliberate port.
3. A clear separation between decision assessment and cryptographic execution authorization.
4. Exact-SHA tests for any selected merge/port.
5. A final branch and consumer/deployment check immediately before archiving.