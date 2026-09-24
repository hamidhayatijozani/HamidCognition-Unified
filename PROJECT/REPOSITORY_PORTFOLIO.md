# Repository Portfolio and Execution Registry

Date: 2026-09-24
Status: ACTIVE / EVIDENCE-FIRST

This registry records the GitHub projects currently visible to the connected account and defines their role in the wider HamidCognition program. Presence of a repository is evidence of repository existence, not evidence that its claims, code, benchmarks, or production status are correct.

## Canonical integration target

- hamidhayatijozani/HamidCognition-Unified
- Default branch: main
- Role: canonical research/integration spine.

## Current project surfaces

| Repository | Observed role | Integration rule |
|---|---|---|
| HamidCognition | legacy/core lineage | inspect, preserve provenance, integrate selectively |
| HamidCognitionEngine | engine lineage | inspect interfaces and reusable implementation |
| hamidcognition-web | web surface | integrate only after interface/evidence checks |
| hamidcognition-realtime | realtime surface | integrate only after runtime tests |
| hamidcognition-v0-max | historical V0-Max lineage | treat as historical evidence, not production proof |
| hamidcognition-complete | integration candidate | inspect against canonical repo |
| ki-is-koni | private project surface | preserve boundary; integrate only verified artifacts |
| epistemic-filter | epistemic filtering lineage | map to ClaimLab / evidence integrity |
| hhj-cognitive-safety-gateway | governance/safety lineage | map to HHJ-CSG and action gating |
| epistemic-filterr | secondary/duplicate-looking surface | compare before any consolidation |
| HamidCognition-Unified | canonical integration spine | primary destination for verified shared research |

## Execution rule

No repository is deleted, renamed, declared canonical, or marked production-ready solely from a narrative report. Every such transition requires a traceable chain:

repository → ref → commit → artifact → test → workflow run → result.

When evidence conflicts, the conflict is retained and recorded rather than silently resolved.

## Immediate engineering spine

OBSERVATION → REPRESENTATION → STATE → TRANSITION → EVIDENCE ALIGNMENT → DECISION → ACTION → OUTCOME → REPLAY / UPDATE

The State Transition Integrity (STI) hypothesis is the current cross-line experimental bridge. It remains a hypothesis until independent empirical testing supports or falsifies it.
