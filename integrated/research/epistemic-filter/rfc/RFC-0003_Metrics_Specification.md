# RFC-0003: Metrics Specification

**Status:** Proposed  
**Author:** Hamid Hayati Jozani  
**Date:** 2026-07-13  
**Version:** 1.0  

---

## 1. Overview

This RFC defines all metrics that HHJ-CSG collects, computes, and exposes for monitoring, evaluation, and governance. Every metric has:

- **Formal Definition:** What it measures
- **Computation Algorithm:** How to calculate it
- **Validation Methodology:** How to verify correctness
- **Acceptance Criteria:** Target values

---

## 2. Metric Categories

```
Metrics
├── Decision Metrics
│   ├── Decision Latency
│   ├── Decision Distribution
│   └── Decision Agreement
├── Risk Metrics
│   ├── Risk Score Distribution
│   ├── False Allow Rate
│   └── False Deny Rate
├── Evidence Metrics
│   ├── Evidence Coverage
│   ├── Evidence Completeness
│   └── Evidence Quality
├── Performance Metrics
│   ├── Throughput
│   ├── Timeout Rate
│   └── Error Rate
└── Quality Metrics
    ├── Replay Consistency
    ├── Audit Completeness
    └── Policy Alignment
```

---

## 3. Decision Metrics

### 3.1 Decision Latency

**Definition:** Time from request receipt to decision output

**Computation:**
```
latency_ms = decision_timestamp - request_timestamp
```

**Aggregations:**
- p50 (median)
- p95 (95th percentile)
- p99 (99th percentile)
- mean
- max

**Validation:**
- Baseline: < 100ms (p50)
- Target: < 300ms (p95)
- Critical: > 500ms (p99)

**Ground Truth:** Measured directly from timestamps in Decision Objects

### 3.2 Decision Distribution

**Definition:** Breakdown of verdicts across all decisions

**Computation:**
```
allow_count = count(decisions where verdict == "ALLOW")
deny_count = count(decisions where verdict == "DENY")
ask_count = count(decisions where verdict == "ASK")
defer_count = count(decisions where verdict == "DEFER")

total = allow_count + deny_count + ask_count + defer_count

allow_percent = (allow_count / total) * 100
deny_percent = (deny_count / total) * 100
ask_percent = (ask_count / total) * 100
defer_percent = (defer_count / total) * 100
```

**Validation:**
- Sum of percentages = 100%
- All counts ≥ 0
- No negative percentages

**Target Distribution (Production):**
- ALLOW: 70-80%
- DENY: 5-15%
- ASK: 5-10%
- DEFER: 0-2%

### 3.3 Decision Agreement

**Definition:** % agreement between HHJ-CSG decision and human expert label

**Computation:**
```
agreement_count = count(decisions where decision == human_label)
total_labeled = count(decisions with human_label)

agreement_rate = (agreement_count / total_labeled) * 100
```

**Validation:**
- Requires human-labeled ground truth
- Minimum 50 labeled examples for statistical significance
- Cohen's Kappa ≥ 0.75 (substantial agreement)

**Acceptance Criteria:**
- Agreement rate ≥ 85%
- Cohen's Kappa ≥ 0.75

---

## 4. Risk Metrics

### 4.1 Risk Score Distribution

**Definition:** Distribution of risk scores across all decisions

**Computation:**
```
risk_scores = [d.metrics.risk_score for d in all_decisions]

mean_risk = mean(risk_scores)
median_risk = median(risk_scores)
std_risk = std_dev(risk_scores)
min_risk = min(risk_scores)
max_risk = max(risk_scores)

# Percentiles
p25 = percentile(risk_scores, 25)
p50 = percentile(risk_scores, 50)
p75 = percentile(risk_scores, 75)
p95 = percentile(risk_scores, 95)
```

**Validation:**
- All scores in [0, 1]
- mean_risk < 0.5 (most decisions are low risk)
- std_risk > 0 (variation exists)

**Target Distribution:**
- p50 < 0.3 (median low risk)
- p95 < 0.7 (95% below moderate risk)

### 4.2 False Allow Rate

**Definition:** % of ALLOW decisions later flagged as risky or violated

