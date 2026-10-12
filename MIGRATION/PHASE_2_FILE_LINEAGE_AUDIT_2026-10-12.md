# Phase 2 — File-Level Lineage Audit (2026-10-12)

**Status:** Static Git-tree/blob comparison. No source code executed by this audit; no files migrated or archived.
**Comparison base:** default branches observed on 2026-10-12. Exact Git blob SHA equality proves identical file content only; it does not prove equivalent behavior or a successful runtime.

## Results

### Six historical HamidCognition repositories vs HamidCognition-Unified

| Source repository | Source blobs | Exact same path + blob in Unified | Source blob SHA found somewhere in Unified | Interpretation |
|---|---:|---:|---:|---|
| `HamidCognition` | 13 | 0 | 2 | Some engine/trading artifacts exist under different integrated paths, but 10+ source files need explicit mapping or an intentional-not-migrated decision. |
| `HamidCognitionEngine` | 11 | 1 | 2 | Canonical engine lineage exists, but unique `forex_trading_bot.py`, `run_hamid.py`, Android guide, sample data and trade log are not present as matching blobs. |
| `hamidcognition-web` | 6 | 0 | 1 | Dashboard template is present under an integrated path; the original `app.py` differs from current same-name applications. Preserve behavioral differences. |
| `hamidcognition-realtime` | 16 | 0 | 8 | Several real-time source files are exact blobs under integrated paths, including the realtime cognition implementation. This supports lineage preservation, not proof of tests passing. |
| `hamidcognition-v0-max` | 21 | 0 | 6 | Core behavior/model/feed/config artifacts have exact integrated blobs; unique API server, governance/RFC, Docker/compose, workflows and tests still need dispositions. |
| `hamidcognition-complete` | 17 | 0 | 6 | Several shared runtime/model/feed/template files have exact integrated blobs; unique mobile and creative-generator files plus deployment artifacts remain to be classified. |

**Important:** “Source blob SHA found somewhere” can include a file moved to a different path. “No same path + SHA” does not mean “not integrated.” Conversely, a README or lineage map is not a substitute for an explicit disposition of each unique executable file.

### Forecast prototype comparison

| Source | Target | Exact blob overlap | Decision |
|---|---|---:|---|
| `EURUSD-5M-ForecastHamid` (JavaScript) | `EURUSD-5M-Forecast` (Python) | 0 blobs across 13 source files | Do not call it redundant yet. Port behavioral invariants and compare timestamp handling, resolution, trader ranking, metrics and tests before archive. |

The older JavaScript trader-intelligence design ranks closed trades over a rolling 48-hour window and filters on positive net profit. The newer requested research design ranks forecasters by error over the previous 24 hours. These are different contracts, not interchangeable implementations.

### Epistemic Filter comparison

- `epistemic-filter` has 25 tracked blobs in its default tree; `HamidCognition-Unified` contains 522 tracked blobs.
- Four source blobs were found somewhere in Unified, including several RFCs under `integrated/research/epistemic-filter/`.
- The implementation, evaluation dataset, test files, workflow and multiple RFC/POC files are not exact-blob matches in Unified.
- Decision: keep `epistemic-filter` as an active independent prototype. If its behavior is to be consumed by Unified, port the missing tests and runtime contract deliberately; do not archive it based on copied RFCs.

### Sbat / cognitive-safety-gateway comparison

- `hhj-cognitive-safety-gateway` has 22 tracked blobs in its default tree; none are exact blob matches in Unified.
- Its Sbat service, evaluator, risk, red-team, consensus, ledger, report and tests have distinct files and an explicit assessment-only product boundary.
- Decision: keep separate until a product/contract review establishes a concrete integration boundary. A shared theme (“AI safety”) is not sufficient reason to merge codebases.

## File-disposition gate for every archive candidate

Every source blob must be assigned one of these labels before archive:

1. **MIGRATED_EXACT** — matching blob SHA exists in the canonical tree and is linked in the manifest.
2. **MIGRATED_CHANGED** — a deliberate port exists, with source/target references and a behavior-preservation test.
3. **HISTORICAL_ONLY** — not migrated; retained in the source repository/history with a written reason.
4. **GENERATED_OR_TRANSIENT** — bytecode/cache or generated output, excluded from canonical source with rationale.
5. **UNRESOLVED** — no disposition; blocks archive.

No repository should be archived while any required executable artifact is `UNRESOLVED`, or while current consumers/deployments are unknown.

## Next actions

1. Build a path-and-blob manifest for each of the six historical repositories, including all unmatched files.
2. Add explicit links from `MIGRATION/LINEAGE.md` to that manifest.
3. Port missing behavioral tests before making semantic-equivalence claims.
4. Check workflows, releases, deployments, open PRs, package references and external consumers.
5. Re-check current HEADs and exact-SHA CI evidence immediately before any archive operation.
