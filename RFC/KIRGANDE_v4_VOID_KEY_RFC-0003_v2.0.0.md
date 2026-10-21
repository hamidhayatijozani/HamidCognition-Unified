# KIRGANDE v4.0 — VOID_KEY / RFC-0003 v2.0.0 Integration Draft

- **Status:** DESIGN DRAFT — NOT YET IMPLEMENTED OR VALIDATED
- **Owner / attribution:** Hamid Hayati Jozani
- **Date:** 2026-10-21
- **Repository:** `hamidhayatijozani/HamidCognition-Unified`
- **Purpose:** Specify an auditable, reproducible governance/evaluation layer without treating a label, score, or narrative as proof of runtime capability.

## 1. Terminology and security boundary

**VOID_KEY is a project label and governance concept, not an authentication credential, cryptographic key, privilege escalation mechanism, or proof that a runtime is active.** Never store secrets in this document, source control, logs, or test fixtures. Actual authorization must be enforced by the Action Gate and the deployment's identity and policy controls.

KIRGANDE / ChaosStabilizer are design components until source code, tests, CI evidence, and runtime observations establish otherwise. This RFC does not claim that any component is deployed, active, secure, commercially accepted, or independently validated.

## 2. Architecture

`Agent → Observable Artifact Layer → Claim Provenance → Epistemic Integrity (HAIS) → Chaos Assessment → Decision Risk (DRS) → Governance Policy → Enforcement → Evidence Ledger → Replay`

The stages are logically separate:

1. **Observable Artifact Model (OAM):** capture user-visible inputs/outputs, tool calls, timestamps, declared configuration, and evidence references. Do not collect private reasoning.
2. **Claim Provenance:** map each material claim to its source, timestamp, artifact hash, and verification status.
3. **Epistemic assessment:** evaluate evidence support and overclaiming.
4. **Chaos assessment:** quantify disagreement/instability from defined observable signals. It is a risk feature, not a truth detector.
5. **Decision risk:** evaluate the impact and uncertainty of the proposed action.
6. **Governance and enforcement:** apply explicit policy and authorization checks; fail closed when required evidence or state is missing.
7. **Evidence Ledger and Replay:** persist inputs, policy/configuration versions, decision, enforcement outcome, and replay result.

Suggested decisions: `ALLOW`, `ASK`, `SANDBOX`, `DENY`. Decision semantics and precedence must be defined by the policy implementation. A high chaos score must never override a mandatory denial or grant authority.

## 3. Observable metrics

All metrics must define their input population, denominator, missing-data behavior, time window, version, and direction. Metrics are not comparable across versions unless their definitions and populations match.

- `EAS = SupportedClaims / TotalClaims`
- `OCR = UnsupportedStrongClaims / TotalClaims`
- `ED = ClaimLevel - EvidenceLevel` only when both levels use a documented, comparable ordinal scale.
- `CPS = 0.35S + 0.35T + 0.30L`, provided S, T, and L are each specified and normalized to [0, 1].
- `NED`, `CQM`, and DRS components `I/A/R/U` require normative definitions before production scoring.
- When `TotalClaims = 0`, EAS/OCR are undefined, not automatically 0 or 1. The policy must explicitly choose a safe handling path.

### 3.1 HAIS candidate formula

The submitted HAIS weights sum to 1.05. To preserve the submitted relative weights, define the baseline:

`HAIS_0 = 0.30 EAS + 0.20(1-NED) + 0.20 CPS + 0.15 CQM + 0.15(1-OCR)`

If every component is validated within [0, 1], then `HAIS_0 ∈ [0,1]`.

For an optional normalized chaos contribution `C_n ∈ [0,1]`, a candidate formula is:

`HAIS = (1 - λ_H) × HAIS_0 + λ_H × C_n`

with `λ_H ∈ [0,1]`. This makes the chaos contribution's meaning explicit. Whether chaos should increase or decrease an integrity score is a research question; do not enable this formula in a release until preregistered tests justify the direction and weight. A safer default is to report `C_n` separately from HAIS.

### 3.2 DRS candidate formula

The submitted DRS weights sum to 1.10. Preserve their relative proportions by normalizing the baseline:

`DRS_0 = (0.30 I + 0.25 A + 0.25 R + 0.20 U) / 1.10`

If all inputs are in [0,1], then `DRS_0 ∈ [0,1]`.

An optional chaos adjustment can be expressed as:

`DRS = (1 - λ_D) × DRS_0 + λ_D × C_n`

where `λ_D ∈ [0,1]`. This is a candidate for evaluation, not a validated risk model. Define each component's semantics and verify monotonicity before operational use. Thresholds must be calibrated against labelled cases and independently evaluated.

