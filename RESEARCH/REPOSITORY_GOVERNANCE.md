# Repository Governance & Citation Map

**Project:** HamidCognition
**Canonical research record:** `HamidCognition-Unified`
**Originator:** Hamid Hayati Jozani
**Record date:** 2026-09-15

## Purpose

This document defines how the public HamidCognition repositories relate to one another and how a reader should cite or interpret them.

The repositories are not assumed to be equivalent, interchangeable, or equally mature. Historical repositories remain part of the provenance record unless explicitly removed for a documented reason.

## Repository roles

| Repository | Role | Interpretation |
|---|---|---|
| `HamidCognition-Unified` | Canonical research/provenance record | Current integration point for claims, experiments, lineage, unknowns and research infrastructure |
| `hhj-cognitive-safety-gateway` | HHJ-CSG historical/technical line | Gateway architecture, governance concepts and prior consolidation work |
| `epistemic-filter` | HHJ-CSG / epistemic governance line | POC, RFCs, metrics and execution-governance research |
| `hamidcognition-realtime` | Real-time trading experiment | Historical implementation and experimental evidence; not automatically validated by its README claims |
| `hamidcognition-complete` | Historical integration attempt | Preserved as an integration-stage artifact |
| `hamidcognition-v0-max` | Historical V0-Max architecture | Earlier implementation lineage; claims must be checked against its actual artifacts |
| `HamidCognition` | Foundational P/S/T and EUR/USD line | Earlier engine, transfer package and simulation artifacts |
| `HamidCognitionEngine` | Simulation lineage | Earlier inferred simulation of P/S/T transition logic |
| `hamidcognition-web` | Web/UI lineage | Earlier live-dashboard implementation |
| `vahshi-` | Historical/experimental trading lineage | Preserve as historical evidence unless independently superseded |

## Canonicalization rule

A repository is not made canonical merely because it is newer, larger, cleaner, or called `complete`.

Canonical status means that the artifact has an explicit place in the current research record and that its epistemic status is documented. Historical implementations remain citable as historical artifacts.

## Citation rule

For a current project-level reference, cite:

`Hamid Hayati Jozani — HamidCognition-Unified`

and include the exact commit or release when reproducibility matters.

For a historical implementation, cite the specific repository and exact commit/path instead of silently treating it as the current canonical implementation.

## Evidence rule

The following are distinct:

- repository existence ≠ scientific validation
- commit history ≠ proof of legal ownership
- benchmark text ≠ independently reproduced benchmark
- implementation ≠ production readiness
- candidate novelty ≠ demonstrated novelty

Claims marked `VERIFIED` require an evidence path in the Unified research record.

## Legacy repository rule

Legacy repositories should not be rewritten to erase their history. Their README may be updated to identify their role, current status, and canonical research record, while preserving the underlying code and commit history.

## Issue rule

Open issues are not closed merely for repository cleanliness. An issue containing a hypothesis, design, contradiction, anomaly, or historical proposal should be migrated or cross-referenced before closure.

## Reproducibility minimum

A reproducible claim should identify, where available:

`dataset → preprocessing → parameters → seed → code commit → environment → execution → output → analysis → claim`

Missing links remain explicitly unknown.
