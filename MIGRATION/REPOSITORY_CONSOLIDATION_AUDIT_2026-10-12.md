# Repository Consolidation Audit — 2026-10-12

**Status:** Read-only inventory and preliminary classification. No source files migrated and no repositories archived by this audit.
**Audit branch base:** `fbb38ed138176e850c43e94cc6c8befb6f587dbf` on `main`.
**Evidence source:** GitHub repository metadata, default-branch recursive trees, current README files, and default-branch HEAD commits inspected on 2026-10-12.
**Important boundary:** This is not a claim that all tests were run. Repository tree presence, a README statement, or an old successful CI run is not proof of current runtime correctness.

## Executive finding

The accessible owner inventory contains **14 repositories**, matching the report's repository count. The proposed target of exactly four repositories is **not safe to execute as written**: at least one apparent “old” repository (`vahshi-`) is now an active, unrelated automotive diagnostics project (Iran AutoDiag Platform / IADP). `ki-is-koni` appears to contain a separate RIPE RIS routing-analysis artifact and is not established as part of the HamidCognition product family. `hhj-cognitive-safety-gateway` describes Sbat, a decision-assessment product that explicitly does not execute the proposed action; that is not automatically equivalent to Action Gate. `EURUSD-5M-ForecastHamid` contains JavaScript modules and tests whose behavior is not yet shown to be equivalent to the Python ClaimLab implementation.

**Recommendation:** do not archive ten repositories in one operation. Keep distinct products distinct; archive only historical repositories after checking unique files, source provenance, downstream references, and recovery instructions. Archive is reversible, deletion is not the proposed plan.

## Repository inventory and preliminary disposition

HEAD values below were read from the default branch on 2026-10-12 before the later merge of `HamidCognitionEngine` PR #2. Its current post-merge HEAD is `9da718d1ba8964a4e4ae3f0f5e3455c6c26cdecb`; see [the branch audit](PHASE_2_BRANCH_AUDIT_2026-10-12.md).

| Repository | Default branch | Observed HEAD | Preliminary disposition | Rationale / open condition |
|---|---|---|---|---|
| `HamidCognition-Unified` | `main` | `fbb38ed138176e850c43e94cc6c8befb6f587dbf` | KEEP — canonical BESAZ / Action Gate integration | Existing migration lineage and product evidence live here. Do not treat copied files as proof of semantic equivalence. |
| `EURUSD-5M-Forecast` | `main` | `749d84a6a12240e55fd13a84b6a93918f1abcc8c` | KEEP — canonical ClaimLab research | Separate research purpose. Current HEAD's live-research supervisor was skipped; prior-SHA success does not validate current HEAD. |
| `vahshi-` | `main` | `d273477f609a0c791d44cd9cbfe150dbfe1edbfd` | KEEP — independent active product | README and tree show active IADP code: OBD-II, CAN, ISO-TP, UDS, simulator, replay and tests. Must not be archived as legacy HamidCognition code. |
| `epistemic-filter` | `master` | `bcd9f9b9c7d59837e3c34d7df82876329911f0a2` | KEEP — active research prototype / reusable library | Has implementation, tests, RFCs and a recent 2026-10-11 commit. Heuristic screening is not a truth oracle or security boundary. |
| `hhj-cognitive-safety-gateway` | `main` | `c621fd983e5b6cd240c803845b1ec731921dcf62` | KEEP SEPARATE pending product-boundary review | README calls the product Sbat and says it assesses decisions but does not execute actions. Do not merge it into Action Gate without API/contract and product-boundary evidence. |
| `ki-is-koni` | `main` | `6e968cef42caa639f78c6c6c696b2616e216ae23` | HOLD — purpose unresolved | Only README and LICENSE appeared in the tree; README content appears to be Python code about RIPE RIS routing prefixes. Treat as a separate project until ownership and intent are clarified by evidence. |
| `EURUSD-5M-ForecastHamid` | `main` | `b7e5e505d562d0fa81080a4f31cc453d6ee38039` | HOLD — legacy candidate, not yet archive-ready | JavaScript forecast engine, market features, model ensemble, trader intelligence and tests are present. The 48-hour positive-net-profit ranking described by the old trader module differs from the newer desired 24-hour forecast-error leaderboard. Port/test behavior before declaring it redundant. |
| `epistemic-filterr` | `main` | `022e82975f098037787fb358126143c2c8b18f4a` | ARCHIVE CANDIDATE after reference check | Default tree contains only README.md, whose content embeds a Python implementation. Verify there are no unique references, releases, consumers or uncommitted external copies before archiving. Do not delete. |
| `HamidCognition` | `master` | `6909b5426a4831eeff951555f196819c9a6fe3ec` | HISTORICAL ARCHIVE CANDIDATE | README describes a historical source artifact. Contains distinct EUR/USD scripts, transfer package and reports. Preserve repository and Git history; ensure unique artifacts are discoverable from canonical lineage docs before archive. |
| `HamidCognitionEngine` | `master` | `3241cdb3ae9ea152d805234c57ebabaf5efe8204` | HISTORICAL ARCHIVE CANDIDATE, with unique-source gate | Contains a materially different absolute P/S/T transition model, `forex_trading_bot.py`, `run_hamid.py`, `android_python_guide.md`, sample data and trade log. Do not claim these are behaviorally represented by the normalized engine. Preserve source provenance and test/document the unique artifacts before archive. |
| `hamidcognition-web` | `main` | `f4fd03b9cf3fbeccdd52131747399d3713d729a6` | HISTORICAL ARCHIVE CANDIDATE | README says historical UI lineage and that the source app was integrated where practical. Verify the specific Flask behavior and dependencies are represented or explicitly marked as not migrated. |
| `hamidcognition-realtime` | `main` | `7217fe47da548b0a084ffc4983d3983e17691c32` | HISTORICAL ARCHIVE CANDIDATE, preserve variant | Realtime engine differs in initial state, thresholds, outputs and input transformation. Keep its lineage and do not flatten into the normalized baseline without behavioral tests. |
| `hamidcognition-v0-max` | `main` | `7da846315ea56a6d1b187546b47f68ffe291c004` | HISTORICAL ARCHIVE CANDIDATE | Existing migration docs establish exact duplicate blobs for several files versus `hamidcognition-complete`; verify the remaining unique API, governance, workflow and Docker files before archive. |
| `hamidcognition-complete` | `main` | `383037f85830f69a9dbd5f21f8d06526bc67d964` | HISTORICAL ARCHIVE CANDIDATE | Existing migration docs establish exact duplicates for several files versus `v0-max`, but unique mobile/creative/platform components remain to be checked. It is not safe to infer whole-repository equivalence from a few matching blobs. |