**Computation:**
```
allowed_decisions = count(decisions where verdict == "ALLOW")

# Track these decisions for 24 hours
risky_outcomes = count(allowed_decisions where post_execution_risk > threshold)
violations = count(allowed_decisions where policy_violated)

false_allows = risky_outcomes + violations

false_allow_rate = (false_allows / allowed_decisions) * 100
```

**Validation:**
- Requires post-execution monitoring
- Minimum 100 ALLOW decisions for statistical significance
- False allow rate ≤ 5%

**Acceptance Criteria:**
- False allow rate ≤ 5%
- Zero critical false allows

### 4.3 False Deny Rate

**Definition:** % of DENY decisions that were actually safe

**Computation:**
```
denied_decisions = count(decisions where verdict == "DENY")

# Simulate or test these decisions in safe environment
safe_outcomes = count(denied_decisions where simulation_succeeds)

false_denies = safe_outcomes

false_deny_rate = (false_denies / denied_decisions) * 100
```

**Validation:**
- Requires simulation or safe replay
- Minimum 50 DENY decisions for significance
- False deny rate ≤ 10%

**Acceptance Criteria:**
- False deny rate ≤ 10%
- No legitimate operations blocked

---

## 5. Evidence Metrics

### 5.1 Evidence Coverage

**Definition:** % of required evidence successfully collected and validated

**Computation:**
```
required_evidence_types = [
    "identity",
    "permissions",
    "environment",
    "resource",
    "policy"
]

collected = 0
for evidence_type in required_evidence_types:
    if decision.evidence[evidence_type].present:
        collected += 1

coverage = (collected / len(required_evidence_types)) * 100
```

**Validation:**
- Coverage in [0, 100]
- All required types checked
- Missing evidence flagged

**Target:**
- Mean coverage ≥ 85%
- p95 coverage ≥ 75%

### 5.2 Evidence Completeness

**Definition:** Depth of evidence for each decision

**Computation:**
```
# For each decision, count evidence fields populated
evidence_fields = {
    "identity_verified": bool,
    "identity_confidence": float,
    "permissions_valid": bool,
    "permissions_list": array,
    "environment_healthy": bool,
    "environment_status": string,
    "resource_exists": bool,
    "resource_accessible": bool,
    "policy_applicable": bool,
    "policy_violations": array
}

populated = count(fields where value is not null)
total_fields = len(evidence_fields)

completeness = (populated / total_fields) * 100
```

**Validation:**
- Completeness in [0, 100]
- All fields checked
- Null values documented

**Target:**
- Mean completeness ≥ 80%

### 5.3 Evidence Quality

**Definition:** Reliability of evidence sources

**Computation:**
```
# Each evidence source has a quality score
source_quality = {
    "identity_service": 0.99,
    "permission_cache": 0.95,
    "environment_api": 0.92,
    "resource_db": 0.98,
    "policy_engine": 0.97
}

# Weighted average
quality_score = weighted_mean(
    [source_quality[s] for s in evidence_sources],
    weights=[evidence_weight[s] for s in evidence_sources]
)
```

**Validation:**
- Quality score in [0, 1]
- All sources have assigned quality
- Weights sum to 1

**Target:**
- Mean quality ≥ 0.95

---

## 6. Performance Metrics

### 6.1 Throughput

**Definition:** Decisions processed per second

**Computation:**
```
time_window = 60  # seconds
decisions_in_window = count(decisions in last 60 seconds)

throughput = decisions_in_window / time_window  # decisions/sec
```

**Validation:**
- Throughput ≥ 0
- Measured over consistent time windows
- Trend analysis for degradation

**Target:**
- Minimum: 100 decisions/sec
- Target: 1000 decisions/sec
- Peak: 5000 decisions/sec

### 6.2 Timeout Rate

**Definition:** % of requests timing out

**Computation:**
```
total_requests = count(all_requests)
timed_out = count(requests where processing_time > timeout_threshold)

timeout_rate = (timed_out / total_requests) * 100
```

**Validation:**
- Timeout rate in [0, 100]
- Threshold clearly defined (e.g., 500ms)
- Trend monitored

**Target:**
- Timeout rate ≤ 1%

### 6.3 Error Rate

**Definition:** % of requests resulting in errors

