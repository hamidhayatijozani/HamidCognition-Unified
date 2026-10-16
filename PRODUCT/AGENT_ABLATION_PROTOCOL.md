# Agent Ablation Protocol v1.0

Status: **PROPOSED — NOT YET EXECUTED**
Owner: BESAZ / HamidCognition-Unified
Purpose: estimate the incremental operational value of the reasoning-and-control loop while holding tools, data, task distribution, and execution budget fixed.

## 1. Claim under test

The agent's value is the difference between outcome quality with a specified decision policy and outcome quality under a defined baseline policy. Tool availability alone is not evidence of agent value.

For a preregistered task distribution (D), define:

- (S_A): success rate of the full agent.
- (S_B): success rate of a basic planner.
- (S_0): success rate of a direct/linear tool policy.
- (C): total cost under a fixed accounting rule.

Primary effect versus baseline:

```text
Absolute uplift       = S_A - S_0
Relative uplift       = (S_A - S_0) / S_0       when S_0 > 0
Normalized headroom   = (S_A - S_0) / (1 - S_0) when S_0 < 1
Cost-adjusted uplift  = (S_A - S_0) / C
```

Report all applicable measures with confidence intervals. Do not call any of them “AAC” without naming the denominator and task distribution. If baseline success is zero or one, the corresponding ratio is undefined; do not patch it with an arbitrary epsilon without reporting that choice.

## 2. Experimental arms

All arms receive the same task statement, starting repository/environment snapshot, tools, data, permissions, wall-clock limit, tool-call limit, and token/compute budget.

### A — Direct tool execution (no adaptive agent)

- Executes a preregistered direct procedure or fixed action sequence.
- No adaptive replanning after intermediate results.
- Tool outputs are recorded identically to other arms.

### B — Basic agent

- Decomposes the goal into a short plan.
- Chooses the next step from the current result.
- Does not use an explicit root-cause ledger or contradiction register.

### C — Full agent

- Maintains hypotheses with supporting and contradicting evidence.
- Selects tests by expected information gain and cost.
- Tracks dependencies, contradictions, failed approaches, and acceptance criteria.
- Revises the plan after observed outcomes.
- Stops when acceptance criteria pass, the budget is exhausted, or a documented blocker is reached.

The distinction between arms must be implemented as an explicit policy difference, not as unequal tool permissions or unequal budgets.

## 3. Task design and controls

1. Freeze and hash the task set before evaluation.
2. Include easy, medium, and difficult tasks; do not select tasks after seeing outcomes.
3. Randomize task order and arm order where practical.
4. Use equivalent clean snapshots and identical external conditions.
5. Give each arm the same budget. Report both wall-clock and resource use.
6. Use an evaluator that does not know which arm produced an output when feasible.
7. Score outcomes against preregistered acceptance tests and independent evidence, not self-reported completion.
8. Record every intervention, tool action, result, retry, and plan revision.
9. Separate task-level outcomes from repeated attempts; attempts on the same task are not independent samples.
10. Publish failures and missing results as well as successes.

## 4. Metrics

Metrics are reported separately; do not add raw rates with different meanings or units into a single uncalibrated sum.

| Metric | Operational definition | Guardrail |
|---|---|---|
| FDI — Factor Discovery Index | Verified root causes found / root causes independently established in the task set | Root-cause reference set must be established independently; unknown causes remain unknown |
| URR — Uncertainty Reduction Rate | ((U_0-U_f)/U_0), using a preregistered uncertainty measure | Use calibrated probability entropy or a fixed unresolved-question rubric; do not substitute text length |
| HRI — Human Reliance Index | Human interventions per task, plus intervention minutes reported separately | Lower is not automatically better if correctness or safety declines |
| CRC — Contradiction Resolution Capacity | Material contradictions correctly resolved / material contradictions seeded or independently found | A contradiction counts as resolved only when evidence supports a resolution or explicit unresolved status |
| PSI — Plan Success Index | Plans meeting their declared acceptance criteria / plans evaluated | A plan revision is not a new independent task; record plan versions |
| RRA — Recovery Rate After Failure | Failures followed by verified recovery within budget / recoverable failures encountered | Classify unrecoverable failures before scoring |
| IRF — Information Return Factor | Independently judged decision-relevant information gained / action count or action cost | State the unit and blind the evaluator where possible |
| ACR — Adaptive Compression Ratio | Initial plausible hypothesis/search-space size / remaining plausible size | Use a declared counting or entropy method; raw search-space cardinality may be unavailable |
| GAI — Goal Progress | Change in a preregistered task-specific distance-to-acceptance measure | Define the distance before running; do not invent a universal metric across tasks |
| EER — Error Exposure Rate | Independently seeded hidden errors detected / hidden errors seeded | Report false positives and missed errors separately |