### Additional archive blocker found after initial inventory

`hamidcognition-complete` has a **draft, untagged release** named `W`, created 2025-12-27, with no release body: [draft release](https://github.com/hamidhayatijozani/hamidcognition-complete/releases/tag/untagged-370108c16429029ca3a5). Its intent and whether it should be retained or closed must be resolved before archiving that repository.

## Verified facts vs unknowns

### Verified from GitHub metadata/tree/README inspection
- 14 repositories are accessible under the owner.
- All 14 currently report `archived: false`.
- `vahshi-` has an active IADP-oriented source tree and CI workflow.
- `epistemic-filter` has implementation, tests, RFCs, evaluation files and a recent commit.
- `hhj-cognitive-safety-gateway` has a Sbat product/service/test tree and CI workflow.
- `epistemic-filterr` has only one tracked file in its current tree: `README.md`.
- The six older HamidCognition-family repositories are already described in the Unified repository's migration docs as historical source lineages, but that documentation does not prove every behavior or file has been migrated.

### UNKNOWN / not yet established
- Whether the four reports described in the external local path exist there and whether their contents match the summary. That local filesystem is not available through this GitHub audit.
- Whether every unique file from the six historical HamidCognition repositories has an equivalent, tested counterpart in Unified.
- Whether external deployments, consumers, bookmarks, packages, secrets, releases, or automation depend on any archive candidate.
- Whether the current HEAD of every repository passes its required tests.
- Whether the Python and JavaScript forecast implementations are behaviorally equivalent.
- Any real-market predictive edge or profitability.

## Safe execution sequence

1. Freeze and record current HEADs and default branches (done for this inventory).
2. Diff source trees and blob SHAs for each archive candidate against canonical paths.
3. For every unique file, classify it as: migrated and tested; intentionally not migrated with reason; or unresolved.
4. Check workflows, releases, packages, deployment references, external integrations and open PRs.
5. Run the relevant tests on the exact candidate commit and, where needed, add behavior-preservation tests.
6. Publish an evidence-backed archive manifest with each repository's HEAD and rollback/unarchive instructions.
7. Archive only the explicitly classified historical candidates, one at a time, after the above gates. Never delete repositories or rewrite source history as part of this plan.

## Stop conditions

Stop before archive if a unique executable artifact lacks a disposition, a required test fails, a consumer/deployment is unresolved, provenance cannot be established, or the repository contains an active product unrelated to the consolidation scope.
