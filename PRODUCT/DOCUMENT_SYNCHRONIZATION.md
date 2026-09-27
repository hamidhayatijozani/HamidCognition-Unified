# Semantic Document Synchronization

## Purpose

The repository contains executable product behavior, tests, GitHub Actions evidence, release metadata, security boundaries, and customer-facing documentation. These artifacts must not silently drift apart.

The Semantic Document Synchronization Layer (SDS) makes documentation state-aware. It does not blindly rewrite prose. It tracks which claims depend on which repository sources and evidence, classifies changes, and applies only deterministic updates automatically.

The design is intentionally similar to goalball: components do not need a complete visual picture. They emit reliable signals, and the shared state lets other components react to the position of the system.

## Operating model

source -> evidence -> semantic state -> document dependency -> action

Sources include code, tests, release metadata, workflow results, and evidence records.

A dependency entry declares the claim or document surface, source paths, evidence required to keep it current, and permitted synchronization mode.

## Synchronization modes

### AUTO

Safe, deterministic facts may be updated automatically: product version, release tag, source commit, generated evidence identifiers, and machine-readable state fields.

### PROPOSE

Semantic prose changes are detected and proposed through a pull request. The system does not silently invent wording.

### BLOCK

Commercial, legal, licensing, payment, regulatory, or customer-transaction claims are never rewritten automatically. The synchronizer marks them stale or blocked until a human-controlled evidence update is made.

## Claim lifecycle

CURRENT -> STALE -> REVALIDATE -> CURRENT

A source change alone does not prove that a claim became false. It proves that the previous evidence binding is no longer sufficient. The system therefore reports evidence drift instead of pretending to understand semantics it cannot prove.

## Current v1 scope

Version 1 performs dependency-map validation, source fingerprint calculation, deterministic release/version consistency checks, stale-claim detection, machine-readable synchronization state generation, CI enforcement, and a safe generated status document.

It deliberately does not use an LLM to rewrite arbitrary repository prose.

## Security boundary

SDS is advisory to product behavior. It cannot grant execution authority, change Action Gate policy, alter customer entitlements, or mark a commercial transaction as paid.

A green SDS check means documentation is synchronized with the evidence rules declared in the dependency map. It does not mean the underlying product claim is universally true.

## Generated state

The machine-readable state is written to evidence/document-sync-state.json during CI. CI may expose it as an artifact. It is not a substitute for the source evidence itself.

## Acceptance

The Product Gates workflow should run the synchronizer after checkout and before release-readiness assertions. A synchronization failure must prevent a release from being described as documentation-consistent.
