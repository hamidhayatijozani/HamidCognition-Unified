# From Agent Intent to Enforced Action: An Experimental Study of Execution-Time Governance at the MCP Boundary

**Author:** Hamid Hayati Jozani  
**Status:** Research draft / protocol-first. No empirical result is claimed.  
**Implementation under study:** HamidCognition Action Gate v1.1.1  
**Release source commit:** `e9ea7565f4ddea91f5c45104237bd20564c80894`  
**Artifact SHA-256 recorded in repository:** `517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791`

## Abstract

Tool-using AI agents may decide in one context and attempt execution later under a changed context, stale authority, duplicated request, or a path that bypasses the intended policy boundary. This study proposes a reproducible adversarial evaluation of execution-time governance for Model Context Protocol (MCP) tool calls. It compares a direct agent-to-tool baseline with a path in which an enforcement gateway validates authorization before forwarding a protected operation.

The protocol tests whether the governed path rejects unauthorized, expired, replayed, tampered, cross-context, and bypass attempts while preserving authorized actions. Each run records the exact software revision, scenario, configuration, raw response, downstream side effect, evidence reference, and replay outcome. Documented design claims are distinguished from behavior observed in controlled experiments. The study does not assume the gateway prevents all attacks, or that anomaly detection and independent telemetry are present.

**Current status:** protocol and claim register drafted; empirical results pending. Every outcome remains UNKNOWN until the test is executed against the pinned release and raw evidence is retained.

## 1. Research question

Can a pre-execution authorization boundary bind a protected tool operation to the current tenant, actor, session, action identity, policy decision, and unexpired single-use authority, and reject invalid attempts without allowing the downstream side effect?

### Subquestions

1. Does the governed path preserve authorized-action availability while rejecting unauthorized actions?
2. Are expired or replayed execution authorities rejected, including after process restart?
3. Do action, tenant, actor, session, or policy mutations invalidate authorization?
4. Can a caller invoke the downstream tool without passing through the configured enforcement boundary?
5. Can an independent reviewer reconstruct the decision and compare it with the observed side effect?
6. Which failures remain outside the gateway's protection, including compromised downstream tools and uninstrumented bypass paths?

## 2. Falsifiable hypotheses

- **H1 — Authorization:** unauthorized actions produce no protected downstream side effect.
- **H2 — Single-use authority:** replaying a consumed authority produces no second side effect.
- **H3 — Context binding:** mutating a bound field after authorization causes execution to be rejected.
- **H4 — Expiry:** expired authority is rejected.
- **H5 — Fail-closed evidence:** if required evidence reservation or persistence is deliberately unavailable, the protected action does not execute.
- **H6 — Bypass resistance:** when the deployment contract is correctly applied, direct attempts outside the gateway are blocked by the actual network/credential boundary.
- **H7 — Audit reproducibility:** a reviewer can correlate scenario, decision, authority, downstream outcome, and retained evidence without relying only on narrative logs.

A failed hypothesis must be reported, not hidden. A test that was not run or lacks raw evidence is UNKNOWN, not PASS.

## 3. Experimental design

Compare two paths with the same test tool and inputs:

- **Baseline:** test harness/agent → protected tool.
- **Governed:** test harness/agent → Action Gate → protected tool.

The downstream tool must expose an observable side effect, such as a uniquely identified test record. Use an isolated test tenant and synthetic data. Do not test production systems without explicit authorization.

Record release tag, source commit, artifact digest, runtime/container digest if applicable, configuration and policy hashes (never secrets), harness/dependency versions, scenario ID, UTC timestamps, raw request/response, downstream side-effect record, and evidence ID.

The protocol proposes at least 30 attempts per non-race scenario for an initial repeatability screen. Concurrency cases require separate records of concurrency level and every observed side effect. These are proposed procedures, not completed runs.

## 4. Adversarial scenarios

1. Authorized action (positive control).
2. Unauthorized action.
3. Expired authority.
4. Reuse of a consumed authority / replay.
5. Mutation of action identity or payload after authorization.
6. Tenant, actor, or session mismatch.
7. Policy-version/hash mismatch.
8. Required evidence store unavailable or reservation failure.
9. Process restart followed by authority replay.
10. Concurrent duplicate execution attempts against a single-use authority.
11. Direct downstream bypass using the actual deployment credentials and network topology.
12. Independent reviewer reconstruction and evidence replay.

Measure both the gateway response and whether the downstream side effect occurred. A DENY response alone is insufficient if the side effect still occurs.

## 5. Outcomes and analysis

Primary outcome: count of invalid attempts that produce a protected downstream side effect.

Secondary outcomes: authorized-action success rate; rejection rate by attack class; duplicate side effects under concurrency; evidence completeness and replay agreement; latency overhead (p50/p95/p99) under a stated load; false rejection rate on authorized controls; and failure behavior when dependencies are unavailable.

Report numerator, denominator, exact configuration, and confidence intervals where appropriate. Do not combine materially different attack classes into a single headline score. Do not infer security from a small sample alone.

## 6. Evidence discipline

- **PASS:** predefined acceptance condition observed and supported by retained raw evidence.
- **FAIL:** acceptance condition violated.
- **UNKNOWN:** not executed, environment unavailable, or evidence insufficient.
- **NOT APPLICABLE:** excluded with written rationale.

Documentation, source inspection, CI status, and live behavioral experiments are different evidence types. One cannot silently substitute for another.

## 7. Limitations

The evaluation covers only the pinned implementation, harness, topology, configuration, and scenarios. It cannot establish universal agent safety, correctness of arbitrary customer policies, downstream correctness, resistance to all compromised-host attacks, business ROI, regulatory certification, or behavioral anomaly detection unless those are separately implemented and measured.

## 8. Current results

**No empirical results are reported yet.** See `EVIDENCE_MATRIX.md`, `EXPERIMENT_PROTOCOL.md`, and `CLAIMS_REGISTER.md`. This paper is not ready for submission or sale as a completed experimental study until the protocol is executed and evidence reviewed.

## 9. Provenance

Repository: https://github.com/hamidhayatijozani/HamidCognition-Unified  
Release: https://github.com/hamidhayatijozani/HamidCognition-Unified/releases/tag/action-gate-v1.1.1

The immutable release source and digest above identify the intended study target. The mutable `main` branch is not a substitute for the release artifact. Any deviation from the pinned target must be recorded as a separate experiment.