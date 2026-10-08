# Agency Decomposition Framework v1.0

Status: PROPOSED — NOT YET EXECUTED
Owner: BESAZ / HamidCognition-Unified

This document upgrades the Agent Ablation Protocol from measuring whether an agent is useful to measuring where measurable capability comes from.

## 1. Claim under test

For a fixed task distribution and environment:

- Ω = admissible execution trajectories
- Ω* = trajectories satisfying the goal and all non-compensable correctness/safety constraints
- p0 = P0(Ω*) baseline success probability
- pA = PA(Ω*) agent success probability

The agent is modeled as a policy-induced redistribution over trajectories.

Success amplification:

AG_succ = pA / p0, for p0 > 0.

Because pA <= 1:

AG_succ <= 1 / p0.

This is the theoretical ceiling for success-ratio amplification. It is not a universal bound on utility.

If p0 = 0, amplification is undefined; report absolute uplift.

## 2. Distribution shift

KL(PA || P0) is a diagnostic for redistribution of trajectory probability mass.

It is NOT itself an agency-value metric: a large KL can correspond to worse outcomes. Finite KL also requires the appropriate support/absolute-continuity condition.

Report KL beside success, cost, and safety results.

## 3. Headroom capture

For 0 < p0 < 1:

E_headroom = (pA - p0) / (1 - p0).

This is the fraction of available success headroom captured by the agent.

## 4. Cost-adjusted Agent Gain

For positive declared costs CA and C0:

UA = pA / CA
U0 = p0 / C0

AG_cost = UA / U0 = (pA / CA) / (p0 / C0).

AG_cost > 1 means more success probability per unit declared cost.

Safety, correctness, security, and data-integrity gates are non-compensable. A cheaper unsafe policy cannot win.

## 5. Four capability components

Define:

- M = memory
- X = contradiction discovery/resolution
- P = adaptive planning
- R = strategy revision/recovery

Full policy A = {M,X,P,R}.

Single-component effects for outcome Y:

ΔM = Y(A) - Y(A-M)
ΔX = Y(A) - Y(A-X)
ΔP = Y(A) - Y(A-P)
ΔR = Y(A) - Y(A-R)

Agency Decomposition Vector:

D_A = (ΔM, ΔX, ΔP, ΔR).

Report uncertainty for every component and use the same task split.

## 6. Interactions

Single ablations cannot identify interactions.

For components i and j:

Iij = Y(A) - Y(A-i) - Y(A-j) + Y(A-i-j).

Positive Iij indicates synergy; negative Iij indicates redundancy/interference.

Preferred design: 2^4 = 16 policies covering all combinations of M, X, P, R.

If resources prevent the full factorial, execute the preregistered single-ablation subset and mark interactions UNKNOWN.

## 7. Attribution

When scalar attribution is needed, use preregistered Shapley values over the four components. Shapley attribution is an attribution convention, not causal proof. Causal interpretation still requires controlled implementation and randomization.

## 8. Experimental controls

All policies receive identical:

- frozen task set and task hash
- environment snapshot
- tools and permissions
- data
- wall-clock, token, tool-call and compute budgets
- evaluator and acceptance tests

Randomize task/policy order where feasible. Blind evaluation where feasible. Record every action, retry, intervention, decision and revision.

A component attribution is INVALID if disabling one component unintentionally disables another.

## 9. Primary endpoints

Report the vector, not an uncalibrated composite:

1. pA, p0, absolute uplift, AG_succ
2. CA, C0, AG_cost
3. E_headroom
4. KL(PA || P0), when valid
5. D_A
6. pairwise interactions Iij
7. recovery and human-intervention metrics
8. non-compensable safety/correctness gates

## 10. Testable hypotheses

H1: AG_succ <= 1/p0 for 0 < p0 <= 1.
H2: 0 <= E_headroom <= 1 for 0 < p0 < 1.
H3: operational superiority requires AG_cost > 1 and all non-compensable gates passing.
H4: identifiable components explain part of full-agent uplift; residual interaction is measurable.
H5: component interactions may be materially non-zero and must be tested.

## 11. Evidence binding

Every run must bind:

- framework version and hash
- source SHA
- task-set hash
- environment snapshot
- exact policy configuration
- randomization seed
- raw trajectory/action logs
- cost ledger
- evaluator outputs
- success predicate
- metric calculations and uncertainty
- missing-data/exclusion decisions
- artifact digests
- reproduction instructions

Evidence from an earlier SHA does not validate a later SHA.

## 12. Current evidence boundary

The framework is a theoretical and experimental specification.

Controlled experiment: NOT RUN.
Policies implemented: UNKNOWN.
Frozen task set: UNKNOWN.
Empirical component contributions: UNKNOWN.
Empirical KL shift: UNKNOWN.
Empirical cost-adjusted gain: UNKNOWN.
Product performance improvement: NOT CLAIMED.

## 13. Relationship to Agent Ablation Protocol

This framework is the conceptual layer above the original Agent Ablation Protocol:

Trajectory Space -> Success Ceiling -> Cost Utility -> Component Ablation -> Interaction -> Attribution.

The research question is now:

Which mechanisms generate measurable agent capability, how much success headroom do they capture, what do they cost, and how do they interact?

## 14. Original operational arms retained

A — Direct tool execution: fixed procedure, no adaptive replanning.

B — Basic agent: short adaptive plan, but no explicit root-cause/contradiction ledger.

C — Full agent: hypotheses, evidence, information-gain tests, contradiction tracking, dependency tracking, acceptance criteria and strategy revision.

All arms must use identical tools, permissions, data, task set and budgets.

## 15. Statistical requirements

Primary endpoint: proportion of tasks passing all preregistered acceptance tests.

Report absolute uplift, relative uplift where defined, and confidence intervals.

Use paired task-level analysis where applicable. Bootstrap at task level, not attempt level. Control false discovery rate for multiple secondary comparisons or label them exploratory.

Do not infer general agent superiority from one repository or task family.

## 16. Status boundary

No experiment is claimed by this document.

- Controlled comparison: NOT RUN
- Agent uplift: UNKNOWN
- AAC: UNKNOWN
- Component contributions: UNKNOWN
- Product release impact: NONE CLAIMED
