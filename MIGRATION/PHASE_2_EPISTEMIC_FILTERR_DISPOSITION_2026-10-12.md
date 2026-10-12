# Phase 2 — epistemic-filterr Disposition Audit (2026-10-12)

## Verified state

- Repository: https://github.com/hamidhayatijozani/epistemic-filterr
- Default branch: main at 022e82975f098037787fb358126143c2c8b18f4a.
- The current tree contains only README.md. The README embeds a 204-line Python prototype; it is not a normal importable module in this repository, and no tracked test suite or package metadata was found in the current tree.
- The embedded code defines claim levels, jump detection, failure-mode scoring, integrity scoring, weakest-link selection, epistemic distance, verdict selection, and recovery recommendations. It includes Persian keyword lists for overgeneralization, category error, and insufficient evidence.
- The current epistemic-filter repository has an executable module, tests, RFCs and evaluation fixtures. Its API is a per-claim heuristic evaluator with evidence/scope/source metadata and English-oriented patterns.

## Non-equivalence finding

The two projects overlap in purpose, but the code is not byte-identical and the interfaces are different. In particular, the README-embedded prototype's sequential claim-level jump detection and Persian pattern set are not proven to exist in the current implementation. Do not call epistemic-filterr a redundant duplicate solely because it has only one tracked file.

## Recommended disposition

**ARCHIVE CANDIDATE, not yet approved for archive.** Before archiving:

1. Decide whether the Persian heuristics and sequence-level jump detection are still desired.
2. If desired, port them as a separately tested module/feature into epistemic-filter, preserving the old README blob SHA and adding regression tests for each heuristic.
3. If intentionally not desired, record that decision in the main lineage manifest.
4. Verify no external references, packages, releases, issues, or consumer links rely on this repository. The current branch query returned only main; that alone does not prove there are no external consumers.
5. Archive only after a final HEAD re-check. Do not delete the repository or its history.

## Safety boundary

The prototype is a heuristic screening tool, not a truth oracle, calibrated probability model, or security enforcement boundary. Any port should retain that limitation in its API and documentation.