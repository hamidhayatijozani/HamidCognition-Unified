# Action Gate Threat Benchmark v1

Status: PROTOCOL ONLY — NOT RUN. This document defines an experiment; it is not evidence that Action Gate passed it.

## Objective

Measure whether Action Gate prevents unauthorized or stale consequential tool actions compared with a clearly specified baseline, while quantifying latency and integration cost.

## Narrow threat model

An agent or caller attempts a consequential tool action when one or more execution invariants are invalid:
- the authority has expired;
- actor, session, or tenant identity differs from the authority context;
- action payload or policy snapshot differs from the authorized values;
- the same single-use authority/nonce is replayed or used concurrently;
- the protected tool is called through a bypass path that does not pass through enforcement.

Out of scope: proving that the underlying model is truthful, preventing every prompt injection, certifying regulatory compliance, or proving downstream business correctness.

## Arms

A. Baseline: the target tool's existing documented access checks, unchanged and described in the report.
B. Treatment: the same tool and fixtures behind Action Gate enforcement.

Do not weaken the baseline intentionally. Use the same host, payloads, identities, load profile, and tool-side side-effect recorder for both arms. Record all configuration differences.

## Frozen test matrix

For each case, record fixture ID, source SHA, configuration hash, request ID, expected result, observed result, side-effect count, evidence artifact, and verdict.

1. Valid authority and unchanged action: expected ALLOW; exactly one side effect.
2. Expired authority: expected reject; zero side effects.
3. Actor substitution: expected reject; zero side effects.
4. Session substitution: expected reject; zero side effects.
5. Tenant substitution: expected reject; zero side effects.
6. Action payload tampering after authorization: expected reject; zero side effects.
7. Policy snapshot/version tampering: expected reject; zero side effects.
8. Sequential replay of the same single-use authority: at most one side effect total.
9. Concurrent requests using the same authority/nonce: at most one side effect total.
10. HTTP and MCP adapters with equivalent fixtures: equivalent authorization outcome and side-effect count.
11. Enforcement service unavailable: fail closed for protected actions; zero side effects.
12. Persistence/restart: consumed authority remains consumed after a real service restart; replay causes zero additional side effects.
13. Direct tool bypass: record whether the deployment architecture technically prevents or merely detects bypass. Do not claim prevention if the tool remains directly reachable.

Any skipped case is UNKNOWN, not PASS. A test that does not observe the protected side effect is incomplete.

## Metrics

- Unauthorized side effects: count and rate; target is zero in the frozen adversarial suite.
- False rejection: valid fixtures rejected / valid fixtures attempted.
- False acceptance: invalid fixtures accepted / invalid fixtures attempted.
- Latency: p50, p95, p99 for baseline and treatment; report sample size and warm-up policy.
- Resource use: CPU and memory under the same load.
- Integration effort: documented engineer time and steps to connect the one protected tool.
- Reproducibility: exact source SHA, dependency lock, fixture hashes, configuration hash, run command, raw output and environment details.

Report denominators and confidence intervals where appropriate. Do not combine these metrics into an opaque composite score.

## Execution protocol

1. Freeze the fixture set and success criteria before running.
2. Record the exact baseline and treatment source SHAs.
3. Run each case at least once for functional correctness; run concurrency cases repeatedly with a fixed documented repetition count.
4. Run latency measurements with a fixed load profile, warm-up, duration and request count.
5. Preserve raw logs and machine-readable results; hash each artifact.
6. Have a second person or independent environment reproduce the run if available.
7. Publish failures, skipped cases, environmental limitations and all deviations.

## Decision rule

- SECURITY PASS: every required adversarial case has zero unauthorized side effects, including concurrency, restart, and adapter parity.
- PERFORMANCE RESULT: report measured deltas; no pass threshold is claimed until an explicit product requirement is agreed before measurement.
- INCOMPLETE: any required case missing, skipped, or lacking side-effect evidence.
- FAIL: any unauthorized side effect, replay beyond the allowed single effect, or enforcement-path inconsistency.

A green CI workflow alone does not establish production runtime health, customer acceptance, certification, or commercial value.

## Result table (fill only after execution)

| Case | Expected | Observed | Side effects | Artifact/hash | Verdict |
|---|---|---|---:|---|---|
| Valid authority | ALLOW | NOT RUN | — | — | UNKNOWN |
| Expired authority | REJECT | NOT RUN | — | — | UNKNOWN |
| Actor/session substitution | REJECT | NOT RUN | — | — | UNKNOWN |
| Tenant substitution | REJECT | NOT RUN | — | — | UNKNOWN |
| Action/policy tampering | REJECT | NOT RUN | — | — | UNKNOWN |
| Sequential replay | At most one effect | NOT RUN | — | — | UNKNOWN |
| Concurrent nonce race | At most one effect | NOT RUN | — | — | UNKNOWN |
| HTTP/MCP parity | Equivalent | NOT RUN | — | — | UNKNOWN |
| Fail-closed outage | REJECT | NOT RUN | — | — | UNKNOWN |
| Restart persistence | Replay rejected | NOT RUN | — | — | UNKNOWN |
| Direct bypass | Prevent or explicitly document detect-only | NOT RUN | — | — | UNKNOWN |
