# BESAZ Mother Memory

## Purpose

Mother Memory stores **attributed model perspectives** about the creator across separate model providers and sessions. It is not a universal profile, personality diagnosis, consciousness store, or source of objective truth.

The system preserves disagreement instead of collapsing different model outputs into one synthetic consensus.

## Architecture

```text
Model export / user-approved assessment
              |
              v
      Provenance + consent gate
              |
              v
     Observation / inference split
              |
              v
       Local private JSON store
       |       |       |       |
    memory  sessions concepts emergence
              |
              v
      Hash-linked audit journal
              |
              v
    Compare / human review / correction
```

The existing BESAZ Awareness hierarchy owns the MEMORY and LEARNING responsibilities. This module provides the first local implementation for cross-model perspective records.

## Data contract

Every assessment records:
- provider, model name and exact model version;
- scope and timestamp;
- directly observed statements or behavior, classified as `OBSERVATION`;
- interpretations, classified as `INFERENCE` or `INTERPRETATION`, each with a basis and bounded confidence;
- strengths, risks, recurring patterns and changes over time;
- evidence references to conversation exports or source records;
- explicit uncertainty and review status.

Model perspectives remain attributed to their source. Similar wording is not treated as agreement. Cross-model comparisons are marked `HUMAN_COMPARISON_REQUIRED`.

## Privacy and governance

- Runtime data defaults to `data/mother_memory/`, which is excluded by the repository's `/data/` ignore rule.
- Set `BESAZ_MOTHER_MEMORY_DIR` to use another private local directory.
- Do not commit real assessments, conversation exports, personal identifiers, or profile snapshots to this public repository.
- Explicit consent is required for every stored assessment.
- Raw transcripts and hidden chain-of-thought are rejected.
- Sensitive-trait inference is out of scope.
- A user can review, dispute, request revision, or delete an assessment.
- The audit journal records event metadata and hashes, not assessment text.
- Local JSON storage is not encrypted and is not a multi-process database. Protect the device and directory with OS-level access controls. Do not expose this store through a public web server.

This first implementation does not automatically read ChatGPT, Claude, Gemini, or other providers' private memories. Each model must export or produce a structured assessment, and the user must explicitly approve its ingestion. No provider-to-provider synchronization is claimed.

## Files

At first initialization, the runtime creates:
- `memory.json`
- `concepts.json`
- `sessions.json`
- `emergence.json`
- `governance.json`
- `manifest.json`
- `audit.jsonl`

The initial release uses the memory and session stores. Concepts remain reserved. The emergence routine only detects exact repeated pattern labels across providers and marks them `REVIEW_REQUIRED`; it does not perform semantic matching or infer a stable trait.

## API

```python
from src.mother_memory import MotherMemory

store = MotherMemory()  # defaults to ignored data/mother_memory/
record = store.record_assessment(payload, consent=True)
records = store.list_assessments()
comparison = store.compare_models()
store.review_assessment(record["assessment_id"], status="DISPUTED")
store.delete_assessment(record["assessment_id"])
audit = store.verify_audit_chain()
```

Allowed review states: `ACCEPTED`, `DISPUTED`, `NEEDS_REVISION`.

## Verification

Run:

```bash
python -m pytest -q tests/test_mother_memory.py
```

The tests use synthetic fixtures only. A passing test suite proves the local storage contract, not the accuracy of any model's assessment or the existence of a live cross-provider connection.

## Maturity boundary

**Implemented in this increment:** local initialization, consent gate, provenance checks, structured assessments, separate model attribution, human review, deletion, and audit-chain verification.

**Not implemented:** provider APIs, automatic conversation ingestion, encrypted-at-rest storage, multi-device synchronization, automatic semantic consensus, psychological diagnosis, or validated longitudinal inference.