A metric with no valid denominator is **N/A**, not zero. A missing ground-truth cause set or uncalibrated uncertainty score must be reported as a measurement limitation.

## 5. Composite score

Do not use the draft expression “sum of FDI, URR, CRC, RRA, IRF, ACR, GAI divided by HRI” as a validated coefficient. Those quantities have different scales; HRI can be zero; and the ratio can become undefined or arbitrarily large.

If a single composite is required, preregister:
- normalization for each component;
- directionality and weights;
- safety/correctness as non-compensable gates;
- missing-data handling;
- sensitivity analysis across reasonable weights.

Always publish the underlying metric vector and primary success-rate uplift alongside any composite.

## 6. Statistical analysis

- Primary endpoint: proportion of tasks passing all preregistered acceptance tests.
- Primary comparison: C versus A; secondary comparisons: B versus A and C versus B.
- Report absolute percentage-point difference, relative difference where defined, and 95% confidence intervals.
- For paired tasks, use paired analysis; use bootstrap resampling at the task level, not at the attempt level.
- For multiple secondary comparisons, control false discovery rate or label analyses exploratory.
- Define minimum meaningful uplift and stopping rules before inspecting outcomes.
- Report results by difficulty and task family without hiding the aggregate.
- Do not infer general agent superiority from one repository or one task family.

## 7. Operational stopping rules

Stop a run when any of the following occurs:
- acceptance criteria pass and evidence is captured;
- the fixed budget is exhausted;
- an external permission, secret, environment, or service is genuinely unavailable;
- a safety or data-integrity invariant is violated.

A stop due to missing access is **BLOCKED**; a completed run with insufficient evidence is **INCONCLUSIVE**; a failed acceptance test is **FAIL**. None may be relabeled PASS.

## 8. Evidence record

Each run must record:

- protocol version and protocol hash;
- repository, branch, source SHA, task-set hash, and environment snapshot;
- arm/policy identifier and configuration;
- start/end time, budgets, tool calls, human interventions, and retries;
- raw task outputs and evaluator results;
- metric calculations, confidence intervals, exclusions, and missing values;
- artifact digest and reproducibility instructions.

The evidence must be bound to the exact source SHA. A successful run on an earlier commit does not verify a later commit.

## 9. Current evidence boundary

This document defines an experiment. It does **not** report that the experiment has run, that an agent uplift has been measured, or that any numeric AAC value is known.

Initial status:
- Protocol authored: pending repository commit verification.
- Arms implemented: UNKNOWN.
- Frozen task set: UNKNOWN.
- Controlled comparison: NOT RUN.
- Agent uplift / AAC: UNKNOWN.
- Product release impact: NONE CLAIMED.

## 10. Acceptance criterion for a positive result

A positive result requires all of the following:

1. The full-agent arm beats the direct baseline on the preregistered primary endpoint by at least the minimum meaningful uplift.
2. The uncertainty interval excludes no uplift under the chosen analysis.
3. The result is not explained by higher budget, extra permissions, easier tasks, or selective exclusions.
4. No non-compensable correctness, security, or data-integrity gate regresses.
5. An independent rerun reproduces the direction of the effect.

Otherwise report **INCONCLUSIVE**, **NO MEANINGFUL UPLIFT**, or **REGRESSION**, as appropriate.
