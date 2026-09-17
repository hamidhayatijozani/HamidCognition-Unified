# EXP-005 — Adversarial Evidence-Gate Validation

Status: PRE-REGISTERED / EXECUTED IN CI

Question: can the EXP-004 evidence validator reject artifacts whose declared interpretation conflicts with the underlying evidence, rather than merely recognizing the canonical result?

Acceptance requires: canonical artifact accepted; forged survival label rejected; forged aggregate rejected; inconsistent snapshot delta rejected; forged derived delta rejected; overlapping snapshots rejected; future-feature contamination rejected; malformed source fingerprint rejected; and a coherent synthetic survival artifact accepted with `SURVIVES_PRELIMINARY` plus `BLOCKED_PENDING_INDEPENDENT_REPRODUCTION`.

`FALSIFIED` is a scientific interpretation of an evaluated claim. `FAILED` is a process or execution failure. `VALIDATED(FALSIFIED)` means the validator established that an artifact satisfies the pre-declared rules for a falsification result. It does not mean the claim is universally false.

Scope: PASS establishes resistance to this registered mutation set and demonstrates that interpretation is derived from evidence fields. It does not prove completeness, cryptographic provenance, or universal validator correctness.