**Computation:**
```
total_requests = count(all_requests)
errors = count(requests where status == "error")

error_rate = (errors / total_requests) * 100

# Breakdown by error type
validation_errors = count(errors where type == "validation")
timeout_errors = count(errors where type == "timeout")
system_errors = count(errors where type == "system")
```

**Validation:**
- Error rate in [0, 100]
- All error types categorized
- Root causes identified

**Target:**
- Error rate ≤ 0.1%
- No cascading failures

---

## 7. Quality Metrics

### 7.1 Replay Consistency

**Definition:** % of decisions that produce identical results when replayed

**Computation:**
```
replayable_decisions = count(decisions where is_replayable == true)

replayed_successfully = 0
for decision in replayable_decisions:
    replayed_result = replay(decision)
    if replayed_result.verdict == decision.verdict:
        replayed_successfully += 1

consistency_rate = (replayed_successfully / replayable_decisions) * 100
```

**Validation:**
- Requires replay infrastructure
- Minimum 100 replayed decisions
- Consistency rate ≥ 95%

**Acceptance Criteria:**
- Replay consistency ≥ 95%
- All metrics match within tolerance

### 7.2 Audit Completeness

**Definition:** % of decisions with complete audit trail

**Computation:**
```
total_decisions = count(all_decisions)

complete_audits = 0
for decision in all_decisions:
    required_fields = [
        "decision_id",
        "decision_timestamp",
        "input",
        "evidence",
        "metrics",
        "decision",
        "lineage",
        "audit"
    ]
    
    if all(field in decision for field in required_fields):
        complete_audits += 1

completeness = (complete_audits / total_decisions) * 100
```

**Validation:**
- Completeness in [0, 100]
- All required fields present
- No missing signatures

**Target:**
- Audit completeness = 100%

### 7.3 Policy Alignment

**Definition:** % of decisions aligned with applied policies

**Computation:**
```
total_decisions = count(all_decisions)

aligned = 0
for decision in all_decisions:
    policy = load_policy(decision.lineage.policy_version)
    
    if decision_respects_policy(decision, policy):
        aligned += 1

alignment_rate = (aligned / total_decisions) * 100
```

**Validation:**
- Alignment in [0, 100]
- Policy rules clearly defined
- Violations documented

**Target:**
- Policy alignment = 100%

---

## 8. Metric Collection

### 8.1 Collection Points

```
Request → [Collect: timestamp, tool_name, context]
  ↓
Analysis → [Collect: evidence metrics, risk scores]
  ↓
Decision → [Collect: verdict, confidence, latency]
  ↓
Execution → [Collect: outcome, post-execution risk]
  ↓
Audit → [Collect: signature, lineage, completeness]
```

### 8.2 Storage Format

**JSONL (JSON Lines):**
```json
{"timestamp": "2026-07-13T12:34:56Z", "metric": "decision_latency_ms", "value": 145, "percentile": "p50"}
{"timestamp": "2026-07-13T12:34:56Z", "metric": "decision_distribution", "verdict": "ALLOW", "count": 1234}
{"timestamp": "2026-07-13T12:34:56Z", "metric": "false_allow_rate", "value": 0.03}
```

### 8.3 Aggregation

**Time Windows:**
- 1 minute (real-time)
- 5 minutes (short-term)
- 1 hour (operational)
- 1 day (daily report)
- 1 week (weekly report)

---

## 9. Alerting Rules

| Metric | Threshold | Action |
|--------|-----------|--------|
| Decision Latency (p95) | > 500ms | Warning |
| Decision Latency (p99) | > 1000ms | Critical |
| Error Rate | > 1% | Warning |
| Error Rate | > 5% | Critical |
| Timeout Rate | > 2% | Warning |
| False Allow Rate | > 5% | Critical |
| False Deny Rate | > 10% | Warning |
| Replay Consistency | < 95% | Critical |
| Audit Completeness | < 100% | Warning |
| Policy Alignment | < 100% | Critical |

---

## 10. Implementation Checklist

- [ ] All metrics defined with formulas
- [ ] Collection points identified
- [ ] Storage backend configured
- [ ] Aggregation logic implemented
- [ ] Alerting rules configured
- [ ] Dashboards created
- [ ] Target values documented
- [ ] Validation tests written

---

**End of RFC-0003**
