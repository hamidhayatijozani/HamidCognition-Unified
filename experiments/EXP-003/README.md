# EXP-003 — Replay Determinism and External-Feed Sensitivity

Status: PROTOCOL READY; EXECUTION BLOCKED UNTIL AN IMMUTABLE EXTERNAL-FEED FIXTURE IS AVAILABLE.

Purpose: determine whether replay behavior changes when external market/feed state is reconstructed from a frozen fixture versus read from a live provider.

## Required evidence

- immutable raw fixture
- fixture SHA-256
- provider/source name
- retrieval timestamp
- timezone and interval
- parser version
- source commit SHA
- exact feature configuration
- replay run fingerprints
- live-feed run fingerprints, if live comparison is performed

## Required comparisons

1. fixture → replay A
2. fixture → replay B
3. live/provider snapshot → replay conversion
4. feature/state trajectory comparison
5. missing-field and timestamp perturbation tests

## Rule

No live API result is allowed to silently become experimental ground truth. A live feed may be used for acquisition, but the acquired bytes/data must be frozen before reproducibility claims are made.