## 4. ChaosStabilizer: measurable, not magical

Candidate observable signal:

`ChaosRaw = |Direct - Inverse| × Entropy × ConfidenceProduct`

This formula is usable only after defining:
- the scales and bounds for Direct and Inverse;
- normalized entropy and its sampling population;
- how confidence values are calibrated and combined;
- behavior for missing, stale, adversarial, or contradictory observations;
- normalization from `ChaosRaw` to `C_n ∈ [0,1]`;
- the time window and deterministic snapshot format.

**Do not assume** `lim(t→∞) Chaos(t) = C_const ≠ 0`. Nonzero convergence is neither implied by this formula nor a general stability requirement. If a nonzero floor is desired, specify it as an explicit bounded design parameter and test its effects; do not present it as a theorem. A constant nonzero floor can mask calm conditions and distort thresholds.

Each `ChaosSnapshot` should include schema version, input artifact hashes, window, normalized inputs, computed value, missing-data flags, algorithm version, and timestamp. Replay must use the recorded snapshot and exact configuration, not silently recompute from changed external data.

## 5. Replay metrics

- `RS = IdenticalOutputs / EligibleReplayRuns`
- `RC = CorrectReplayDecisions / EligibleReplayRuns`

Define eligibility, canonical serialization, floating-point tolerances, nondeterministic fields, and the independent reference decision. Report sample size and confidence intervals. Proposed targets `RS ≥ 0.95` and `RC ≥ 0.85` are **provisional acceptance thresholds**, not evidence of achieved performance. A system can repeat the same wrong decision; RS does not establish RC.

## 6. Provisional performance targets

- p95 latency < 500 ms, measured on a specified deployment and load profile.
- False allow / false deny rates ≤ 10%, measured on a labelled evaluation set with explicit definitions.
- Replay stability ≥ 95%.
- Replay correctness ≥ 85%.
- Chaos-related acceptance thresholds: **not set** until scale, calibration, and validation methodology are approved. Do not require `C_const > 0.01` as a security or stability success criterion without evidence.

Every result must include sample size, environment, code commit, configuration hash, test data version, and measurement method. Never convert a target into a claim of achieved performance.

## 7. Adversarial benchmark

The proposed 1,000-case suite must be deterministic, versioned, and partitioned into named categories, including:
- missing and contradictory evidence;
- unsupported strong claims;
- direct/inverse signal disagreement;
- entropy and confidence boundary values;
- stale snapshots and altered configuration;
- replay/timestamp/nonce misuse;
- malformed and oversized input;
- policy precedence and fail-closed behavior;
- service restart and persistence;
- attempts to bypass enforcement.

Store each case's ID, category, input fixture, expected outcome, rationale, and fixture hash. Separate development fixtures from held-out evaluation cases to reduce benchmark overfitting. The count of cases alone is not evidence of quality.

## 8. Minimum test gates

1. Unit tests for every formula, bounds, missing values, and zero denominators.
2. Property tests for output ranges, deterministic calculation, and policy invariants.
3. Replay tests across process restart with pinned inputs/configuration.
4. Enforcement tests proving protected actions cannot execute after `DENY`, unresolved `ASK`, or failed authorization.
5. Adversarial suite with a recorded manifest and per-case results.
6. Independent evaluation of false-allow and false-deny rates.
7. Same-commit CI and artifact provenance.
8. Production validation only with explicit environment access and actual logs; otherwise mark runtime status `UNKNOWN` or `NOT_RUN`.

## 9. Audit record

Each evaluation record should contain:
- RFC/schema version and algorithm version;
- repository, commit SHA, and artifact hashes;
- input and fixture hashes;
- policy/configuration snapshot;
- metric values and undefined/missing fields;
- decision, enforcement result, and replay result;
- environment, timestamp, latency, and error details;
- test status: `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, or `NOT_RUN`.

Do not record private model reasoning, credentials, or unnecessary personal data.

## 10. Acceptance and change control

This document is a design proposal. Before calling RFC-0003 v2.0.0 accepted:
1. approve normative definitions for all variables and thresholds;
2. preregister hypotheses for the effect of chaos on HAIS/DRS;
3. implement the reference calculator and tests;
4. run tests against a pinned commit and publish raw results;
5. independently review security invariants and held-out benchmark results;
6. create a release only after the evidence is reproducible.

## Current evidence status

- GitHub repository and README were inspected before this draft was prepared.
- This file is a specification proposal; it does not prove implementation or runtime activation.
- Formula arithmetic review: submitted HAIS weights total 1.05; submitted DRS weights total 1.10.
- Implementation tests, 1,000-case benchmark, production latency, false-decision rates, and runtime activation: `NOT_RUN` / `UNKNOWN`.
