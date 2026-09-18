# RFC-0002: Decision Object Schema

**Status:** Proposed  
**Author:** Hamid Hayati Jozani  
**Date:** 2026-07-13  
**Version:** 1.0  

---

## 1. Overview

This RFC defines the complete schema for Decision Objects—the immutable records that capture every execution governance decision. Each Decision Object contains:

- **Input:** The original permission request
- **Evidence:** Validated runtime observations
- **Metrics:** Computed risk/confidence scores
- **Decision:** The verdict (ALLOW/DENY/ASK/DEFER)
- **Rationale:** Human-readable explanation
- **Lineage:** Immutable trace for replay
- **Audit:** Timestamps and signatures

---

## 2. Decision Object Schema (Complete)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "decision_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this decision"
    },
    "decision_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When this decision was made"
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Schema version (semver)"
    },
    "input": {
      "type": "object",
      "description": "Original permission request",
      "properties": {
        "event_id": { "type": "string", "format": "uuid" },
        "workspace_id": { "type": "string", "format": "uuid" },
        "agent_id": { "type": "string", "format": "uuid" },
        "tool_name": { "type": "string" },
        "tool_params_hash": { "type": "string" },
        "context": {
          "type": "object",
          "properties": {
            "user_role": { "type": "string" },
            "environment": { "type": "string" },
            "session_id": { "type": "string" }
          }
        }
      },
      "required": ["event_id", "workspace_id", "tool_name"]
    },
    "evidence": {
      "type": "object",
      "description": "Validated runtime observations",
      "properties": {
        "identity_verified": { "type": "boolean" },
        "identity_confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "permissions_valid": { "type": "boolean" },
        "permissions_list": { "type": "array", "items": { "type": "string" } },
        "environment_healthy": { "type": "boolean" },
        "environment_status": { "type": "string" },
        "resource_exists": { "type": "boolean" },
        "resource_accessible": { "type": "boolean" },
        "policy_applicable": { "type": "boolean" },
        "policy_violations": { "type": "array", "items": { "type": "string" } },
        "recent_similar_actions": { "type": "integer" },
        "recent_failures": { "type": "integer" },
        "evidence_coverage": { "type": "number", "minimum": 0, "maximum": 1 }
      },
      "required": ["identity_verified", "permissions_valid", "evidence_coverage"]
    },
    "metrics": {
      "type": "object",
      "description": "Computed risk and confidence scores",
      "properties": {
        "risk_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Overall risk assessment"
        },
        "confidence_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Confidence in this decision"
        },
        "evidence_completeness": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "policy_alignment": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "anomaly_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Deviation from baseline"
        },
        "impact_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Potential impact if executed"
        },
        "reversibility_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Can this action be undone?"
        }
      },
      "required": ["risk_score", "confidence_score", "evidence_completeness"]
    },
    "decision": {
      "type": "object",
      "description": "The governance verdict",
      "properties": {
        "verdict": {
          "type": "string",
          "enum": ["ALLOW", "DENY", "ASK", "DEFER"],
          "description": "Final decision"
        },
        "rationale": {
          "type": "string",
          "description": "Human-readable explanation"
        },
        "reasoning_chain": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "step": { "type": "integer" },
              "condition": { "type": "string" },
              "result": { "type": "boolean" },
              "weight": { "type": "number" }
            }
          },
          "description": "Step-by-step decision logic"
        },
        "alternative_decisions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "verdict": { "type": "string" },
              "confidence": { "type": "number" },
              "probability": { "type": "number" }
            }
          }
        },
        "enforcement_action": {
          "type": "string",
          "enum": ["execute", "block", "escalate", "sandbox", "retry"],
          "description": "What AgentRQ should do"
        }
      },
      "required": ["verdict", "rationale", "enforcement_action"]
    },
    "lineage": {
      "type": "object",
      "description": "Immutable trace for replay",
      "properties": {
        "lineage_token": {
          "type": "string",
          "description": "JWS signed token"
        },
        "event_chain": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "event_id": { "type": "string" },
              "event_type": { "type": "string" },
              "timestamp": { "type": "string" },
              "event_hash": { "type": "string" }
            }
          },
          "description": "All events that contributed to this decision"
        },
        "policy_version": { "type": "string" },
        "model_version": { "type": "string" },
        "evidence_snapshot": {
          "type": "object",
          "description": "Snapshot of all evidence at decision time"
        },
        "evidence_hash": {
          "type": "string",
          "description": "SHA256 hash of evidence for integrity"
        },
        "policy_hash": {
          "type": "string",
          "description": "SHA256 hash of policy rules applied"
        }
      },
      "required": ["lineage_token", "event_chain", "evidence_hash", "policy_hash"]
    },
    "audit": {
      "type": "object",
      "description": "Audit trail and signatures",
      "properties": {
        "created_by": { "type": "string" },
        "created_at": { "type": "string", "format": "date-time" },
        "signed_by": { "type": "string" },
        "signature": { "type": "string" },
        "signature_algorithm": { "type": "string" },
        "public_key_id": { "type": "string" },
        "verified_at": { "type": "string", "format": "date-time" },
        "verification_status": {
          "type": "string",
          "enum": ["valid", "invalid", "expired", "unknown"]
        }
      },
      "required": ["created_by", "created_at", "signature"]
    },
    "recovery": {
      "type": "object",
      "description": "Recommended recovery actions",
      "properties": {
        "recommendation": { "type": "string" },
        "priority": {
          "type": "string",
          "enum": ["low", "medium", "high", "critical"]
        },
        "actions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "action": { "type": "string" },
              "description": { "type": "string" },
              "estimated_effort": { "type": "string" }
            }
          }
        }
      }
    },
    "replay_metadata": {
      "type": "object",
      "description": "Data needed for deterministic replay",
      "properties": {
        "is_replayable": { "type": "boolean" },
        "replay_key": { "type": "string" },
        "replay_instructions": { "type": "string" },
        "expected_result": { "type": "string" },
        "replay_tested": { "type": "boolean" },
        "replay_verified_at": { "type": "string", "format": "date-time" }
      }
    }
  },
  "required": [
    "decision_id",
    "decision_timestamp",
    "version",
    "input",
    "evidence",
    "metrics",
    "decision",
    "lineage",
    "audit"
  ]
}
```

---

## 3. Field Descriptions

### 3.1 Input Section

| Field | Type | Description |
|-------|------|-------------|
| event_id | UUID | Original permission request ID |
| workspace_id | UUID | Workspace context |
| agent_id | UUID | Requesting agent |
| tool_name | String | Tool/action being requested |
| tool_params_hash | String | SHA256 hash of parameters (not plaintext) |
| context.user_role | String | admin/user/service |
| context.environment | String | production/staging/development |
| context.session_id | String | Session identifier |

### 3.2 Evidence Section

| Field | Type | Description |
|-------|------|-------------|
| identity_verified | Boolean | Was identity successfully verified? |
| identity_confidence | Float [0-1] | Confidence in identity verification |
| permissions_valid | Boolean | Does identity have required permissions? |
| permissions_list | Array | List of verified permissions |
| environment_healthy | Boolean | Is environment in healthy state? |
| environment_status | String | healthy/degraded/critical |
| resource_exists | Boolean | Does target resource exist? |
| resource_accessible | Boolean | Can agent access this resource? |
| policy_applicable | Boolean | Are policies applicable? |
| policy_violations | Array | List of policy violations detected |
| recent_similar_actions | Integer | Count of similar actions in last hour |
| recent_failures | Integer | Count of failures in last hour |
| evidence_coverage | Float [0-1] | % of context successfully validated |

### 3.3 Metrics Section

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| risk_score | Float | 0-1 | Overall risk (0=safe, 1=critical) |
| confidence_score | Float | 0-1 | Decision confidence |
| evidence_completeness | Float | 0-1 | % of required evidence present |
| policy_alignment | Float | 0-1 | Alignment with policies |
| anomaly_score | Float | 0-1 | Deviation from baseline |
| impact_score | Float | 0-1 | Potential impact if executed |
| reversibility_score | Float | 0-1 | Can action be undone? |

### 3.4 Decision Section

| Field | Type | Description |
|-------|------|-------------|
| verdict | Enum | ALLOW/DENY/ASK/DEFER |
| rationale | String | Why this decision was made |
| reasoning_chain | Array | Step-by-step logic |
| alternative_decisions | Array | Other possible verdicts |
| enforcement_action | String | execute/block/escalate/sandbox/retry |

### 3.5 Lineage Section

| Field | Type | Description |
|-------|------|-------------|
| lineage_token | String | JWS signed token (immutable proof) |
| event_chain | Array | All events contributing to decision |
| policy_version | String | Policy version applied |
| model_version | String | Model/algorithm version |
| evidence_snapshot | Object | Complete evidence state |
| evidence_hash | String | SHA256(evidence) for integrity |
| policy_hash | String | SHA256(policy) for integrity |

### 3.6 Audit Section

| Field | Type | Description |
|-------|------|-------------|
| created_by | String | System/user that created this |
| created_at | DateTime | Creation timestamp |
| signed_by | String | Who signed this decision |
| signature | String | Cryptographic signature |
| signature_algorithm | String | RS256/ES256/HS256 |
| public_key_id | String | ID of public key for verification |
| verified_at | DateTime | When signature was verified |
| verification_status | String | valid/invalid/expired/unknown |

---

## 4. Decision Logic Examples

### Example 1: ALLOW Decision

```json
{
  "decision_id": "dec-001",
  "decision_timestamp": "2026-07-13T12:34:56Z",
  "input": {
    "tool_name": "read_logs",
    "context": { "user_role": "admin" }
  },
  "evidence": {
    "identity_verified": true,
    "permissions_valid": true,
    "environment_healthy": true,
    "evidence_coverage": 0.95
  },
  "metrics": {
    "risk_score": 0.15,
    "confidence_score": 0.92,
    "evidence_completeness": 0.95
  },
  "decision": {
    "verdict": "ALLOW",
    "rationale": "Admin identity verified, permissions valid, environment healthy, low risk",
    "enforcement_action": "execute"
  }
}
```

### Example 2: DENY Decision

```json
{
  "decision_id": "dec-002",
  "decision_timestamp": "2026-07-13T12:35:00Z",
  "input": {
    "tool_name": "delete_database",
    "context": { "user_role": "user", "environment": "production" }
  },
  "evidence": {
    "identity_verified": true,
    "permissions_valid": false,
    "policy_violations": ["no_delete_in_production"]
  },
  "metrics": {
    "risk_score": 0.95,
    "confidence_score": 0.98,
    "evidence_completeness": 0.88
  },
  "decision": {
    "verdict": "DENY",
    "rationale": "User lacks delete permissions in production; policy violation detected",
    "enforcement_action": "block"
  }
}
```

### Example 3: ASK Decision

```json
{
  "decision_id": "dec-003",
  "decision_timestamp": "2026-07-13T12:36:00Z",
  "input": {
    "tool_name": "restart_service",
    "context": { "user_role": "developer" }
  },
  "evidence": {
    "identity_verified": true,
    "permissions_valid": true,
    "environment_healthy": true,
    "recent_similar_actions": 0,
    "anomaly_score": 0.68
  },
  "metrics": {
    "risk_score": 0.65,
    "confidence_score": 0.55,
    "anomaly_score": 0.68
  },
  "decision": {
    "verdict": "ASK",
    "rationale": "Unusual pattern detected; developer has permissions but anomaly score elevated",
    "enforcement_action": "escalate"
  }
}
```

---

## 5. Replay Capability

Every Decision Object MUST be replayable:

```python
# Pseudo-code for replay
def replay_decision(decision_object):
    # 1. Restore evidence snapshot
    evidence = decision_object.lineage.evidence_snapshot
    
    # 2. Load policy version
    policy = load_policy(decision_object.lineage.policy_version)
    
    # 3. Apply decision logic
    new_decision = apply_decision_logic(evidence, policy)
    
    # 4. Verify result matches original
    assert new_decision.verdict == decision_object.decision.verdict
    assert new_decision.metrics == decision_object.metrics
    
    return True  # Replay successful
```

---

## 6. Validation Rules

- [ ] decision_id is unique UUID
- [ ] All timestamps are UTC ISO8601
- [ ] All scores are between 0 and 1
- [ ] Verdict is one of: ALLOW/DENY/ASK/DEFER
- [ ] Signature is cryptographically valid
- [ ] Evidence hash matches evidence snapshot
- [ ] Policy hash matches applied policy
- [ ] Lineage token is valid JWS
- [ ] All required fields present
- [ ] No plaintext sensitive data

---

## 7. Implementation Checklist

- [ ] JSON Schema validation implemented
- [ ] All decision types tested
- [ ] Replay capability verified
- [ ] Signature generation/verification working
- [ ] Hash integrity verified
- [ ] Lineage tokens created correctly
- [ ] Audit trail complete
- [ ] Recovery recommendations generated

---

**End of RFC-0002**
